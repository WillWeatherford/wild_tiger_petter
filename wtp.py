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
TILE_SIZE = 200

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


def get_file_paths(root):
    return [os.path.join(p, f) for p, d, files in os.walk(root) for f in files]


def load_image(filename):
    return pygame.image.load(filename).convert()


def load_rand_tile():
    # random rotation also
    return load_image(random.choice(get_file_paths(TILES_PATH)))


class ImgObj(pygame.sprite.Sprite):
    def __init__(self, pos=OFFSCREEN, width=0, height=0):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.rect = pygame.Rect(self.x, self.y, width, height)

    def __str__(self):
        return '{} at {}; w: {}, h: {}'.format(repr(self), self.pos, self.width, self.height)

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

    def move(self, direction):
        if not isinstance(direction, tuple) and len(direction) == 2:
            raise TypeError('{} direction must be tuple len 2.'
                            ''.format(repr(self)))
        x, y = direction
        self._x += x
        self._y += y
        self._rect.move_ip(x, y)


class Tile(ImgObj):
    def __init__(self, *args, **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        self.image = load_rand_tile()

    def collide(self, pos):
        print('{} colling with center point? {}'
              ''.format(str(self), self.rect.collidepoint(pos)))
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class Tiger(ImgObj):
    pass


class Player(ImgObj):
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)

    def draw(self, surface):
        self.image = pygame.draw.circle(surface, RED, self.pos, 10)


class TileMatrix(ImgObj):
    def __init__(self, size, *args, **kwargs):
        super(TileMatrix, self).__init__(*args, **kwargs)
        assert size % 2 != 0 and size >= 5, ('Tile Matrix size must be '
                                             'an odd number at least 5')
        self.size = int(size)
        self.index_range = range(0 - size / 2, (size / 2) + 1)
        self.rows = {matrix_x:
                     {matrix_y: Tile(self.rel_tile_pos((matrix_x, matrix_y)),
                                     TILE_SIZE,
                                     TILE_SIZE)
                      for matrix_y in self.index_range}
                     for matrix_x in self.index_range}

    def __str__(self):
        tiles = ''
        # tiles = '\n'.join(list(str(t) for t in self.get_matrix()))
        return '{}\n{}'.format(self.pos, tiles)

    def rel_tile_pos(self, matrix_pos):
        # return (TILE_SIZE * self.pos[i] * xy for i, xy enumerate(matrix_pos))
        # print('{} * {} * {}'.format(matrix_pos, self.pos, TILE_SIZE))
        x = self.x + (matrix_pos[0] * TILE_SIZE) - (TILE_SIZE / 2)
        y = self.y + (matrix_pos[1] * TILE_SIZE) - (TILE_SIZE / 2)
        return (x, y)

    def redraw(self, direction):
        if direction == UP:
            print self.self.index_range[-1]
            for i in self.index_range[:-1]:
                self.rows[i] = self.rows[i + 1]

    def get_matrix(self):
        for row, col in self.rows.items():
            for pos, tile in col.items():
                yield tile

    def off_center(self):
        print(str(self.rows[0][0].rect))
        return not self.rows[0][0].collide(CENTER_FRAME_POS)

    def move(self, direction):
        # note, direction is a tuple (x change, y change)
        super(TileMatrix, self).move(direction)
        for tile in self.get_matrix():
            tile.move(direction)
        if self.off_center():
            print('Tile off center.')
        #     self.redraw(direction)

    def draw(self, surface):
        for tile in self.get_matrix():
            tile.draw(surface)


class GameState(object):

    def __init__(self):
        self.tile_matrix = TileMatrix(5, pos=CENTER_FRAME_POS)
        self.player = Player(pos=CENTER_FRAME_POS)
        self.direction = None

    def __str__(self):
        return '''
        GameState:
        \tTileMatrix:
        \t{tm}
        '''.format(tm=self.tile_matrix)

    def move(self):
        if self.direction:
            self.tile_matrix.move(self.direction)
            # move tigers

    def draw(self, surface):
        self.tile_matrix.draw(surface)
        # draw tigers
        self.player.draw(surface)

    def process_event(self, event):
        if event.type == pgl.KEYDOWN:
            if event.key == pgl.K_ESCAPE:
                self.quit()
            self.direction = DIRECTIONS.get(event.key, None)
        if event.type == pgl.KEYUP and event.key in DIRECTIONS.keys():
            self.direction = None
        if event.type == pgl.QUIT:
            self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()


def main():

    # initialize

    game_state = GameState()
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
