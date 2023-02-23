import pygame
from objects import *
from constants import *
from setup import *

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('CHESS')

    game = default_setup()
    player = Player(game)
    game.draw(screen)
    while True:
        #INPUT
        mouse_position = pygame.mouse.get_pos()
        is_mouse_down = False
        is_mouse_up = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()

                if event.key == pygame.K_SPACE:
                    game.switch_turn()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_mouse_down = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_mouse_up = True

        #UPDATE
        player.update(screen, mouse_position, is_mouse_down, is_mouse_up)

        clock.tick(FPS)
        pygame.display.flip()

def terminate():
    pygame.quit()
    raise SystemExit

if __name__ == '__main__':
    main()
