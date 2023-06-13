import pygame

from tools.spritesheet import SpriteSheet
from constants import SQUARE_SIZE, WINDOW_RESOLUTION, WINDOW_CAPTION, FONT_SIZE

# Setup pygame
pygame.init()
window = pygame.display.set_mode(WINDOW_RESOLUTION)
pygame.display.set_caption(WINDOW_CAPTION, WINDOW_CAPTION)
clock = pygame.time.Clock()

# Load all fonts
FONT = pygame.font.Font("assets/fonts/DIN Condensed Bold.ttf", FONT_SIZE)

# Load all sprites
PIECE_SPRITES = SpriteSheet("assets/sprites/custom-pieces.png", (150,150), (SQUARE_SIZE, SQUARE_SIZE), True).slice_sheet()
SQUARE_SPRITES = SpriteSheet("assets/sprites/squares.png", (100,100), (SQUARE_SIZE, SQUARE_SIZE), True).slice_sheet()
SYMBOL_SPRITES = SpriteSheet("assets/sprites/symbols.png", (100,100), (SQUARE_SIZE, SQUARE_SIZE), True).slice_sheet()

# Load all sounds

pygame.display.set_icon(PIECE_SPRITES[1])
