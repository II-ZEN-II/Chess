from __future__ import annotations
from typing import TYPE_CHECKING

from constants import Colour, PieceType, MoveType, GameStates
from pieces import get_moves

if TYPE_CHECKING:
    from board import Board
    from pieces import Move, Piece


class Engine:
    def __init__(self, board: Board) -> None:
        self.board = board

    def get_pseudo_legal_moves(self, current_turn_pieces: list[Piece]) -> list[Move]:
        pseudo_legal_moves = []

        for piece in current_turn_pieces:
            if not piece.alive:
                continue
            pseudo_legal_moves += get_moves(self.board, piece)

        return pseudo_legal_moves

    def get_legal_moves(self, in_check: bool, pseudo_legal_moves: list[Move], current_turn_king: Piece, opponent_pieces: list[Piece]) -> list[Move]:
        legal_moves = []

        for move in pseudo_legal_moves:
            # stops castling out of or through check
            if move.move_type == MoveType.CASTLE_KING_SIDE:
                if in_check or self.is_attacked(current_turn_king.x+1, current_turn_king.y, opponent_pieces):
                    continue
            elif move.move_type == MoveType.CASTLE_QUEEN_SIDE:
                if in_check or self.is_attacked(current_turn_king.x-1, current_turn_king.y, opponent_pieces):
                    continue

            # checks if king is attacked after making move -> illegal
            self.perform_move(move)

            if not self.is_attacked(current_turn_king.x, current_turn_king.y, opponent_pieces):
                legal_moves.append(move)

            self.unperform_move(move)

        return legal_moves

    def is_gameover(self, in_check: bool, number_of_valid_moves: int) -> GameStates:
        if self.board.half_moves >= 50:
            print("STALEMATE! 50 move rule")
            return GameStates.STALEMATE

        if number_of_valid_moves == 0:
            if in_check:
                print(f"CHECKMATE! {self.board.opponent_turn.name} WINS")
                return GameStates.CHECKMATE
            else:
                print("STALEMATE!")
                return GameStates.STALEMATE
        if in_check:
            print('CHECK!')
            return GameStates.CHECK
        return GameStates.NOTHING

    def perform_move(self, move: Move) -> None:
        # perform capture
        if move.target is not None:
            move.target.alive = False
            self.board.set_piece(move.target.x, move.target.y, None)

        # perform promotion
        if move.move_type == MoveType.PROMOTION:
            # TODO: Add promotion to other pieces -> link to UI
            move.piece.piece_type = PieceType.QUEEN

        # move piece
        move.piece.x = move.target_x
        move.piece.y = move.target_y
        self.board.set_piece(move.target_x, move.target_y, move.piece)
        self.board.set_piece(move.piece_x, move.piece_y, None)

    def unperform_move(self, move: Move) -> None:
        # unmove piece
        move.piece.x = move.piece_x
        move.piece.y = move.piece_y
        self.board.set_piece(move.target_x, move.target_y, None)
        self.board.set_piece(move.piece_x, move.piece_y, move.piece)

        # unperform promotion
        if move.move_type == MoveType.PROMOTION:
            move.piece.piece_type = PieceType.PAWN

        # unperform capture
        if move.target is not None:
            move.target.alive = True
            self.board.set_piece(move.target.x, move.target.y, move.target)

    def is_attacked(self, x: int, y: int, opponent_pieces: list[Piece]) -> bool:
        for opponent_piece in opponent_pieces:
            if not opponent_piece.alive:
                continue
            for move in get_moves(self.board, opponent_piece):
                if x == move.target_x and y == move.target_y:
                    return True
        return False

    def set_enpassant_target(self, move: Move) -> None:
        if move.move_type == MoveType.DOUBLE_PUSH:
            direction = -1 if move.piece.colour == Colour.WHITE else 1
            self.board.enpassant_target = (move.target_x,move.target_y-direction,move.piece)
        else:
            self.board.enpassant_target = (-1,-1,None)

    def perform_castle(self, move: Move) -> None:
        # king has already moved two spaces so just need to jump rook
        if move.move_type == MoveType.CASTLE_KING_SIDE:
            direction = -1
            if move.piece.colour == Colour.WHITE:
                rook = self.board.get_piece(7, 7)
            else:
                rook = self.board.get_piece(7, 0)
        elif move.move_type == MoveType.CASTLE_QUEEN_SIDE:
            direction = 1
            if move.piece.colour == Colour.WHITE:
                rook = self.board.get_piece(0, 7)
            else:
                rook = self.board.get_piece(0, 0)
        else:
            # haven't castled
            return

        self.board.set_piece(rook.x, rook.y, None)
        self.board.set_piece(move.piece.x+direction, move.piece.y, rook)
        rook.x = move.piece.x+direction
        rook.y = move.piece.y

    def update_castling_rights(self, move: Move) -> None:
        # can't castle if moved king
        if move.piece.piece_type == PieceType.KING or move.move_type == MoveType.CASTLE_KING_SIDE or move.move_type == MoveType.CASTLE_QUEEN_SIDE:
            self.board.castling_rights[move.piece.colour] = [False, False]

        # captured opponent's rook
        if move.target is not None and move.target.piece_type == PieceType.ROOK:
            # kingside rook captured
            if move.target_x == 7 and move.target_y == 7 or move.target_x == 7 and move.target_y == 0:
                self.board.castling_rights[move.target.colour][0] = False
            # queenside rook captured
            if move.target_x == 0 and move.target_y == 7 or move.target_x == 0 and move.target_y == 0:
                self.board.castling_rights[move.target.colour][1] = False

        # moved your rook
        if move.piece.piece_type == PieceType.ROOK:
            # kingside rook moved
            if move.piece_x == 7 and move.piece_y == 7 or move.piece_x == 7 and move.piece_y == 0:
                self.board.castling_rights[move.piece.colour][0] = False
            # queenside rook moved
            if move.piece_x == 0 and move.piece_y == 7 or move.piece_x == 0 and move.piece_y == 0:
                self.board.castling_rights[move.piece.colour][1] = False
