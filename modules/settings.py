import pygame

pygame.init()
WIDTH, HEIGHT = 800, 400
MAP_MIN_Y = -5
END_X = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_COLOR = (100, 200, 100)
CAR_COLOR = (200, 0, 0)
WHEEL_COLOR = (0, 0, 0)
DRIVER_COLOR = (50, 50, 200)