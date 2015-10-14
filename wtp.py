import os
import sys
import pygame
import random
pygame.init()
from pygame.locals import USEREVENT, MOUSEBUTTONUP, QUIT

#########################
# GLOBAL CONSTANTS

DEFAULT_FONT = 'arial'

UP = "up"
DOWN = "down"
CENTER = "center"
CENTER_CENTER = "center center"
RIGHT = "right"
LEFT = "left"

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


#############################


def get_file_paths(root):
    return [os.path.join(p, f) for p, d, files in os.walk(root) for f in files]


def load_image(filename):
    return pygame.image.load(filename).convert()


def load_rand_tile():
    return load_image(random.choice(get_file_paths(TILES_PATH)))


class ImgObj(object):
    pass


class Tile(ImgObj):
    pass


class TileMatrix(object):
    def __init__(self, size):
        self.size = size
        self.pos = 


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


class GameState(object):

    def __init__(self, test_text=None):
        self.test_text = test_text

    def draw(self, surface):
        self.test_text.draw(surface)


class Tiger(object):
    pass


def main():

    # initialize

    file_paths = get_file_paths(TILES_PATH)
    tile = pygame.image.load(random.choice(file_paths)).convert()
    game_state = GameState()
    game_state.test_text = Text(DEFAULT_FONT, (100, 100), 'Test', 20, RED)
    while True:
        FRAME.fill(BLACK)
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                pygame.quit()
                sys.exit()
                # game_state.process_click(event.pos)
            if event.type == USEREVENT + 1:
                # game_state.process_game()
                pass
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        game_state.draw(FRAME)
        #
        FRAME.blit(tile, (100, 100))
        pygame.display.update()
        fps_clock.tick(FPS)

if __name__ == '__main__':
    main()
