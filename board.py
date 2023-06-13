from __future__ import annotations
from typing import TYPE_CHECKING

from pieces import Piece
from constants import Colour, PieceType, MoveType, BOARD_WIDTH, BOARD_HEIGHT, PIECE_TO_STRING, STRING_TO_PIECE, RANKS, FILES

if TYPE_CHECKING:
    from pieces import Piece, Move


class Board:
    def __init__(self, width: int = BOARD_WIDTH, height: int = BOARD_HEIGHT) -> None:
        self.width = width
        self.height = height

        self.pieces = {Colour.WHITE:[], Colour.BLACK:[]}
        self.board = self.create_empty_board()

        self.current_turn = Colour.WHITE
        self.opponent_turn = Colour.BLACK
        self.enpassant_target = (-1,-1,None)
        self.castling_rights = {Colour.WHITE:[False,False], Colour.BLACK:[False,False]}
        self.half_moves = 0
        self.full_moves = 1

    def create_empty_board(self) -> list[None]:
        return [[None for x in range(self.width)] for y in range(self.height)]

    def place_initial_piece(self, piece_type: PieceType, colour: Colour, x: int, y: int) -> None:
        if not self.inside_board(x, y):
            print(f"Error: {piece_type.name} cannot be placed outside board.")
            return
        elif self.get_piece(x, y) is not None:
            print(f"Error: {piece_type.name} cannot be placed ontop of another piece.")
            return

        new_piece = Piece(piece_type, colour, x, y, True)
        if new_piece.piece_type == PieceType.KING:
            self.pieces[colour].insert(0, new_piece)
        else:
            self.pieces[colour].append(new_piece)

        self.set_piece(x, y, new_piece)

    def get_piece(self, x: int, y: int) -> Piece:
        return self.board[y][x]

    def set_piece(self, x: int, y: int, piece: Piece) -> None:
        self.board[y][x] = piece

    def inside_board(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_other_turn(self, turn: Colour) -> Colour:
        if turn == Colour.WHITE: return Colour.BLACK
        elif turn == Colour.BLACK: return Colour.WHITE

    def switch_turn(self) -> None:
        self.opponent_turn = self.current_turn
        self.current_turn = self.get_other_turn(self.current_turn)

    def update_full_moves(self) -> None:
        if self.current_turn == Colour.BLACK:
            self.full_moves += 1

    def update_half_moves(self, move: Move) -> None:
        if move.piece.piece_type == PieceType.PAWN or move.move_type == MoveType.CAPTURE:
            self.half_moves = 0
        elif self.current_turn == Colour.BLACK:
            self.half_moves += 1

    def load_FEN(self, fen_string: str) -> None:
        self.pieces = {Colour.WHITE:[], Colour.BLACK:[]}
        self.board = self.create_empty_board()
        self.current_turn = Colour.WHITE
        self.opponent_turn = Colour.BLACK
        self.enpassant_target = (-1,-1,None)
        self.castling_rights = {Colour.WHITE:[False,False], Colour.BLACK:[False,False]}
        self.half_moves = 0
        self.full_moves = 1

        try:
            board, turn, castling, en_passant, half_moves, full_moves = fen_string.split(' ')
        except:
            print('Error: Invalid FEN string')
            return

        x = 0
        y = 0
        for char in board:
            if char == '/':
                y += 1
                x = 0
            elif char.lower() in STRING_TO_PIECE:
                # place piece
                piece_type = STRING_TO_PIECE[char.lower()]
                colour = Colour.WHITE if char.isupper() else Colour.BLACK
                self.place_initial_piece(piece_type, colour, x, y)

                x += 1
            else:
                # number to skip
                x += int(char)

        # Set turn
        if turn == 'w':
            self.current_turn = Colour.WHITE
            self.opponent_turn = Colour.BLACK
        else:
            self.current_turn = Colour.BLACK
            self.opponent_turn = Colour.WHITE

        # Set Castling
        # TODO say in invalid fen string -> king moved, rook not there
        for char in castling:
            if char == 'K':
                self.castling_rights[Colour.WHITE][0] = True
            if char == 'Q':
                self.castling_rights[Colour.WHITE][1] = True
            if char == 'k':
                self.castling_rights[Colour.BLACK][0] = True
            if char == 'q':
                self.castling_rights[Colour.BLACK][1] = True

        # Set en_passant
        # TODO: Say if invalid -> target pawn not in spot supposed to be
        x = -1
        y = -1
        for char in en_passant:
            if char in RANKS:
                x = RANKS.index(char)
            elif char in FILES:
                y = 8 - int(char)

        if x != -1 and y != -1:
            direction = 1 if self.current_turn == Colour.WHITE else -1
            target = self.get_piece(x, y+direction)
            self.enpassant_target = (x,y,target)

        self.half_moves = int(half_moves)
        self.full_moves = int(full_moves)

    def get_FEN(self) -> str:
        fen = ""

        # Board
        empty_count = 0
        for y in range(self.height):
            for x in range(self.width):
                piece = self.get_piece(x, y)
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += str(empty_count)
                        empty_count = 0
                    notation = PIECE_TO_STRING[piece.piece_type]
                    if piece.colour == Colour.WHITE:
                        notation = notation.upper()
                    fen += notation
            if empty_count > 0:
                fen += str(empty_count)
                empty_count = 0
            if y < self.height - 1:
                fen +=  '/'

        # Turn
        turn = 'w' if self.current_turn == Colour.WHITE else 'b'
        fen += f" {turn}"

        # Castling
        castling = ""
        if self.castling_rights[Colour.WHITE][0]:
            castling += 'K'
        if self.castling_rights[Colour.WHITE][1]:
            castling += 'Q'
        if self.castling_rights[Colour.BLACK][0]:
            castling += 'k'
        if self.castling_rights[Colour.BLACK][0]:
            castling += 'q'
        if castling == "":
            castling = '-'

        fen += f" {castling}"

        # En_passant target
        en_passant = ""
        if self.enpassant_target[2] is None:
            en_passant = "-"
        else:
            en_passant += RANKS[self.enpassant_target[0]]
            en_passant += str(self.height-self.enpassant_target[1])

        fen += f" {en_passant}"

        fen += f" {self.half_moves}"
        fen += f" {self.full_moves}"

        return fen
