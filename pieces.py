from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from constants import Colour, PieceType, MoveType

if TYPE_CHECKING:
    from board import Board


@dataclass (slots=True)
class Move:
    move_type: MoveType
    piece: Piece
    piece_x: int
    piece_y: int
    target: Piece
    target_x: int
    target_y: int

@dataclass (slots=True)
class Piece:
    piece_type: PieceType
    colour: Colour
    x: int
    y: int
    alive: bool


def get_moves(board: Board, piece: Piece):
    match piece.piece_type:
        case PieceType.PAWN:
            return get_pawn_moves(board, piece)
        case PieceType.KNIGHT:
            return get_knight_moves(board, piece)
        case PieceType.BISHOP:
            return get_bishop_moves(board, piece)
        case PieceType.ROOK:
            return get_rook_moves(board, piece)
        case PieceType.QUEEN:
            return get_queen_moves(board, piece)
        case PieceType.KING:
            return get_king_moves(board, piece)

def get_pawn_moves(board: Board, piece: Piece) -> list[Move]:
    direction = -1 if piece.colour == Colour.WHITE else 1
    pseudo_legal_moves = []

    new_x = piece.x
    new_y = piece.y + direction

    is_promotion = new_y == board.height-1 or new_y == 0

    # forward one
    if board.inside_board(new_x, new_y) and board.get_piece(new_x, new_y) is None:
        # move
        pseudo_legal_moves.append(Move(MoveType.PROMOTION if is_promotion else MoveType.MOVE, piece, piece.x, piece.y, None, new_x, new_y))

        # forward two
        if piece.y == 1 or piece.y == board.height-2:
            if board.inside_board(new_x, new_y+direction) and board.get_piece(new_x, new_y+direction) is None:
                pseudo_legal_moves.append(Move(MoveType.DOUBLE_PUSH, piece, piece.x, piece.y, None, new_x, new_y+direction))

    # captures
    for side in (-1,1):
        new_x = piece.x + (direction * side)
        if board.inside_board(new_x, new_y):
            target = board.get_piece(new_x, new_y)
            if target is not None and target.colour != piece.colour:
                pseudo_legal_moves.append(Move(MoveType.PROMOTION if is_promotion else MoveType.CAPTURE, piece, piece.x, piece.y, target, new_x, new_y))

            if new_x == board.enpassant_target[0] and new_y == board.enpassant_target[1] and board.enpassant_target[2].colour != piece.colour:
                pseudo_legal_moves.append(Move(MoveType.EN_PASSANT, piece, piece.x, piece.y, board.enpassant_target[2], new_x, new_y))

    return pseudo_legal_moves

def get_knight_moves(board: Board, piece: Piece) -> list[Move]:
    moves = ((2,-1),(2,1),(-1,-2),(1,-2),(-2,-1),(-2,1),(1,2),(-1,2))
    return get_set_moves(board, moves, piece)

def get_bishop_moves(board: Board, piece: Piece) -> list[Move]:
    sliding_moves = ((-1,-1),(-1,1),(1,-1),(1,1))
    return get_sliding_moves(board, sliding_moves, piece)

def get_rook_moves(board: Board, piece: Piece) -> list[Move]:
    sliding_moves = ((0,-1),(-1,0),(1,0),(0,1))
    return get_sliding_moves(board, sliding_moves, piece)

def get_queen_moves(board: Board, piece: Piece) -> list[Move]:
    sliding_moves = ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1))
    return get_sliding_moves(board, sliding_moves, piece)

def get_king_moves(board: Board, piece: Piece) -> list[Move]:
    moves = ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1))
    castling_moves = []

    new_x = piece.x
    # castle kingside
    if board.castling_rights[piece.colour][0]:
        empty = True
        for i in range(2):
            new_x += 1
            if not board.inside_board(new_x, piece.y) or board.get_piece(new_x, piece.y) is not None:
                empty = False
                break
        if empty:
            castling_moves.append(Move(MoveType.CASTLE_KING_SIDE, piece, piece.x, piece.y, None, new_x, piece.y))

    new_x = piece.x
    # castle queenside
    if board.castling_rights[piece.colour][1]:
        empty = True
        for i in range(3):
            new_x -= 1
            if not board.inside_board(new_x, piece.y) or board.get_piece(new_x, piece.y) is not None:
                empty = False
                break
        if empty:
            castling_moves.append(Move(MoveType.CASTLE_QUEEN_SIDE, piece, piece.x, piece.y, None, new_x+1, piece.y))

    return get_set_moves(board, moves, piece) + castling_moves

def get_sliding_moves(board: Board, sliding_moves: tuple[tuple], piece: Piece) -> list[Move]:
    pseudo_legal_moves = []

    for direction in sliding_moves:
        new_x = piece.x + direction[0]
        new_y = piece.y + direction[1]

        # moves
        while board.inside_board(new_x, new_y) and board.get_piece(new_x, new_y) is None:
            pseudo_legal_moves.append(Move(MoveType.MOVE, piece, piece.x, piece.y, None, new_x, new_y))
            new_x += direction[0]
            new_y += direction[1]

        # captures
        if not board.inside_board(new_x, new_y):
            continue

        target = board.get_piece(new_x, new_y)
        if target.colour != piece.colour:
            pseudo_legal_moves.append(Move(MoveType.CAPTURE, piece, piece.x, piece.y, target, new_x, new_y))

    return pseudo_legal_moves

def get_set_moves(board: Board, moves: tuple[tuple], piece: Piece) -> list[Move]:
    pseudo_legal_moves = []

    for move in moves:
        new_x = piece.x + move[0]
        new_y = piece.y + move[1]

        # moves and captures
        if not board.inside_board(new_x, new_y):
            continue

        target = board.get_piece(new_x, new_y)

        if target is None:
            pseudo_legal_moves.append(Move(MoveType.MOVE, piece, piece.x, piece.y, target, new_x, new_y))
        elif target.colour != piece.colour:
            pseudo_legal_moves.append(Move(MoveType.CAPTURE, piece, piece.x, piece.y, target, new_x, new_y))

    return pseudo_legal_moves
