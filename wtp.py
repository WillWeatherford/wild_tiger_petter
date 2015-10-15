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

DIRECTIONS = (UP, RIGHT, LEFT, DOWN)

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


class ImgObj(object):
    def __init__(self, pos=OFFSCREEN):
        self.pos = pos

    def __str__(self):
        return '{} at {}'.format(repr(self), self.pos)

    @property
    def pos(self):
        return self._x, self._y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @pos.setter
    def pos(self, pos):
        if not isinstance(pos, tuple) and len(pos) == 2:
            raise TypeError('{} pos must be tuple len 2.'.format(repr(self)))
        self._x = pos[0]
        self._y = pos[1]

    def move(self, direction):
        if direction == LEFT:
            self._x += MOVE_SPEED
        elif direction == RIGHT:
            self._x -= MOVE_SPEED
        elif direction == UP:
            self._y += MOVE_SPEED
        elif direction == DOWN:
            self._y -= MOVE_SPEED


class Tile(ImgObj):
    def __init__(self, *args, **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        self.image = load_rand_tile()

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class Tiger(ImgObj):
    pass


class TileMatrix(ImgObj):
    def __init__(self, size, *args, **kwargs):
        super(TileMatrix, self).__init__(*args, **kwargs)
        assert size % 2 != 0 and size >= 5, ('Tile Matrix size must be '
                                             'an odd number at least 5')
        self.size = int(size)
        self.index_range = range(0 - size / 2, (size / 2) + 1)
        self.rows = {mx: {my: Tile(self.rel_tile_pos((mx, my))) for my in self.index_range}
                     for mx in self.index_range}

    def __str__(self):
        tiles = ''
        # tiles = '\n'.join(list(str(t) for t in self.get_matrix()))
        return '{}\n{}'.format(self.pos, tiles)

    def rel_tile_pos(self, matrix_pos):
        # return (TILE_SIZE * self.pos[i] * xy for i, xy enumerate(matrix_pos))
        print('{} * {} * {}'.format(matrix_pos, self.pos, TILE_SIZE))
        x = self.x + (matrix_pos[0] * TILE_SIZE) - (TILE_SIZE / 2)
        y = self.y + (matrix_pos[1] * TILE_SIZE) - (TILE_SIZE / 2)
        return (x, y)

    def get_matrix(self):
        for row, col in self.rows.items():
            for pos, tile in col.items():
                yield tile

    def move(self, direction):
        super(TileMatrix, self).move(direction)
        print(str(self))
        for tile in self.get_matrix():
            tile.move(direction)

    def draw(self, surface):
        for tile in self.get_matrix():
            tile.draw(surface)


class GameState(object):

    def __init__(self):
        self.tile_matrix = TileMatrix(5, pos=CENTER_FRAME_POS)

    def __str__(self):
        return '''
        GameState:
        \tTileMatrix:
        \t{tm}
        '''.format(tm=self.tile_matrix)

    def move(self, direction):
        self.tile_matrix.move(direction)

    def draw(self, surface):
        self.tile_matrix.draw(surface)

    def process_event(self, event):
        if event.type == pgl.KEYDOWN:
            if event.key == pgl.K_ESCAPE:
                self.quit()
            elif event.key in DIRECTIONS:
                self.move(event.key)

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
        for event in pygame.event.get():
            game_state.process_event(event)
        game_state.draw(FRAME)
        pygame.display.update()
        fps_clock.tick(FPS)

if __name__ == '__main__':
    main()
