from objects import *
from constants import *

translation = {
    'a' : 0,
    'b' : 1,
    'c' : 2,
    'd' : 3,
    'e' : 4,
    'f' : 5,
    'g' : 6,
    'h' : 7,
}

def default_setup():
    return parse_fen_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

def parse_fen_string(string):
    try:
        board, turn, castling_rights, en_passant, half_moves, full_moves = string.split(' ')
        turn = WHITE if turn == 'w' else BLACK
        white_castling_rights = [True if 'K' in castling_rights else False, True if 'Q' in castling_rights else False]
        black_castling_rights = [True if 'k' in castling_rights else False, True if 'q' in castling_rights else False]
        en_passant_target = None if en_passant == '-' else (translation[en_passant[0]],8-int(en_passant[1]))

        game = Game(BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE, turn, white_castling_rights, black_castling_rights, en_passant_target, int(half_moves), int(full_moves))

        x = 0
        y = 0
        for char in board:
            match char:
                case '/':
                    x = -1
                    y += 1
                case 'p': game.place_initial_piece(x,y,Pawn,BLACK)
                case 'P': game.place_initial_piece(x,y,Pawn,WHITE)
                case 'n': game.place_initial_piece(x,y,Knight,BLACK)
                case 'N': game.place_initial_piece(x,y,Knight,WHITE)
                case 'b': game.place_initial_piece(x,y,Bishop,BLACK)
                case 'B': game.place_initial_piece(x,y,Bishop,WHITE)
                case 'r': game.place_initial_piece(x,y,Rook,BLACK)
                case 'R': game.place_initial_piece(x,y,Rook,WHITE)
                case 'q': game.place_initial_piece(x,y,Queen,BLACK)
                case 'Q': game.place_initial_piece(x,y,Queen,WHITE)
                case 'k': game.place_initial_piece(x,y,King,BLACK)
                case 'K': game.place_initial_piece(x,y,King,WHITE)
                case other:
                    x += (int(other) - 1)
            x += 1
    except ValueError:
        print('Invalid FEN string')

    game.start_player_turn()

    return game


