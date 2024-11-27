import pygame
from src.game import Game

def main():
    pygame.init()
    game = Game(render_mode=True)
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()