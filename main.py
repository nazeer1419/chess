import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from config import Config
from pieces import Piece
from point import Point
from board import Board, BoardPosition

def reshape_screen(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(*Config.CAMERA_SIDES)
    glMatrixMode(GL_MODELVIEW)

def main():
    pygame.init()
    #pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_mode(Config.SCREEN_SIZE, DOUBLEBUF | OPENGL)
    reshape_screen(*Config.SCREEN_SIZE)

    '''# enable alpha channels & alpha blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)'''

    board = Board(Point(Config.CAMREA_LEFT_SIDE, Config.CAMREA_TOP_SIDE))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == VIDEORESIZE:
                new_width, new_height = event.size
                reshape_screen(new_width, new_height)
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                width, height = pygame.display.get_surface().get_size()

                true_x = Config.CAMREA_LEFT_SIDE + (mouse_x / float(width)) * (Config.CAMREA_RIGHT_SIDE - Config.CAMREA_LEFT_SIDE)
                true_y = Config.CAMREA_BOTTOM_SIDE + (1 - (mouse_y / float(height))) * (Config.CAMREA_TOP_SIDE - Config.CAMREA_BOTTOM_SIDE)

                print(f'mouse pressed ({true_x}, {true_y})')

                board.evalutate_click(true_x, true_y)
            
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #glClearColor(0, 0, 0, 1)

        board.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()