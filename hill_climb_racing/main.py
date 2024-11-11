# main.py

import pygame
from src.game import Game

def main():
    pygame.init()
    game = Game(render_mode=True)  # Ustaw render_mode na True
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()
