from __future__ import annotations
from typing import TYPE_CHECKING
import random
import pygame

from constants import SQUARE_SIZE, BOARD_WIDTH, BOARD_HEIGHT, RANKS, FILES, FONT_SIZE, FONT_COLOUR, TEXT_OFFSET, FPS, LOAD_FILE, Colour, GameStates, PieceType
from setup import window, clock, FONT, PIECE_SPRITES, SQUARE_SPRITES, SYMBOL_SPRITES
from engine import Engine
from board import Board

if TYPE_CHECKING:
    from pieces import Move


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.engine = Engine(self.board)

        # Game variables
        self.gameover = False

        self.current_turn_pieces = []
        self.opponent_pieces = []
        self.in_check = False
        self.legal_moves = False

        # Move history
        self.board_history = self.load_game(LOAD_FILE)
        self.position_index = 0

        # Move selection variables
        self.selected_square = None
        self.last_move = None

        # Setup game
        self.board.load_FEN(self.board_history[self.position_index])
        self.start_new_turn()

    def run(self) -> None:
        self.render_board()
        while True:
            # Input
            mouse_position = pygame.mouse.get_pos()
            position = screen_to_square(mouse_position)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        terminate()
                    if event.key == pygame.K_SPACE:
                        # perform random legal move
                        if not self.gameover:
                            self.deselect()
                            self.perform_turn(random.choice(self.legal_moves))
                            self.render_board()
                    if event.key == pygame.K_RIGHT:
                        self.position_index = min(len(self.board_history)-1, self.position_index+1)
                        self.shift_position()
                    if event.key == pygame.K_LEFT:
                        self.position_index = max(0, self.position_index-1)
                        self.shift_position()
                    if event.key == pygame.K_DOWN:
                        self.position_index = 0
                        self.shift_position()
                    if event.key == pygame.K_UP:
                        self.position_index = len(self.board_history)-1
                        self.shift_position()
                    if event.key == pygame.K_s:
                        self.save_game(LOAD_FILE)
                        print(f"Saved as file to load! {LOAD_FILE}")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.selected_square == None:
                        self.select(position)
                    elif position == self.selected_square:
                        self.deselect()
                    elif self.get_selected_move(self.selected_square, position) is None:
                        self.deselect()
                        self.select(position)
                    self.render_board()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.selected_square is not None:
                        selected_move = self.get_selected_move(self.selected_square, position)
                        if position != self.selected_square and selected_move is not None:
                            self.deselect()
                            self.perform_turn(selected_move)
                    self.render_board()

            # Process
            pygame.display.set_caption(f"FPS: {int(clock.get_fps())}/{FPS}")

            # Render
            # only renders when input is made :))

            pygame.display.flip()
            clock.tick(FPS)

    def shift_position(self) -> None:
        self.board.load_FEN(self.board_history[self.position_index])
        self.gameover = False
        self.selected_square = None
        self.last_move = None
        self.start_new_turn()
        self.render_board()

    def get_selected_move(self, piece_position: tuple[int], target_position: tuple[int]) -> Move:
        for move in self.legal_moves:
            if (move.piece_x == piece_position[0] and move.piece_y == piece_position[1] and
                move.target_x == target_position[0] and move.target_y == target_position[1]):
                return move
        return None

    def select(self, position: tuple[int]) -> None:
        self.selected_square = position

    def deselect(self) -> None:
        self.selected_square = None

    def start_new_turn(self) -> None:
        self.current_turn_pieces = self.board.pieces[self.board.current_turn]
        self.opponent_pieces = self.board.pieces[self.board.opponent_turn]

        self.in_check = self.engine.is_attacked(self.current_turn_pieces[0].x, self.current_turn_pieces[0].y, self.opponent_pieces)

        pseudo_legal_moves = self.engine.get_pseudo_legal_moves(self.current_turn_pieces)
        self.legal_moves = self.engine.get_legal_moves(self.in_check, pseudo_legal_moves, self.current_turn_pieces[0], self.opponent_pieces)

        game_state = self.engine.is_gameover(self.in_check, len(self.legal_moves))
        if game_state == GameStates.STALEMATE or game_state == GameStates.CHECKMATE:
            self.gameover = True
            self.legal_moves = []

    def perform_turn(self, selected_move: Move) -> None:
        if self.gameover:
            return

        self.last_move = selected_move
        self.engine.perform_move(selected_move)

        # *Irreversible* changes
        self.engine.set_enpassant_target(selected_move)
        self.engine.update_castling_rights(selected_move)
        self.engine.perform_castle(selected_move)

        self.board.update_full_moves()
        self.board.update_half_moves(selected_move)
        self.board.switch_turn()

        # backtracked and made different move
        if self.position_index != len(self.board_history)-1:
            self.board_history = self.board_history[:self.position_index+1]

        self.position_index += 1
        self.board_history.append(self.board.get_FEN())

        self.start_new_turn()

    def save_game(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            for i in range(self.position_index+1):
                file.write(self.board_history[i]+'\n')

    def load_game(self, file_path: str) -> str:
        history = []
        with open(file_path, "r") as file:
            for line in file.readlines():
                history.append(line.strip())
        return history

    def render_board(self) -> None:
        # Draw squares (white or black)
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                square_sprite = SQUARE_SPRITES[0] if (x+y) % 2 == 0 else SQUARE_SPRITES[1]
                window.blit(square_sprite, (x*SQUARE_SIZE, y*SQUARE_SIZE))

        # Draw board coordinates
        for x in range(BOARD_WIDTH):
            window.blit(FONT.render(RANKS[x], True, FONT_COLOUR), ((x)*SQUARE_SIZE+SQUARE_SIZE-FONT_SIZE/2, BOARD_HEIGHT*SQUARE_SIZE-FONT_SIZE))
        for y in range(BOARD_HEIGHT):
            window.blit(FONT.render(FILES[y], True, FONT_COLOUR), (TEXT_OFFSET, y*SQUARE_SIZE+TEXT_OFFSET))

        # Draw highlight squares
        if self.last_move is not None:
            window.blit(SQUARE_SPRITES[3], (self.last_move.piece_x*SQUARE_SIZE, self.last_move.piece_y*SQUARE_SIZE))
            window.blit(SQUARE_SPRITES[3], (self.last_move.target_x*SQUARE_SIZE, self.last_move.target_y*SQUARE_SIZE))
        if self.selected_square is not None:
            window.blit(SQUARE_SPRITES[2], (self.selected_square[0]*SQUARE_SIZE, self.selected_square[1]*SQUARE_SIZE))

        # Draw pieces on board
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                piece = self.board.get_piece(x, y)
                if piece is not None:
                    colour = 0 if piece.colour == Colour.WHITE else 6
                    piece_sprite = PIECE_SPRITES[piece.piece_type.value + colour]
                    window.blit(piece_sprite, (x*SQUARE_SIZE, y*SQUARE_SIZE))

        # Draw symbols for selected piece moves
        if self.selected_square is not None:
            for move in self.legal_moves:
                if move.piece_x == self.selected_square[0] and move.piece_y == self.selected_square[1]:
                    window.blit(SYMBOL_SPRITES[move.move_type.value], (move.target_x*SQUARE_SIZE, move.target_y*SQUARE_SIZE))

def screen_to_square(mouse_position) -> tuple[int]:
    return (int(mouse_position[0]/SQUARE_SIZE), int(mouse_position[1]/SQUARE_SIZE))

def terminate() -> None:
    pygame.quit()
    raise SystemExit
