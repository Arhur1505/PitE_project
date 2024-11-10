import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SKY_COLOR
from src.car import Car
from src.terrain import Terrain

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hill Climb Racing")
        self.clock = pygame.time.Clock()
        self.running = True
        self.car = Car(100, SCREEN_HEIGHT - 200)
        self.terrain = Terrain()
        self.camera_x = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        self.car.handle_input()

    def update(self):
        self.car.update(self.terrain)
        self.camera_x = self.car.x - 100

    def draw(self):
        self.screen.fill(SKY_COLOR)
        self.terrain.draw(self.screen, self.camera_x)
        self.car.draw(self.screen, self.camera_x)
        pygame.display.flip()
