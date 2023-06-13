from board import Board
from engine import Engine

def main():
    # https://www.chessprogramming.org/Perft_Results#Initial_Position -> depth of 1
    debug_accuracy("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 20)
    debug_accuracy("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 0", 48)
    debug_accuracy("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 0", 14)
    # Innacurate due to promotion only to queen -> off by three due to underpromotion to knight, bishop and rook
    debug_accuracy("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 44)
    debug_accuracy("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", 46)

    # https://gist.github.com/peterellisjones/8c46c28141c162d1d8a0f0badbc9cff9
    debug_accuracy("r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2", 8)
    debug_accuracy("8/8/8/2k5/2pP4/8/B7/4K3 b - d3 0 3", 8)
    debug_accuracy("r1bqkbnr/pppppppp/n7/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 2 2", 19)
    debug_accuracy("r3k2r/p1pp1pb1/bn2Qnp1/2qPN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQkq - 3 2", 5)
    debug_accuracy("2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQ - 3 2", 44)
    debug_accuracy("rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w KQ - 3 9", 39)
    # Innacurate due to promotion only to queen -> off by six due to underpromotion to knight, bishop and rook as pawn can promote 2 ways
    debug_accuracy("2r5/3pk3/8/2P5/8/2K5/8/8 w - - 5 4", 9)


def debug_accuracy(fen_string: str, legal_moves: int) -> None:
    print()
    print(fen_string)
    output = number_of_moves(fen_string)
    print(f"expected: {legal_moves}, output: {output}")
    print(f"correct: {output == legal_moves}")

def number_of_moves(fen_string: str) -> int:
    board = Board()
    board.load_FEN(fen_string)
    engine = Engine(board)

    current_turn_pieces = board.pieces[board.current_turn]
    opponent_pieces = board.pieces[board.opponent_turn]

    in_check = engine.is_attacked(current_turn_pieces[0].x, current_turn_pieces[0].y, opponent_pieces)

    pseudo_legal_moves = engine.get_pseudo_legal_moves(current_turn_pieces)
    legal_moves = engine.get_legal_moves(in_check, pseudo_legal_moves, current_turn_pieces[0], opponent_pieces)

    return len(legal_moves)

if __name__ == "__main__":
    main()
