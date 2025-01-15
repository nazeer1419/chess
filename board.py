from OpenGL.GL import *
from OpenGL.GLU import *

from config import Config
from board_position import BoardPosition
from promotion_board import PromotionBoard
from pieces import Piece
from point import Point

class Board:
    def __init__(self, position:Point):
        self.board_positions = {}
        self.valid_positions = {}

        next_position = position.clone()

        for row in range(Config.BOARD_SIZE):
            # reset x position
            next_position.x = position.x

            for column in range(Config.BOARD_SIZE):
                board_position = Point(next_position.x + Config.BOARD_RING_SIZE * Config.SCALE, next_position.y - Config.BOARD_RING_SIZE * Config.SCALE)
                piece_position = Point(board_position.x + Config.BOARD_PADDING * Config.SCALE, board_position.y - Config.BOARD_PADDING * Config.SCALE)

                new_board_position = BoardPosition(
                    position = board_position,
                    row = row,
                    column = column,
                    piece = self.get_default_piece(row, column, piece_position)
                )

                # updates
                self.board_positions[row, column] = new_board_position

                # update next_position x
                next_position.x = next_position.x + Config.SCALE * (Config.BOARD_RING_SIZE + Config.BOARD_PADDING * 2 + Config.PIECE_SIZE)

            # update next_position y
            next_position.y = next_position.y - Config.SCALE * (Config.BOARD_RING_SIZE + Config.BOARD_PADDING * 2 + Config.PIECE_SIZE)

        self.selected_board_position:BoardPosition = None
        self.player_turn = '1'

        # Promotion tile stuff
        self.last_next_position = Point(next_position.x, position.y)
        self.init_promotion = False
        self.promotion_board = None

    def draw(self):
        for board_position in self.board_positions.values():
            board_position.draw()

        if self.init_promotion:
            self.promotion_board.draw()

    def reset(self, selected:bool = False, highlight:bool = False, double_move:bool = False):
        # reset all selected ones
        for board_position in self.board_positions.values():
            board_position:BoardPosition

            if selected:
                self.selected_board_position = None
                self.valid_positions = {}
                self.init_promotion = False
                self.promotion_board = None
            if highlight:
                board_position.selected = False
                board_position.valid = False

                # reset flag if the piece is from the other player
                if board_position.piece and board_position.piece.player == self.player_turn:
                    board_position.piece.pawn_double_move = False

    def evalutate_click(self, x:float, y:float):
        board_position = self.get_click_board_position(x, y)

        if board_position:
            # if promotion is initiated
            if self.init_promotion:
                if board_position.promotion:
                    print(self.selected_board_position.piece)
                    self.selected_board_position.piece.piece_name = board_position.piece.piece_name

                    # switch player
                    if self.player_turn == '1':
                        self.player_turn = '2'
                    elif self.player_turn == '2':
                        self.player_turn = '1'
                    else:
                        self.player_turn = '0'

                    # reset selected & highlight
                    self.reset(True, True)
            # player selected valid movement
            elif board_position.valid:
                piece = self.selected_board_position.piece

                # TODO: Fucking castling
                if board_position.piece and piece.piece_name == 'KING' and board_position.piece.piece_name == 'ROOK' and piece.player == board_position.piece.player:
                    castle_row, castle_column = board_position.piece.row, board_position.piece.column
                    king_row, king_column = piece.row, piece.column
                    # change is considered from the King point of view
                    if castle_column == 0:
                        king_column_change = -2
                        rook_column_change = -1
                    elif castle_column == 7:
                        king_column_change = 2
                        rook_column_change = 1
                    else:
                        king_column_change = 0
                        rook_column_change = 0

                    king_new_position = self.board_positions[king_row, king_column + king_column_change]
                    castle_new_position = self.board_positions[king_row, king_column + rook_column_change]

                    print(king_new_position.piece)
                    print(castle_new_position.piece)

                    self.selected_board_position.move_piece_to(king_new_position)
                    board_position.move_piece_to(castle_new_position)

                else:
                    # move piece
                    removed_piece = self.selected_board_position.move_piece_to(board_position)

                # Fucking En passant & Promotion
                if piece.player == '1':
                    axis_change = 1
                    row_threshold = 0
                elif piece.player == '2':
                    axis_change = -1
                    row_threshold = 7
                else:
                    axis_change = 0
                    row_threshold = -1

                # get row & column for left/right
                row, column = piece.row + axis_change, piece.column

                # check we are not out of bound
                if (row >= 0 and row < Config.BOARD_SIZE) and (column >= 0 and column < Config.BOARD_SIZE):
                    # get other board position
                    other_board_position:BoardPosition = self.board_positions[row, column]

                    # check if there is a pawn at the bottom/top, if yes, delete it
                    if other_board_position.piece and other_board_position.piece.pawn_double_move:
                        other_piece = other_board_position.piece
                        other_board_position.piece = None

                # Fucking Promotion
                if piece.piece_name == 'PAWN' and piece.row == row_threshold:
                    # initiate promotion
                    self.init_promotion = True
                    start_position = Point(self.last_next_position.x + Config.SCALE * (Config.BOARD_RING_SIZE + Config.BOARD_PADDING * 2 + Config.PIECE_SIZE), self.last_next_position.y)
                    self.promotion_board = PromotionBoard(start_position, self.player_turn)

                # TODO: check game over
                
                if not self.init_promotion:
                    # switch player
                    if self.player_turn == '1':
                        self.player_turn = '2'
                    elif self.player_turn == '2':
                        self.player_turn = '1'
                    else:
                        self.player_turn = '0'

                    # reset selected & highlight
                    self.reset(True, True)
                else:
                    self.reset(False, True)

                    self.selected_board_position = board_position

            # player selected a not valid movement
            else:
                # reset selected
                self.reset(True, True)

                # if board has piece, make it selected
                if board_position.piece:
                    board_position.selected = True
                
                if board_position.piece and board_position.piece.player == self.player_turn:
                    self.selected_board_position = board_position
                    print(f'Three {self.selected_board_position.piece}')

                    if board_position:
                        self.get_valid_positions(board_position)
        # player selected place outside of board
        else:
            # reset selected & highlight
            self.reset(True, True)

        '''for valid_position in self.valid_positions.values():
            valid_position:BoardPosition

            #print(f'{valid_position.row}, {valid_position.column}')'''

    def get_click_board_position(self, x:float, y:float):
        # check where the mouse where clicked
        for board_position in self.board_positions.values():
            board_position:BoardPosition

            # get board position bounding box
            P1, P2, P3, P4 = board_position.get_bounding_box()

            # check if the given coordinates are inside the bounding box
            if (x >= P1.x and x <= P3.x) and (y >= P3.y and y <= P1.y):
                return board_position
        
        # if clicked on promotion board
        if  self.promotion_board:
            for board_position in self.promotion_board.board_positions.values():
                board_position:BoardPosition

                # get board position bounding box
                P1, P2, P3, P4 = board_position.get_bounding_box()

                # check if the given coordinates are inside the bounding box
                if (x >= P1.x and x <= P3.x) and (y >= P3.y and y <= P1.y):
                    return board_position
    
    def get_valid_positions(self, board_position:'BoardPosition'):
        piece = board_position.piece

        if piece:
            piece_row, piece_column = piece.row, piece.column

            if piece.piece_name == 'PAWN':
                if piece.player == '1':
                    axis_change = -1
                    en_passant_row = 3
                elif piece.player == '2':
                    axis_change = 1
                    en_passant_row = 4
                else:
                    axis_change = 0
                    en_passant_row = -1

                # regular movement
                check_next = self._check_valid_positions(board_position, piece_row + axis_change, piece_column, False)

                if check_next and not piece.moved:
                    self._check_valid_positions(board_position,piece_row + axis_change * 2, piece_column, False)
                
                # check diagonally
                self._check_valid_positions(board_position, piece_row + axis_change, piece_column - axis_change, must_eat = True)
                self._check_valid_positions(board_position, piece_row + axis_change, piece_column + axis_change, must_eat = True)

                # Fucking En passant
                # if a pawn is located at en passant row
                if piece_row == en_passant_row:
                    # get row & column for left/right
                    row, column = piece_row, piece_column - axis_change

                    # check we are not out of bound
                    if (row >= 0 and row < Config.BOARD_SIZE) and (column >= 0 and column < Config.BOARD_SIZE):
                        # get other board position
                        other_board_position:BoardPosition = self.board_positions[row, column]

                        # check if there is a pawn at the left/right that has pawn_double_move flag, if yes, mark place as valid
                        if other_board_position.piece and other_board_position.piece.pawn_double_move:
                            self._check_valid_positions(board_position, row + axis_change, column)

                    
                    # get row & column for other side
                    row, column = piece_row, piece_column + axis_change

                    # check we are not out of bound
                    if (row >= 0 and row < Config.BOARD_SIZE) and (column >= 0 and column < Config.BOARD_SIZE):
                        # get other board position
                        other_board_position:BoardPosition = self.board_positions[row, column]

                        # check if there is a pawn at the left/right that has pawn_double_move flag, if yes, mark place as valid
                        if other_board_position.piece and other_board_position.piece.pawn_double_move:
                            self._check_valid_positions(board_position, row + axis_change, column)

            elif piece.piece_name == 'ROOK':
                self._check_continuous(board_position, 1, 0)
                self._check_continuous(board_position, -1, 0)

                self._check_continuous(board_position, 0, 1)
                self._check_continuous(board_position, 0, -1)
            elif piece.piece_name == 'KNIGHT':
                check_next = self._check_valid_positions(board_position, piece_row + 2, piece_column + 1)
                check_next = self._check_valid_positions(board_position, piece_row + 2, piece_column - 1)

                check_next = self._check_valid_positions(board_position, piece_row - 2, piece_column + 1)
                check_next = self._check_valid_positions(board_position, piece_row - 2, piece_column - 1)
                
                check_next = self._check_valid_positions(board_position, piece_row + 1, piece_column + 2)
                check_next = self._check_valid_positions(board_position, piece_row - 1, piece_column + 2)
                
                check_next = self._check_valid_positions(board_position, piece_row + 1, piece_column - 2)
                check_next = self._check_valid_positions(board_position, piece_row - 1, piece_column - 2)
            elif piece.piece_name == 'BISHOP':
                self._check_continuous(board_position, 1, 1)
                self._check_continuous(board_position, 1, -1)

                self._check_continuous(board_position, -1, 1)
                self._check_continuous(board_position, -1, -1)
            elif piece.piece_name == 'QUEEN':
                self._check_continuous(board_position, 1, 0)
                self._check_continuous(board_position, -1, 0)

                self._check_continuous(board_position, 0, 1)
                self._check_continuous(board_position, 0, -1)

                self._check_continuous(board_position, 1, 1)
                self._check_continuous(board_position, 1, -1)

                self._check_continuous(board_position, -1, 1)
                self._check_continuous(board_position, -1, -1)
            elif piece.piece_name == 'KING':
                check_next = self._check_valid_positions(board_position, piece_row + 1, piece_column)
                check_next = self._check_valid_positions(board_position, piece_row - 1, piece_column)
                
                check_next = self._check_valid_positions(board_position, piece_row, piece_column + 1)
                check_next = self._check_valid_positions(board_position, piece_row, piece_column - 1)
                
                check_next = self._check_valid_positions(board_position, piece_row + 1, piece_column + 1)
                check_next = self._check_valid_positions(board_position, piece_row + 1, piece_column - 1)
                
                check_next = self._check_valid_positions(board_position, piece_row - 1, piece_column + 1)
                check_next = self._check_valid_positions(board_position, piece_row - 1, piece_column - 1)

                # Castling
                if not piece.moved:
                    self._check_continuous(board_position, 0, 1, True)
                    self._check_continuous(board_position, 0, -1, True)

                # TODO: Game over
            else:
                pass

    # TODO: change return type to BoardPosition, not Boolean
    def _check_valid_positions(self, board_position:'BoardPosition', row, column, can_eat:bool = True, must_eat = False, castling = False) -> bool:
        if (row >= 0 and row < Config.BOARD_SIZE) and (column >= 0 and column < Config.BOARD_SIZE):
            other_board_position:BoardPosition = self.board_positions[row, column]

            if castling:
                if (column == 0 or column == 7) and board_position.piece.player == other_board_position.piece.player and other_board_position.piece.piece_name == 'ROOK' and not other_board_position.piece.moved:
                    other_board_position.valid = True
                    self.valid_positions[row, column] = other_board_position

                    return False
                elif other_board_position.piece:
                    return False
                else:
                    return True
            elif other_board_position.piece and other_board_position.piece.player == board_position.piece.player:
                # stop when your own piece blocks the way
                return False
            elif other_board_position.piece and other_board_position.piece.player != board_position.piece.player:
                if can_eat:
                    # make the other position valid
                    other_board_position.valid = True
                    self.valid_positions[row, column] = other_board_position
                # stop after because the piece will block the way
                return False
            else:
                # otherwise, it's empty
                if must_eat:
                    return False,
                else:
                    other_board_position.valid = True
                    self.valid_positions[row, column] = other_board_position
                    return True
        else:
            return False

    def _check_continuous(self, board_position:'BoardPosition', row_change:int, column_change:int, castling = False):
        piece_row, piece_column = board_position.piece.row, board_position.piece.column

        # define variables
        check_next = True
        row, column = piece_row + row_change, piece_column + column_change
        # while check next is true
        while check_next:
            # update check_next
            check_next = self._check_valid_positions(board_position, row, column, castling=castling)
            # update row & column
            row, column = row + row_change, column + column_change

    def get_default_piece(self, row:int, column:int, piece_position:Point):
        # player 2 main pieces
        if row == 0 and column == 0:
            return Piece('Rook', '2', piece_position, row, column)
        elif row == 0 and column == 1:
            return Piece('Knight', '2', piece_position, row, column)
        elif row == 0 and column == 2:
            return Piece('Bishop', '2', piece_position, row, column)
        elif row == 0 and column == 3:
            return Piece('Queen', '2', piece_position, row, column)
        elif row == 0 and column == 4:
            return Piece('King', '2', piece_position, row, column)
        elif row == 0 and column == 5:
            return Piece('Bishop', '2', piece_position, row, column)
        elif row == 0 and column == 6:
            return Piece('Knight', '2', piece_position, row, column)
        elif row == 0 and column == 7:
            return Piece('Rook', '2', piece_position, row, column)
        
        # player 2 pawns
        elif row == 1 and column == 0:
            return Piece('Pawn', '2', piece_position, row, column)
        elif row == 1 and column == 1:
            return Piece('Pawn', '2', piece_position, row, column)
        elif row == 1 and column == 2:
            return Piece('Pawn', '2', piece_position, row, column)
        elif row == 1 and column == 3:
            return Piece('Pawn', '2', piece_position, row, column)
        elif row == 1 and column == 4:
            return Piece('Pawn', '2', piece_position, row, column)
        elif row == 1 and column == 5:
            return Piece('Pawn', '2', piece_position, row, column)
        elif row == 1 and column == 6:
            return Piece('Pawn', '2', piece_position, row, column)
        elif row == 1 and column == 7:
            return Piece('Pawn', '2', piece_position, row, column)
        
        # player 1 main pieces
        if row == 7 and column == 0:
            return Piece('Rook', '1', piece_position, row, column)
        elif row == 7 and column == 1:
            return Piece('Knight', '1', piece_position, row, column)
        elif row == 7 and column == 2:
            return Piece('Bishop', '1', piece_position, row, column)
        elif row == 7 and column == 3:
            return Piece('Queen', '1', piece_position, row, column)
        elif row == 7 and column == 4:
            return Piece('King', '1', piece_position, row, column)
        elif row == 7 and column == 5:
            return Piece('Bishop', '1', piece_position, row, column)
        elif row == 7 and column == 6:
            return Piece('Knight', '1', piece_position, row, column)
        elif row == 7 and column == 7:
            return Piece('Rook', '1', piece_position, row, column)
        
        # player 1 pawns
        elif row == 6 and column == 0:
            return Piece('Pawn', '1', piece_position, row, column)
        elif row == 6 and column == 1:
            return Piece('Pawn', '1', piece_position, row, column)
        elif row == 6 and column == 2:
            return Piece('Pawn', '1', piece_position, row, column)
        elif row == 6 and column == 3:
            return Piece('Pawn', '1', piece_position, row, column)
        elif row == 6 and column == 4:
            return Piece('Pawn', '1', piece_position, row, column)
        elif row == 6 and column == 5:
            return Piece('Pawn', '1', piece_position, row, column)
        elif row == 6 and column == 6:
            return Piece('Pawn', '1', piece_position, row, column)
        elif row == 6 and column == 7:
            return Piece('Pawn', '1', piece_position, row, column)
        
        # otherwise return None
        else:
            return None

