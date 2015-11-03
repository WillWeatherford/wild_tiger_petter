import os
import sys
import math
import pygame as pg
import random
pg.init()

#########################
# GLOBAL CONSTANTS

MESSAGE = 'message'
WALKING = 'walking'
PETTING = 'petting'
GAME_OVER = 'game over'

OFFSCREEN = (-2000, -2000)

DEFAULT_FONT = 'arial'

UP = pg.K_UP
DOWN = pg.K_DOWN
RIGHT = pg.K_RIGHT
LEFT = pg.K_LEFT
W = pg.K_w
A = pg.K_a
S = pg.K_s
D = pg.K_d

H = pg.K_h
SPACE = pg.K_SPACE

MOVE_SPEED = 1
DIRECTIONS = {LEFT: (-MOVE_SPEED, 0),
              UP: (0, -MOVE_SPEED),
              RIGHT: (MOVE_SPEED, 0),
              DOWN: (0, MOVE_SPEED),
              A: (-MOVE_SPEED, 0),
              W: (0, -MOVE_SPEED),
              D: (MOVE_SPEED, 0),
              S: (0, MOVE_SPEED)}

DEGREES = (0.0, 90.0, 180.0, 270.0)

DI_DE = {DIRECTIONS[LEFT]: 0.0,
         DIRECTIONS[UP]: 270.0,
         DIRECTIONS[RIGHT]: 180.0,
         DIRECTIONS[DOWN]: 90.0}

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)
ORANGE = (255, 140,   0)
YELLOW = (255, 255,   0)

FPS = 30  # frames per second setting
fps_clock = pg.time.Clock()

PLAYER_ANIM_RATE = 6

FRAME_WIDTH, FRAME_HEIGHT = 1280, 720
SCREEN_RECT = pg.Rect(0, 0, FRAME_WIDTH, FRAME_HEIGHT)
CENTER_FRAME_X = FRAME_WIDTH / 2
CENTER_FRAME_Y = FRAME_HEIGHT / 2
CENTER_FRAME_POS = (CENTER_FRAME_X, CENTER_FRAME_Y)
FRAME = pg.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT), pg.FULLSCREEN)

MAX_PICTURE_HEIGHT = int(FRAME_HEIGHT * 0.75)

TILES_PATH = './tiles'
SPRITES_PATH = './sprites'
TIGER_PICS_PATH = './tiger_pics'
TIGER_SPRITES_FILENAME = 'tiger_sprites.png'
PLAYER_SPRITES_FILENAME = 'walker2.png'
TILE_SIZE = 200

TIGER_W, TIGER_H = 19, 51
PLAYER_H, PLAYER_W = 20, 20

MIN_PET_SPEED, MAX_PET_SPEED = 5, 10
TOO_FAST_MOD, TOO_SLOW_MOD = 1.4, 0.8
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

YAWN_MAX = 1000
GRRR_MAX = 500

ROAR_MIN = FPS * 6
ROAR_MAX = FPS * 12

MESSAGE_FONT_HEIGHT = 25
MESSAGE_SCREEN_TIME = FPS * 1
MESSAGE_LINE_SPACING = 20
ROAR_HEIGHT_FAR = 20
ROAR_HEIGHT_NEAR = 30

TOPLEFT = 'topleft'
CENTER = 'center'

MESSAGE_SCREEN_DELAY = 2

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
    'Congratulations, you petted all the tigers!',
    'Press Space to start a new game, or Esc to quit.'
]
CONTINUE_MESSAGES = [
    'Press "H" at any time for help. Press "Space" to continue.'
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
    return pg.image.load(filename).convert()


def random_rotate(surface):
    return


def load_rand_tile():
    filename = random.choice(get_file_paths(TILES_PATH))
    return load_image(filename)


# should convert this into a general sprite getting function
def load_tiger_sprite():
    filename = os.path.join(SPRITES_PATH, TIGER_SPRITES_FILENAME)
    image = load_image(filename)
    image.set_colorkey(WHITE)
    return image.subsurface((0, 0, TIGER_W, TIGER_H))


def load_tiger_pics():
    return [scale_picture(load_image(filename))
            for filename in get_file_paths(TIGER_PICS_PATH)]


def scale_picture(picture):
    w, h = picture.get_size()
    h_ratio = float(h) / MAX_PICTURE_HEIGHT
    new_size = (int(float(w) / h_ratio), int(float(h) / h_ratio))
    return pg.transform.smoothscale(picture, new_size)


def get_player_frames():
    filename = os.path.join(SPRITES_PATH, PLAYER_SPRITES_FILENAME)
    image = load_image(filename)
    image.set_colorkey(WHITE)
    return [image.subsurface(x, 0, PLAYER_H, PLAYER_W)
            for x in range(0, image.get_width(), PLAYER_W)]

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


def cleanup(obj):
    if obj:
        for name, attr in obj.__dict__.items():
            try:
                attr.cleanup()
            except AttributeError:
                pass
            try:
                iterable = iter(attr)
                for item in iterable:
                    try:
                        item.cleanup()
                    except AttributeError:
                        pass
            except:
                TypeError
            delattr(obj, name)
    del obj

#######################################################


class ImgObj(pg.sprite.Sprite):
    def __init__(self, pos=OFFSCREEN, image=None,
                 width=0, height=0, alignment=TOPLEFT):
        pg.sprite.Sprite.__init__(self)
        self.alignment = alignment
        if image:
            self.image = image
            self.rect = self.image.get_rect()
        else:
            self.image = pg.Surface((width, height))
            self.rect = pg.Rect(pos, (width, height))
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

    def random_rotate(self):
        pos = tuple(self.pos)
        self.image = pg.transform.rotate(self.image, random.choice(DEGREES))
        self.rect = self.image.get_rect()
        self.pos = pos

    def collidelistall(self, a_list):
        return self.rect.collidelistall(a_list)

    def collide_pos(self, pos):
        return self.rect.collidepoint(pos)

    def collide_rect(self, rect):
        if isinstance(rect, ImgObj):
            rect = rect.rect
        return self.rect.colliderect(rect)

    def cleanup(self):
        cleanup(self)

    def fill(self, color):
        self.image = pg.Surface((self.width, self.height))
        self.image.fill(color, rect=self.image.get_rect())

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Text(ImgObj):
    def __init__(self, string, font_name, color, height, *args, **kwargs):
        self.string = string
        self.font_name = font_name
        self.font_height = height
        self.color = color
        self.font = pg.font.SysFont(font_name, height)
        image = self.font.render(string, True, color)
        super(Text, self).__init__(*args, image=image, **kwargs)

    def __str__(self):
        return 'Text at {} saying: {}'.format(self.pos, self.string)

    def cleanup(self):
        super(Text, self).cleanup()
        del self.font

    def update(self, pos=OFFSCREEN, string=None, color=None, height=None):
        if color:
            self.color = color
        if string:
            self.string = string
        if height:
            self.font_height = height
        self.font = pg.font.SysFont(self.font_name, self.font_height)
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
        self.delay = MESSAGE_SCREEN_DELAY

        if alignment == TOPLEFT:
            x = 100
        elif alignment == CENTER:
            x = CENTER_FRAME_X
        messages = list(messages) + CONTINUE_MESSAGES
        self.messages = [
            Text(m, DEFAULT_FONT, ORANGE, MESSAGE_FONT_HEIGHT,
                 pos=(x, (i + 1) * (FRAME_HEIGHT / (len(messages) + 1))),
                 alignment=alignment)
            for i, m in enumerate(messages)]

    def __str__(self):
        return 'MessageScreen:\n{}'.format(
            '\n'.join([str(m) for m in self.messages]))

    def update(self, keys):
        print('MessageScreen update called')
        self.delay -= 1
        if keys[SPACE] and self.delay <= 0:
            print('{} next mode func triggered'.format(self))
            self.next_mode_func()

    def draw(self, surface):
        for m in self.messages:
            m.draw(surface)


class Animator(object):
    def __init__(self, frames):
        self.frames = frames
        self.last_i = len(frames) - 1
        self.current_i = -1

    def __iter__(self):
        return iter(self.frames)

    def __next__(self):
        if self.current_i >= self.last_i:
            self.reset()
        self.current_i += 1
        return self.frames[self.current_i]

    def first(self):
        return self.frames[0]

    def next(self):
        return self.__next__()

    def reset(self):
        self.current_i = -1

    def cleanup(self):
        cleanup(self)


class Player(ImgObj):
    def __init__(self, *args, **kwargs):
        self.frames = get_player_frames()
        self.anim_counter = PLAYER_ANIM_RATE - 1
        self.direction = DIRECTIONS[LEFT]
        self.moving_frames = {
            di: Animator([pg.transform.rotate(f, de) for f in self.frames])
            for di, de in DI_DE.items()}

        super(Player, self).__init__(image=self.frames[0], *args, **kwargs)

    def move(self, direction):
        if direction:
            self.direction = direction
            self.anim_counter += 1
            if self.anim_counter > PLAYER_ANIM_RATE:
                self.image = self.moving_frames[self.direction].next()
                self.anim_counter = 0
        else:
            self.anim_counter = PLAYER_ANIM_RATE
            self.moving_frames[self.direction].reset()
            self.image = self.moving_frames[self.direction].first()


class Tile(ImgObj):
    def __init__(self, matrix_pos, tile_pos_in_matrix, *args, **kwargs):
        pos = rel_tile_pos(matrix_pos, tile_pos_in_matrix)
        super(Tile, self).__init__(*args,
                                   pos=pos,
                                   image=load_rand_tile(),
                                   width=TILE_SIZE,
                                   height=TILE_SIZE,
                                   **kwargs)
        self.random_rotate()
        self.tiger = None

    def __str__(self):
        return 'Tile at {}'.format(self.pos)

    def place_tiger(self, tiger):
        self.tiger = tiger
        self.tiger.pos = self.random_pos()
        self.tiger.random_rotate()

    def reposition(self, matrix_pos, tile_pos_in_matrix, direction=(0, 0)):
        self.pos = rel_tile_pos(matrix_pos, tile_pos_in_matrix, direction)
        self.image = load_rand_tile()
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
        # use direction ?
        self.center_tile = self.tiles[self.center_index][self.center_index]
        print('Update pos: Center tile: {}'.format(self.center_tile))
        self.pos = self.tiles[0][0].topleft
        print('Update pos: tile_matrix.pos: {}'.format(self.pos))

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
                                    image=load_tiger_sprite(),
                                    width=TIGER_W,
                                    height=TIGER_H,
                                    **kwargs)
        self.picture = ImgObj(image=picture, pos=CENTER_FRAME_POS,
                              alignment=CENTER)
        self.roar = Text('ROAR', DEFAULT_FONT, BLACK, ROAR_HEIGHT_FAR,
                         alignment=CENTER)
        self.roar_timer = 0
        self.petted = False
        self.desired_pet_speed = random.randrange(MIN_PET_SPEED, MAX_PET_SPEED)
        self.too_fast = self.desired_pet_speed * TOO_FAST_MOD
        self.too_slow = self.desired_pet_speed * TOO_SLOW_MOD
        self.roar_min = random.randrange(ROAR_MIN, ROAR_MAX)
        self.roar_max = random.randrange(self.roar_min, ROAR_MAX)

    def update(self, tile_matrix):
        x, y = OFFSCREEN
        self.roar_timer += 1
        if self.roar_timer >= self.roar_max:
            self.roar_timer = 0
        if self.roar_timer >= self.roar_min:
            if self.x not in range(FRAME_WIDTH):
                x = 30  # fix to something more specific
                y = self.y
            if self.y not in range(FRAME_HEIGHT):
                x = self.x
                y = 30
        self.roar.update(pos=(x, y))

    def draw_picture(self, surface):
        self.picture.draw(surface)

    def draw(self, surface):
        super(Tiger, self).draw(surface)
        self.roar.draw(surface)


class TigerManager(object):
    '''
    Handles all Tiger objects for both movement on map as well as petting.
    '''
    def __init__(self):
        tiger_pics = load_tiger_pics()
        self.tigers = [Tiger(pic) for pic in tiger_pics]
        self.pet_text = Text('', DEFAULT_FONT, ORANGE, PET_TEXT_HEIGHT,
                             pos=PET_TEXT_CENTER, alignment=CENTER)
        self.pet_bar = ImgObj(height=PET_BAR_HEIGHT, width=1,
                              pos=PET_BAR_CENTER, alignment=CENTER)
        self.reset()

    def __str__(self):
        return 'Tigers:\n{}'.format('\n'.join(self.tigers))

    def reset(self):
        self.tiger_to_pet = None
        self.last_pet_pos = None
        self.distances = []  # give a better starting list of distances
        self.purr_score = 0
        self.yawn_score = 0
        self.grrr_score = 0
        self.total_score = 0
        self.petting_time = PETTING_TIME

    def pet(self, mouse):
        mousedown = bool(mouse.get_pressed()[0])
        mouse_pos = mouse.get_pos()
        result = self.process_pet(self.tiger_to_pet, mousedown, mouse_pos)
        if result:
            messages = list(PET_FEEDBACK[result])
            messages.append('Petting score: {}'.format(int(self.purr_score)))
            self.tiger_to_pet.petted = True
            self.tiger_to_pet.pos = OFFSCREEN
            self.total_score += self.purr_score
            self.reset()
            return messages
        return None

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
            self.purr_score += 1 / abs(pet_speed - tiger.desired_pet_speed)
            self.pet_text.update(pos=PET_TEXT_CENTER, string=PURR,
                                 color=ORANGE)
            self.pet_bar.fill(ORANGE)

        if self.petting_time <= 0:
            return PURR
        elif self.yawn_score >= YAWN_MAX:
            return YAWN
        elif self.grrr_score >= GRRR_MAX:
            return GRRR
        return None

    def tigers_to_pet(self):
        return [tiger for tiger in self.tigers if not tiger.petted]

    def collide(self, player):
        for tiger in self.tigers:
            if tiger.collide_rect(player):
                self.tiger_to_pet = tiger
                return True
        return False

    def update(self, tile_matrix):
        for tiger in self.tigers_to_pet():
            tiger.update(tile_matrix)

    def move(self, direction):
        direction = mirror_direction(direction)
        for tiger in self.tigers_to_pet():
            tiger.move(direction)
            tiger.roar.move(direction)

    def draw_petting(self, surface):
        self.tiger_to_pet.draw_picture(surface)
        self.pet_bar.draw(surface)
        self.pet_text.draw(surface)

    def draw(self, surface):
        for tiger in self.tigers_to_pet():
            tiger.draw(surface)
            tiger.roar.draw(surface)


class GameState(object):
    '''
    Master game state, containing current player action, tile map, game
    objects on map, and any messages to display between modes.
    Evaluates Pygame events and updates accordingly.
    Evaluates Pygame key and mouse input and sets game attributes accordingly.
    '''
    def __init__(self, matrix_size):
        self.matrix_size = matrix_size
        self.mode = MESSAGE
        self.message_screen = MessageScreen(START_MENU_MESSAGES, self.start_game)
        self.tigers = TigerManager()
        self.tile_matrix = TileMatrix(matrix_size, self.tigers.tigers_to_pet(),
                                      pos=init_matrix_pos(matrix_size))
        self.player = Player(pos=tuple(CENTER_FRAME_POS), alignment=CENTER)
        self.direction_stack = []
        self.direction = None
        self.total_score = 0
        self.game_over = False

    def __str__(self):
        return '''
        GameState current mode: {}
        {}
        {}
        '''.format(self.mode, self.tile_matrix, self.message_screen)

    def reset(self):
        self.direction = None
        self.message_screen = None

    def help_me(self):
        self.mode = MESSAGE
        # need to change this to call back to previous message screen
        # maybe use a "next mode" attribute
        cleanup(self.message_screen)
        self.message_screen = MessageScreen(HELP_MESSAGES,
                                            self.start_walking)

    def start_game(self):
        self.mode = MESSAGE
        cleanup(self.message_screen)
        self.message_screen = MessageScreen(NEW_GAME_MESSAGES,
                                            self.start_walking)

    def start_petting(self):
        print('start_petting')
        self.mouse.set_visible(True)
        self.mode = PETTING
        self.reset()

    def start_walking(self):
        print('start_walking')
        self.mouse.set_visible(False)
        self.mode = WALKING
        self.reset()

    def process_events(self, events):
        '''
        Assign key and mouse events to self attributes keeping track
        of movements, etc.
        '''
        for event in events:
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.quit()
            elif hasattr(event, 'key') and event.key in DIRECTIONS.keys():
                direction = DIRECTIONS[event.key]
                if event.type == pg.KEYDOWN:
                    self.direction_stack.append(direction)
                if event.type == pg.KEYUP:
                    if direction in self.direction_stack:
                        self.direction_stack.remove(direction)
                if self.direction_stack:
                    self.direction = self.direction_stack[-1]
                else:
                    self.direction = None

    def move(self, direction):
        self.player.move(direction)
        if direction:
            self.tile_matrix.move(direction)
            self.tigers.move(direction)
            if self.tigers.collide(self.player):
                self.mode = MESSAGE
                cleanup(self.message_screen)
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
        if self.mode == MESSAGE:
            self.message_screen.update(self.keys)
        if self.mode == WALKING:
            self.tigers.update(self.tile_matrix)
            self.move(self.direction)
        if self.mode == PETTING:
            result_messages = self.tigers.pet(self.mouse)
            if result_messages:
                self.mode = MESSAGE
                cleanup(self.message_screen)
                self.message_screen = MessageScreen(result_messages,
                                                    self.start_walking)
        if not self.tigers.tigers_to_pet() and not self.game_over:
            self.game_over = True
            self.mode = MESSAGE
            cleanup(self.message_screen)
            messages = list(GAME_OVER_MESSAGES)
            messages.append('Your final score: {}'.format(self.total_score))
            self.message_screen = MessageScreen(GAME_OVER_MESSAGES,
                                                self.restart)

    def restart(self):
        print('restarting: cleaning up...')
        cleanup(self.tigers)
        cleanup(self.tile_matrix)
        cleanup(self.player)
        cleanup(self.message_screen)
        print('finished cleanup. reinitializing...')
        self.__init__(self.matrix_size)

    def quit(self):
        pg.quit()
        sys.exit()


def main():

    try:
        size = int(sys.argv[1])
    except IndexError:
        size = 3

    game_state = GameState(size)
    print(str(game_state))

    while True:
        FRAME.fill(BLACK)
        game_state.keys = pg.key.get_pressed()
        game_state.mouse = pg.mouse
        game_state.process_events(pg.event.get())
        game_state.update()
        game_state.draw(FRAME)
        pg.display.update()
        fps_clock.tick(FPS)

if __name__ == '__main__':
    main()
