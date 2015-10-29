import os
import sys
import math
import pygame
import random
pygame.init()
import pygame.locals as pgl
#########################
# GLOBAL CONSTANTS

MESSAGE = 'message'
WALKING = 'walking'
PETTING = 'petting'
GAME_OVER = 'game over'

OFFSCREEN = (-2000, -2000)

DEFAULT_FONT = 'arial'

UP = pgl.K_UP
DOWN = pgl.K_DOWN
RIGHT = pgl.K_RIGHT
LEFT = pgl.K_LEFT

HELP_KEY = pgl.K_h

MOVE_SPEED = 1
DIRECTIONS = {UP: (0, -MOVE_SPEED),
              RIGHT: (MOVE_SPEED, 0),
              LEFT: (-MOVE_SPEED, 0),
              DOWN: (0, MOVE_SPEED)}

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)
ORANGE = (255, 140,   0)
YELLOW = (255, 255,   0)

FPS = 30  # frames per second setting
fps_clock = pygame.time.Clock()

FRAME_WIDTH, FRAME_HEIGHT = 800, 600
CENTER_FRAME_X = FRAME_WIDTH / 2
CENTER_FRAME_Y = FRAME_HEIGHT / 2
CENTER_FRAME_POS = (CENTER_FRAME_X, CENTER_FRAME_Y)
FRAME = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))

TILES_PATH = './tiles'
SPRITES_PATH = './sprites'
TIGER_PICS_PATH = './tiger_pics'
TIGER_SPRITES_FILENAME = 'tiger_sprites.png'
TILE_SIZE = 200
DEGREES = [0, 90, 180, 270]

TIGER_W, TIGER_H = 19, 51

MIN_PET_SPEED, MAX_PET_SPEED = 5, 10
TOO_FAST_MOD, TOO_SLOW_MOD = 1.4, 1.4
PETTING_TIME = FPS * 20
PET_BAR_MOD = 60
PET_BAR_CENTER = (CENTER_FRAME_X, 20)
PET_TEXT_CENTER = (CENTER_FRAME_X, 60)
PET_BAR_HEIGHT = 50
PET_TEXT_HEIGHT = 30
NUM_PETS = 100

YAWN = 'YAAAWWWNNN...'
PURR = 'PUUURRRRRRRRR'
GRRR = 'GRRRRRRRRRRR!'

YAWN_GRRR_MAX = 500

MESSAGE_FONT_HEIGHT = 20
MESSAGE_SCREEN_TIME = FPS * 1
MESSAGE_LINE_SPACING = 20

TOPLEFT = 'topleft'
CENTER = 'center'


START_MENU_MESSAGES = [
    'Welcome to',
    'WILD TIGER PETTER',
]
HELP_MESSAGES = [
    'Click, hold and drag the mouse button to pet.',
    'Pet the tiger where it wants to be petted.',
    "Don't pet too fast, or the tiger will get angry.",
    "Don't pet too slow, or the tiger will get bored.",
    'Pet the tiger until it is happy!'
]
NEW_GAME_MESSAGES = [
    'How about a nice walk in the jungle...',
    'But could there be any wild tigers about?'
]
BEFORE_PET_MESSAGES = [
    "It's a ferociously cute tiger!",
    'Pet it before it gets away!'
]
PURR_MESSAGES = [
    'Great job petting that tiger!',
    'Now back to that nice walk...'
]
GRRR_MESSAGES = [
    'That tiger got angry and stalked off.',
    'Maybe there are more around...'
]
YAWN_MESSAGES = [
    'That tiger became bored and wandered away.',
    'Maybe there are more around...'
]
GAME_OVER_MESSAGES = [
    'Game Over.',
    'Congratulations!'
]
CONTINUE_MESSAGES = [
    'Press "H" at any time for help.',
    'Click or press any other button to continue.'
]

PET_FEEDBACK = {
    PURR: PURR_MESSAGES,
    YAWN: YAWN_MESSAGES,
    GRRR: GRRR_MESSAGES
}
#############################


################################################
# Image loading tools


def get_file_paths(root):
    return [os.path.join(p, f) for p, d, files in os.walk(root) for f in files]


def load_image(filename):
    return pygame.image.load(filename).convert()


def load_rand_tile():
    filename = random.choice(get_file_paths(TILES_PATH))
    tile = load_image(filename)
    return pygame.transform.rotate(tile, random.choice(DEGREES))


# will need to convert this into a general sprite getting function
def get_tiger_sprite():
    filename = os.path.join(SPRITES_PATH, TIGER_SPRITES_FILENAME)
    image = load_image(filename)
    image.set_colorkey(WHITE)
    subsurface = image.subsurface((0, 0, TIGER_W, TIGER_H))
    return pygame.transform.rotate(subsurface, random.choice(DEGREES))


##########################################
# other utils


def init_matrix_pos(matrix_size):
    return tuple([xy - (TILE_SIZE * (matrix_size / 2)) - TILE_SIZE / 2
                  for xy in CENTER_FRAME_POS])


def rel_tile_pos(matrix_pos, tile_pos_in_matrix, direction=(0, 0)):
    return tuple(map(
        lambda xy1, xy2, xy3: xy1 + (TILE_SIZE * xy2) + (TILE_SIZE * xy3),
        matrix_pos, tile_pos_in_matrix, direction))


def distance(pos1, pos2):
    try:
        x_delt, y_delt = map(lambda xy1, xy2: abs(xy1 - xy2), pos1, pos2)
        return math.hypot(x_delt, y_delt)
    except:
        return 0


def distances(pos_list):
    if len(pos_list) < 2:
        return []
    return [distance(pos, pos_list[i - 1]) for i, pos in enumerate(pos_list[1:])]


def total_distance(pos_list, total=0):
    if len(pos_list) < 2:
        return total
    else:
        total += distance(pos_list[0], pos_list[1])
        return total_distance(pos_list[1:], total)


def avg_distance(pos_list):
    return total_distance(pos_list) / len(pos_list)


def trailing_index(vector):
    if vector < 0:
        return -1
    elif vector > 0:
        return 0


def leading_index(vector, iterable):
    if vector < 0:
        return 0
    elif vector > 0:
        return len(iterable) - 1


def mirror_direction(direction):
    return tuple(-xy for xy in direction)

#######################################################


class ImgObj(pygame.sprite.Sprite):
    def __init__(self, pos=OFFSCREEN, image=None,
                 width=0, height=0, alignment=TOPLEFT):
        pygame.sprite.Sprite.__init__(self)
        self.alignment = alignment
        if image:
            self.image = image
            self.rect = self.image.get_rect()
        else:
            self.image = pygame.Surface((width, height))
            self.rect = pygame.Rect(pos, (width, height))
        self.pos = pos

    def __str__(self):
        return '{} at {}; w: {}, h: {}'.format(self.__class__.__name__,
                                               self.pos,
                                               self.width,
                                               self.height)

    @property
    def pos(self):
        return self._x, self._y

    @pos.setter
    def pos(self, pos):
        if not isinstance(pos, tuple) and len(pos) == 2:
            raise TypeError('{} pos must be tuple len 2.'.format(repr(self)))
        self._x, self._y = pos
        setattr(self.rect, self.alignment, pos)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        self._rect = rect
        self._width = rect.width
        self._height = rect.height
        self._center = rect.center
        self.pos = getattr(rect, self.alignment)

    @property
    def width(self):
        return self._rect.width

    @width.setter
    def width(self, w):
        self._width = w
        self._rect.width = w

    @property
    def height(self):
        return self._rect.height

    @property
    def center(self):
        return self._rect.center

    @property
    def topleft(self):
        return self._rect.topleft

    def move(self, direction):
        if not isinstance(direction, tuple) and len(direction) == 2:
            raise TypeError('{} direction must be tuple len 2.'
                            ''.format(repr(self)))
        x, y = direction
        self._x += x
        self._y += y
        self._rect.move_ip(x, y)

    def random_pos(self):
        return (self.x + random.randrange(self.width),
                self.y + random.randrange(self.height))

    def collidelistall(self, a_list):
        return self.rect.collidelistall(a_list)

    def collide_pos(self, pos):
        return self.rect.collidepoint(pos)

    def collide_rect(self, rect):
        return self.rect.colliderect(rect)

    def fill(self, color):
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color, rect=self.rect)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Text(ImgObj):
    def __init__(self, string, font_name, color, height, *args, **kwargs):
        self.string = string
        self.font_name = font_name
        self.color = color
        self.font = pygame.font.SysFont(font_name, height)
        image = self.font.render(string, True, color)
        super(Text, self).__init__(*args, image=image, **kwargs)

    def __str__(self):
        return 'Text at {} saying: {}'.format(self.pos, self.string)

    def update(self, pos=OFFSCREEN, string=None, color=None):
        if color:
            self.color = color
        if string:
            self.string = string
        self.image = self.font.render(self.string, True, self.color)
        self.rect = self.image.get_rect()
        self.pos = pos


class MessageScreen(object):
    '''
    Class for managing and displaying message screens in between gameplay.
    Automatically formats all text to be horizontally centered and
    vertically evenly spaced.
    '''
    def __init__(self, messages, next_mode_func, alignment=CENTER):
        self.next_mode_func = next_mode_func

        if alignment == TOPLEFT:
            x = 100
        elif alignment == CENTER:
            x = CENTER_FRAME_X

        messages.extend(CONTINUE_MESSAGES)
        self.messages = [
            Text(m, DEFAULT_FONT, ORANGE, MESSAGE_FONT_HEIGHT,
                 pos=(x, (i + 1) * (FRAME_HEIGHT / (len(messages) + 1))),
                 alignment=alignment)
            for i, m in enumerate(messages)]

    def __str__(self):
        return 'MessageScreen:\n{}'.format(
            '\n'.join([str(m) for m in self.messages]))

    def update(self, mousedown):
        if mousedown:
            self.next_mode_func()

    def draw(self, surface):
        for m in self.messages:
            m.draw(surface)


class Player(ImgObj):
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)

    def draw(self, surface):
        self.image = pygame.draw.circle(surface, RED, self.pos, 10)


class Tile(ImgObj):
    def __init__(self, matrix_pos, tile_pos_in_matrix, *args, **kwargs):
        pos = rel_tile_pos(matrix_pos, tile_pos_in_matrix)
        super(Tile, self).__init__(*args,
                                   pos=pos,
                                   image=load_rand_tile(),
                                   width=TILE_SIZE,
                                   height=TILE_SIZE,
                                   **kwargs)
        self.tiger = None

    def __str__(self):
        return 'Tile at {}'.format(self.pos)

    def place_tiger(self, tiger):
        # randomly rotate tiger
        self.tiger = tiger
        self.tiger.pos = self.random_pos()

    def reposition(self, matrix_pos, tile_pos_in_matrix, direction=(0, 0)):
        # get new random and rotated image
        self.pos = rel_tile_pos(matrix_pos, tile_pos_in_matrix, direction)
        if self.tiger:
            self.place_tiger(self.tiger)


# make TileMatrix into an iterable class
class TileMatrix(ImgObj):
    def __init__(self, size, tigers, *args, **kwargs):
        super(TileMatrix, self).__init__(*args,
                                         width=TILE_SIZE * size,
                                         height=TILE_SIZE * size,
                                         **kwargs)
        assert size % 2 != 0 and size >= 3, ('Tile Matrix size must be '
                                             'an odd number at least 5')
        self.size = int(size)
        self.index_range = range(size)
        self.center_index = size / 2
        self.tiles = [[Tile(self.pos, (matrix_x, matrix_y))
                       for matrix_y in self.index_range]
                      for matrix_x in self.index_range]
        self.update_pos()
        tiles = list(self.get_matrix())
        random.shuffle(tiles)

        for tile in tiles:
            if tile != self.center_tile:
                try:
                    if not tile.tiger:
                        tile.place_tiger(tigers.pop())
                except IndexError:
                    pass

    def __str__(self):
        tiles = '\n'.join([' | '.join(
            ['({}, {}): {}'.format(x, y, str(self.tiles[x][y]))
             for x in self.index_range])
            for y in self.index_range])
        return 'Tile Matrix with upperleft at {}\n{}'.format(self.pos, tiles)

    def reposition(self, direction):
        '''
        Repositions all Tiles in the matrix when the center tile moves off of
        the center point where the player is.
        Overwrites tiles on the trailing edge. Creates new tiles on the leading
        edge.
        This creates the illusion of a constant unending map.
        '''
        # dx and dy track the individual x and y movement vectors
        dx, dy = direction
        # remember: direction of map movement is reversed compared to
        # arrow direction (player direction)

        if dx:
            tiles_to_move = self.tiles.pop(trailing_index(dx))
            random.shuffle(tiles_to_move)
            x = leading_index(dx, tiles_to_move)
            self.tiles.insert(x, tiles_to_move)
            for y, tile in enumerate(tiles_to_move):
                tile.reposition(self.pos, (x, y), direction)
        elif dy:
            tiles_to_move = [x.pop(trailing_index(dy)) for x in self.tiles]
            random.shuffle(tiles_to_move)
            for x, tile in enumerate(tiles_to_move):
                y = leading_index(dy, tiles_to_move)
                self.tiles[x].insert(y, tile)
                tile.reposition(self.pos, (x, y), direction)
        print(self)
        self.update_pos()

    def get_matrix(self):
        for row in self.tiles:
            for tile in row:
                yield tile

    def update_pos(self, direction=(0, 0)):
        # use direction
        self.center_tile = self.tiles[self.center_index][self.center_index]
        self.pos = self.tiles[0][0].pos

    def off_center(self):
        return not self.center_tile.collide_pos(CENTER_FRAME_POS)

    def move(self, direction):
        super(TileMatrix, self).move(mirror_direction(direction))
        for tile in self.get_matrix():
            tile.move(mirror_direction(direction))
        if self.off_center():
            print('Tile off center; redrawing.')
            self.reposition(direction)

    def draw(self, surface):
        for tile in self.get_matrix():
            tile.draw(surface)


class Tiger(ImgObj):
    def __init__(self, picture, *args, **kwargs):
        super(Tiger, self).__init__(*args,
                                    image=get_tiger_sprite(),
                                    width=TIGER_W,
                                    height=TIGER_H,
                                    **kwargs)
        self.picture = ImgObj(image=picture, pos=CENTER_FRAME_POS,
                              alignment=CENTER)

        self.petted = False
        self.desired_pet_speed = random.randrange(MIN_PET_SPEED, MAX_PET_SPEED)
        self.too_fast = self.desired_pet_speed * TOO_FAST_MOD
        self.too_slow = self.desired_pet_speed / TOO_SLOW_MOD

    def draw_picture(self, surface):
        self.picture.draw(surface)


class TigerManager(object):
    def __init__(self):
        tiger_pics = [load_image(pic) for pic in get_file_paths(TIGER_PICS_PATH)]
        self.tigers = [Tiger(pic) for pic in tiger_pics]
        self.pet_text = Text('', DEFAULT_FONT, ORANGE, PET_TEXT_HEIGHT,
                             pos=PET_TEXT_CENTER, alignment=CENTER)
        self.pet_bar = ImgObj(height=PET_BAR_HEIGHT,
                              pos=PET_BAR_CENTER, alignment=CENTER)
        self.reset()

    def __str__(self):
        return 'Tigers:\n{}'.format('\n'.join(self.tigers))

    def reset(self):
        self.tiger_to_pet = None
        self.last_pet_pos = None
        self.distances = []  # give a better starting list of distances
        self.pet_score = 0
        self.yawn_score = 0
        self.grrr_score = 0
        self.petting_time = PETTING_TIME

    def pet(self, mousedown, mouse_pos):
        result = self.process_pet(self.tiger_to_pet, mousedown, mouse_pos)
        if result:
            self.tiger_to_pet.petted = True
            self.tiger_to_pet.pos = OFFSCREEN
            self.reset()
        return result

    def process_pet(self, tiger, mousedown, mouse_pos):
        self.petting_time -= 1
        if mousedown:
            dist = distance(self.last_pet_pos, mouse_pos)
            self.last_pet_pos = mouse_pos
        else:
            dist = 0
            self.last_pet_pos = None

        self.distances.insert(0, dist)
        if len(self.distances) > NUM_PETS:
            self.distances.pop()

        pet_speed = sum(self.distances) / len(self.distances)
        self.pet_bar.width = pet_speed * PET_BAR_MOD
        self.pet_bar.pos = PET_BAR_CENTER

        if pet_speed >= tiger.too_fast:
            self.grrr_score += abs(pet_speed - tiger.too_fast)
            self.pet_text.update(pos=PET_TEXT_CENTER, string=GRRR, color=RED)
            self.pet_bar.fill(RED)
        elif pet_speed <= tiger.too_slow:
            self.yawn_score += abs(pet_speed - tiger.too_slow)
            self.pet_text.update(pos=PET_TEXT_CENTER, string=YAWN,
                                 color=YELLOW)
            self.pet_bar.fill(YELLOW)
        else:
            # the score is higher closer to desired speed
            self.pet_score += 1 / abs(pet_speed - tiger.desired_pet_speed)
            self.pet_text.update(pos=PET_TEXT_CENTER, string=PURR,
                                 color=ORANGE)
            self.pet_bar.fill(ORANGE)

        # print('Time: {}; Pet speed: {:.2f} vs {:.2f} Purr: {:.2f}, '
        #       'Grrr: {:.2f}, Yawn: {:.2f}'.format(
        #           self.petting_time, pet_speed, tiger.desired_pet_speed,
        #           self.pet_score, self.grrr_score, self.yawn_score))

        # or if tiger gets too bored or too annoyed
        if self.petting_time <= 0:
            return PURR
        elif self.yawn_score >= YAWN_GRRR_MAX:
            return YAWN
        elif self.grrr_score >= YAWN_GRRR_MAX:
            return GRRR
        return None

    def tigers_to_pet(self):
        return [tiger for tiger in self.tigers if not tiger.petted]

    def collide(self, player):
        # should check if collide with player, not center pos
        for tiger in self.tigers:
            if tiger.collide_pos(CENTER_FRAME_POS):
                self.tiger_to_pet = tiger
                return True
        return False

    def move(self, direction):
        direction = mirror_direction(direction)
        for tiger in self.tigers:
            tiger.move(direction)

    def draw_petting(self, surface):
        self.tiger_to_pet.draw_picture(surface)
        self.pet_bar.draw(surface)
        self.pet_text.draw(surface)

    def draw(self, surface):
        for tiger in self.tigers_to_pet():
            tiger.draw(surface)


class GameState(object):
    '''
    Master game state, containing current player action, tile map, game
    objects on map, and any messages to display between modes.
    '''
    def __init__(self, matrix_size):
        self.mode = MESSAGE
        self.message_screen = MessageScreen(START_MENU_MESSAGES, self.start_game)
        self.tigers = TigerManager()
        self.tile_matrix = TileMatrix(matrix_size, self.tigers.tigers_to_pet(),
                                      pos=init_matrix_pos(matrix_size))
        self.player = Player(pos=CENTER_FRAME_POS)
        self.direction = None
        self.mousedown = False

    def __str__(self):
        return '''
        GameState current mode: {}
        {}
        {}
        '''.format(self.mode, self.tile_matrix, self.message_screen)

    def reset(self):
        self.direction = None
        self.mousedown = False
        self.message_screen = None

    def help_me(self):
        self.mode = MESSAGE
        # need to change this to call back to previous message screen
        # maybe use a "next mode" attribute
        self.message_screen = MessageScreen(HELP_MESSAGES,
                                            self.start_walking)

    def start_game(self):
        self.mode = MESSAGE
        self.message_screen = MessageScreen(NEW_GAME_MESSAGES,
                                            self.start_walking)

    def start_petting(self):
        print('start_petting')
        self.mode = PETTING
        self.reset()

    def start_walking(self):
        print('start_walking')
        self.mode = WALKING
        self.reset()

    def process_event(self, event):
        keyup, keydown = None, None
        if event.type == pgl.KEYUP:
            keyup = event.key or None
        elif event.type == pgl.KEYDOWN:
            keydown = event.key or None
        if event.type == pgl.QUIT or keydown == pgl.K_ESCAPE:
            self.quit()

        if event.type == pgl.MOUSEBUTTONDOWN:
            self.mousedown = True
        elif event.type == pgl.MOUSEBUTTONUP:
            self.mousedown = False

        if self.mode == WALKING:
            if keydown:
                self.direction = DIRECTIONS.get(keydown, None)
            if keyup and self.direction in DIRECTIONS.values():
                self.direction = None

    def move(self, direction):
        if self.mode == WALKING:
            self.tile_matrix.move(direction)  # reverse
            self.tigers.move(direction)  # reverse
            if self.tigers.collide(self.player):  # move to Player obj rect
                self.mode = MESSAGE
                self.message_screen = MessageScreen(BEFORE_PET_MESSAGES,
                                                    self.start_petting)

    def draw(self, surface):
        if self.mode == MESSAGE:
            self.message_screen.draw(surface)
        elif self.mode == WALKING:
            self.tile_matrix.draw(surface)
            self.tigers.draw(surface)
            self.player.draw(surface)
        elif self.mode == PETTING:
            self.tigers.draw_petting(surface)

    def update(self):
        # print(self)
        if self.mode == MESSAGE and self.message_screen:
            self.message_screen.update(self.mousedown)
        if self.mode == WALKING and self.direction:
            self.move(self.direction)
        if self.mode == PETTING:
            result = self.tigers.pet(self.mousedown, pygame.mouse.get_pos())
            print('Petting result: {}'.format(result))
            if result:
                self.mode = MESSAGE
                self.message_screen = MessageScreen(
                    PET_FEEDBACK[result],
                    self.start_walking)
        if not self.tigers.tigers_to_pet():
            self.mode = MESSAGE
            self.message_screen = MessageScreen(GAME_OVER_MESSAGES, self.game_over)

    def game_over(self):
        pass

    def quit(self):
        pygame.quit()
        sys.exit()


def main():

    # initialize

    game_state = GameState(3)
    print(str(game_state))

    while True:
        FRAME.fill(BLACK)
        events = pygame.event.get()
        if events:
            game_state.process_event(events[0])
        game_state.update()
        game_state.draw(FRAME)
        pygame.display.update()
        fps_clock.tick(FPS)

if __name__ == '__main__':
    main()
