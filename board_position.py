from OpenGL.GL import *
from OpenGL.GLU import *

from config import Config
from pieces import Piece
from point import Point

class BoardPosition:
    def __init__(self, position:Point, row:int, column:int, piece:Piece, promotion:bool = False):
        self.position = position
        self.row = row
        self.column = column
        self.piece = piece
        self.selected = False
        self.valid = False
        self.promotion = promotion

    def draw(self):
        # get bounding box coordinates
        P1, P2, P3, P4 = self.get_bounding_box()

        # select color
        if self.selected:
            color = Config.SELECTED_COLOR
        elif self.valid:
            color = Config.VALID_COLOR
        else:
            if (self.row % 2 == 0 and self.column % 2 == 0) or (self.row % 2 == 1 and self.column % 2 == 1):
                color = Config.BOARD_SECONDARY_COLOR
            else:
                color = Config.BOARD_PRIMARY_COLOR

        # draw board position
        glBegin(GL_QUADS)

        glColor3f(*color)

        glVertex2f(P1.x, P1.y)
        glVertex2f(P2.x, P2.y)
        glVertex2f(P3.x, P3.y)
        glVertex2f(P4.x, P4.y)

        glEnd()

        # draw piece if exist
        if self.piece:
            self.piece.draw()

    def move_piece_to(self, other_board_position:'BoardPosition'):
        removed_piece = other_board_position.piece

        # move piece from here to other
        other_board_position.piece = self.piece

        # empty here
        self.piece = None

        # re-calculate the position for piece
        position = other_board_position.position

        other_board_position.piece.position = Point(position.x + (Config.BOARD_PADDING * Config.SCALE), position.y - (Config.BOARD_PADDING * Config.SCALE))

        # update row & column
        other_board_position.piece.row = other_board_position.row
        other_board_position.piece.column = other_board_position.column

        # update pawn double move ONLY if, the piece is a pawn, and piece was not moved, the difference is two rows
        if other_board_position.piece.piece_name == 'PAWN' and not other_board_position.piece.moved and abs(self.row - other_board_position.row) == 2:
            other_board_position.piece.pawn_double_move = True

        # update moved flag
        other_board_position.piece.moved = True

        # handle removed piece
        return removed_piece

    def get_bounding_box(self):
        # get constants
        SCALE = Config.SCALE
        PIECE_SIZE = Config.PIECE_SIZE
        BOARD_PADDING = Config.BOARD_PADDING

        # calculate points
        P1 = self.position.clone()
        P2 = Point(self.position.x + (PIECE_SIZE + BOARD_PADDING * 2) * SCALE, self.position.y)
        P3 = Point(self.position.x + (PIECE_SIZE + BOARD_PADDING * 2) * SCALE, self.position.y - (PIECE_SIZE + BOARD_PADDING * 2) * SCALE)
        P4 = Point(self.position.x, self.position.y - (PIECE_SIZE + BOARD_PADDING * 2) * SCALE)

        return P1, P2, P3, P4