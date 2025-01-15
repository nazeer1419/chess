from OpenGL.GL import *
from OpenGL.GLU import *

from config import Config
from board_position import BoardPosition
from pieces import Piece
from point import Point

class PromotionBoard:
    def __init__(self, position:Point, player:str):
        self.board_positions = {}

        next_position = position.clone()

        for row in range(Config.PROMOTION_ROWS):
            # reset x position
            next_position.x = position.x

            for column in range(Config.PROMOTION_COLUMNS):
                board_position = Point(next_position.x + Config.BOARD_RING_SIZE * Config.SCALE, next_position.y - Config.BOARD_RING_SIZE * Config.SCALE)
                piece_position = Point(board_position.x + Config.BOARD_PADDING * Config.SCALE, board_position.y - Config.BOARD_PADDING * Config.SCALE)

                new_board_position = BoardPosition(
                    position = board_position,
                    row = row,
                    column = column,
                    piece = self.get_default_piece(row, column, piece_position, player),
                    promotion = True,
                )

                # updates
                self.board_positions[row, column] = new_board_position

                # update next_position x
                next_position.x = next_position.x + Config.SCALE * (Config.BOARD_RING_SIZE + Config.BOARD_PADDING * 2 + Config.PIECE_SIZE)

            # update next_position y
            next_position.y = next_position.y - Config.SCALE * (Config.BOARD_RING_SIZE + Config.BOARD_PADDING * 2 + Config.PIECE_SIZE)

    def draw(self):
        for board_position in self.board_positions.values():
            board_position.draw()

    def get_default_piece(self, row:int, column:int, piece_position:Point, player:str):
        if row == 0 and column == 0:
            return Piece('Rook', player, piece_position, row, column)
        elif row == 1 and column == 0:
            return Piece('Knight', player, piece_position, row, column)
        elif row == 2 and column == 0:
            return Piece('Bishop', player, piece_position, row, column)
        elif row == 3 and column == 0:
            return Piece('Queen', player, piece_position, row, column)
        else:
            return None
