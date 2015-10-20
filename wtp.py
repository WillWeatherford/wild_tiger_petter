import os
import sys
import pygame
import random
pygame.init()
import pygame.locals as pgl
#########################
# GLOBAL CONSTANTS

OFFSCREEN = (-200, -200)

DEFAULT_FONT = 'arial'

UP = pgl.K_UP
DOWN = pgl.K_DOWN
RIGHT = pgl.K_RIGHT
LEFT = pgl.K_LEFT

DIRECTIONS = {UP: (0, 1),
              RIGHT: (-1, 0),
              LEFT: (1, 0),
              DOWN: (0, -1)}


CENTER = 'center'
CENTER_CENTER = 'center center'


MOVE_SPEED = 1

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

FPS = 30  # frames per second setting
fps_clock = pygame.time.Clock()

FRAME_WIDTH, FRAME_HEIGHT = 800, 600
CENTER_FRAME_POS = (FRAME_WIDTH / 2, FRAME_HEIGHT / 2)
FRAME = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))

TILES_PATH = './tiles'
SPRITES_PATH = './sprites'
TIGER_PICS_PATH = './tiger_pics'
TIGER_SPRITES_FILENAME = 'tiger_sprites.png'
TILE_SIZE = 200
DEGREES = [0, 90, 180, 270]

TIGER_W, TIGER_H = 19, 51

#############################


class Text(object):

    def __init__(self, font_name, pos, string, height, color,
                 alignment=CENTER_CENTER):
        self.font_name = font_name
        self.pos = pos
        self.string = string
        self.height = height
        self.color = color
        self.alignment = alignment
        self.font = pygame.font.SysFont(self.font_name, self.height)
        self.update(self.pos, self.string)

    def __str__(self):
        return 'Text at {} saying: {}'.format(self.pos, self.string)

    def get_pos(self):
        return self.pos

    def align(self, pos):
        if self.alignment == CENTER:
            self.rect.midtop = pos
        elif self.alignment == CENTER_CENTER:
            self.rect.center = pos
        elif self.alignment == RIGHT:
            self.rect.topright = pos
        elif self.alignment == LEFT:
            self.rect.topleft = pos

    def update(self, pos=None, string=None, color=None):
        if color:
            self.color = color
        if string:
            self.string = string
        if pos:
            self.pos = pos
        self.surface_obj = self.font.render(self.string, True, self.color)
        self.rect = self.surface_obj.get_rect()
        self.align(self.pos)

    def draw(self, surface):
        surface.blit(self.surface_obj, self.rect)

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
    rect = (0, 0, TIGER_W, TIGER_H)
    filename = os.path.join(SPRITES_PATH, TIGER_SPRITES_FILENAME)
    image = load_image(filename)
    return image.subsurface(rect)


class ImgObj(pygame.sprite.Sprite):
    def __init__(self, pos=OFFSCREEN, width=0, height=0):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.rect = pygame.Rect(self.x, self.y, width, height)

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

    @property
    def width(self):
        return self._rect.width

    @property
    def height(self):
        return self._rect.height

    @property
    def center(self):
        return self._rect.center

    def move(self, direction):
        if not isinstance(direction, tuple) and len(direction) == 2:
            raise TypeError('{} direction must be tuple len 2.'
                            ''.format(repr(self)))
        x, y = direction
        self._x += x
        self._y += y
        self._rect.move_ip(x, y)

    def collide(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class Tile(ImgObj):
    def __init__(self, *args, **kwargs):
        super(Tile, self).__init__(*args,
                                   width=TILE_SIZE,
                                   height=TILE_SIZE,
                                   **kwargs)
        self.image = load_rand_tile()

    def __str__(self):
        return 'Tile at {}'.format(self.pos)


class Tiger(ImgObj):
    def __init__(self, pic, *args, **kwargs):
        super(Tiger, self).__init__(*args,
                                    width=TIGER_W,
                                    height=TIGER_H,
                                    **kwargs)
        self.pic = pic
        self.image = get_tiger_sprite()


class Player(ImgObj):
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)

    def draw(self, surface):
        self.image = pygame.draw.circle(surface, RED, self.pos, 10)


class TileMatrix(ImgObj):
    def __init__(self, size, *args, **kwargs):
        super(TileMatrix, self).__init__(*args,
                                         width=TILE_SIZE * size,
                                         height=TILE_SIZE * size,
                                         **kwargs)
        assert size % 2 != 0 and size >= 3, ('Tile Matrix size must be '
                                             'an odd number at least 5')
        self.size = int(size)
        self.index_range = range(size)
        self.center_index = size / 2
        self.init_matrix_pos(size)
        self.tiles = [[Tile(self.rel_tile_pos((matrix_x, matrix_y)))
                       for matrix_y in self.index_range]
                      for matrix_x in self.index_range]
        self.center_tile = self.get_center_tile()

    def __str__(self):
        tiles = '\n'.join([' | '.join(
            ['({}, {}): {}'.format(x, y, str(self.tiles[x][y]))
             for x in self.index_range])
            for y in self.index_range])
        return 'Tile Matrix centered at {}\n{}'.format(self.pos, tiles)

    def init_matrix_pos(self, matrix_size):
        return tuple([xy - (TILE_SIZE * (matrix_size / 2)) - TILE_SIZE / 2
                      for xy in CENTER_FRAME_POS])

    def rel_tile_pos(self, matrix_pos, direction=(0, 0)):
        return tuple(map(
            lambda xy1, xy2, xy3: xy1 + (TILE_SIZE * xy2) + (TILE_SIZE * xy3),
            self.pos, matrix_pos, direction))

    def redraw(self, direction):
        '''
        Repositions all Tiles in the matrix when the center tile moves off of
        the center point where the player is.
        Overwrites tiles on the trailing edge. Creates new tiles on the leading
        edge.
        '''
        print('Matrix pos before redraw: {}'.format(self))

        # dx and dy track the individual x and y movement vectors
        dx, dy = direction
        # remember: directions are reversed compared to arrow direction
        print('Direction: {}'.format(direction))

        x_range = self.index_range[::-dx or -dy]
        y_range = self.index_range[::-dy or -dx]
        for x in x_range:
            for y in y_range:
                print('Tile at ({}, {}) moves to ({}, {})'.format(
                    x, y, x + dx, y + dy))
                if x + dx >= 0 and y + dy >= 0:
                    try:
                        self.tiles[x + dx][y + dy] = self.tiles[x][y]
                    except IndexError:
                        print('Index error raised; need to ignore and insert '
                              'at end of row/column')
                if (dx and x == x_range[-1]) or (dy and y == y_range[-1]):
                    self.tiles[x][y] = Tile(self.rel_tile_pos((x - dx, y - dy)))

        self.center_tile = self.get_center_tile()
        self.pos = self.tiles[0][0].pos
        print('Matrix pos after redraw: {}'.format(self))

    def get_matrix(self):
        for row in self.tiles:
            for tile in row:
                yield tile

    def get_center_tile(self, direction=(0, 0)):
        return self.tiles[self.center_index][self.center_index]

    def off_center(self):
        return not self.center_tile.collide(CENTER_FRAME_POS)

    def move(self, direction):
        # note, direction is a tuple (x change, y change)
        super(TileMatrix, self).move(direction)
        self.rect.move_ip(direction)
        for tile in self.get_matrix():
            tile.move(direction)
        if self.off_center():
            print('Tile off center; redrawing.')
            self.redraw(direction)

    def draw(self, surface):
        for tile in self.get_matrix():
            tile.draw(surface)


class GameState(object):
    '''
    Master game state, containing current player action, tile map, game
    objects on map.
    '''

    def __init__(self, matrix_size):
        self.tile_matrix = TileMatrix(matrix_size)
        self.tigers = self.init_tigers()
        self.player = Player(pos=CENTER_FRAME_POS)
        self.direction = None

    def __str__(self):
        return '''
        GameState;
        {}
        '''.format(self.tile_matrix)

    def init_tigers(self):
        tiger_pics = [load_image(pic) for pic in get_file_paths(TIGER_PICS_PATH)]
        return [Tiger(pic, pos=self.random_pos()) for pic in tiger_pics]

    def random_pos(self):
        return tuple(random.randrange(d) for d in self.tile_matrix.rect.size)

    def move(self):
        if self.direction:
            self.tile_matrix.move(self.direction)
            for tiger in self.tigers:
                tiger.move(self.direction)

    def draw(self, surface):
        self.tile_matrix.draw(surface)
        for tiger in self.tigers:
            tiger.draw(surface)
        self.player.draw(surface)

    def process_event(self, event):
        if event.type == pgl.KEYUP and event.key in DIRECTIONS.keys():
            self.direction = None
        if event.type == pgl.KEYDOWN:
            if event.key == pgl.K_ESCAPE:
                self.quit()
            self.direction = DIRECTIONS.get(event.key, None)
        if event.type == pgl.QUIT:
            self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()


def main():

    # initialize

    game_state = GameState(5)
    print(str(game_state))

    while True:
        FRAME.fill(BLACK)
        events = pygame.event.get()
        if events:
            game_state.process_event(events[0])
        game_state.move()
        game_state.draw(FRAME)
        pygame.display.update()
        fps_clock.tick(FPS)

if __name__ == '__main__':
    main()
