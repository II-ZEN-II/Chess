import pygame

from enum import Enum, auto
from string import ascii_letters

pygame.init()

# Don't change board size
BOARD_WIDTH = 8
BOARD_HEIGHT = 8
RANKS = [ascii_letters[i] for i in range(BOARD_WIDTH)]
FILES = [str(i) for i in range(BOARD_HEIGHT,0,-1)]

# Pygame Constants
SCREEN = pygame.display.Info()
SQUARE_SIZE = (min(SCREEN.current_w, SCREEN.current_h) - 100) // max(BOARD_WIDTH, BOARD_HEIGHT)
FPS = 0
WINDOW_RESOLUTION = (BOARD_WIDTH*SQUARE_SIZE, BOARD_HEIGHT*SQUARE_SIZE)
WINDOW_CAPTION = "CHESS"

# Asset constants
FONT_SIZE = SQUARE_SIZE//4
FONT_COLOUR = (255,255,255)
TEXT_OFFSET = SQUARE_SIZE//FONT_SIZE

LOAD_FILE = "games/load.txt"

class Colour(Enum):
    WHITE = auto()
    BLACK = auto()

class PieceType(Enum):
    PAWN = 0
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()

class MoveType(Enum):
    MOVE = 0
    CAPTURE = auto()
    DOUBLE_PUSH = auto()
    EN_PASSANT = auto()
    PROMOTION = auto()
    CASTLE_QUEEN_SIDE = auto()
    CASTLE_KING_SIDE = auto()

class GameStates(Enum):
    NOTHING = auto()
    CHECK = auto()
    STALEMATE = auto()
    CHECKMATE = auto()

# PIECE_VALUES = {
#     PieceType.PAWN: 1,
#     PieceType.KNIGHT: 3,
#     PieceType.BISHOP: 3,
#     PieceType.ROOK: 5,
#     PieceType.QUEEN: 9,
#     PieceType.KING: 999
# }

PIECE_TO_STRING = {
    PieceType.PAWN: 'p',
    PieceType.KNIGHT: 'n',
    PieceType.BISHOP: 'b',
    PieceType.ROOK: 'r',
    PieceType.QUEEN: 'q',
    PieceType.KING: 'k'
}

STRING_TO_PIECE = {
    'p' : PieceType.PAWN,
    'n' : PieceType.KNIGHT,
    'b' : PieceType.BISHOP,
    'r' : PieceType.ROOK,
    'q' : PieceType.QUEEN,
    'k' : PieceType.KING
}
