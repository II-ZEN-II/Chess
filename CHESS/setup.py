from objects import *
from constants import *

def default_setup():
    game = Game(BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE, WHITE, [True, True], [True, True])
    game.set_piece(0,1,Pawn(BLACK))
    game.set_piece(1,1,Pawn(BLACK))
    game.set_piece(2,1,Pawn(BLACK))
    game.set_piece(3,1,Pawn(BLACK))
    game.set_piece(4,1,Pawn(BLACK))
    game.set_piece(5,1,Pawn(BLACK))
    game.set_piece(6,1,Pawn(BLACK))
    game.set_piece(7,1,Pawn(BLACK))

    game.set_piece(0,0,Rook(BLACK))
    game.set_piece(1,0,Knight(BLACK))
    game.set_piece(2,0,Bishop(BLACK))
    game.set_piece(3,0,Queen(BLACK))
    game.set_piece(4,0,King(BLACK))
    game.set_piece(5,0,Bishop(BLACK))
    game.set_piece(6,0,Knight(BLACK))
    game.set_piece(7,0,Rook(BLACK))

    game.set_piece(0,6,Pawn(WHITE))
    game.set_piece(1,6,Pawn(WHITE))
    game.set_piece(2,6,Pawn(WHITE))
    game.set_piece(3,6,Pawn(WHITE))
    game.set_piece(4,6,Pawn(WHITE))
    game.set_piece(5,6,Pawn(WHITE))
    game.set_piece(6,6,Pawn(WHITE))
    game.set_piece(7,6,Pawn(WHITE))

    game.set_piece(0,7,Rook(WHITE))
    game.set_piece(1,7,Knight(WHITE))
    game.set_piece(2,7,Bishop(WHITE))
    game.set_piece(3,7,Queen(WHITE))
    game.set_piece(4,7,King(WHITE))
    game.set_piece(5,7,Bishop(WHITE))
    game.set_piece(6,7,Knight(WHITE))
    game.set_piece(7,7,Rook(WHITE))
    return game
