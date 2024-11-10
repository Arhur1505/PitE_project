import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_COLOR

class Terrain:
    def __init__(self):
        self.points = self.generate_terrain()

    def generate_terrain(self):
        terrain = []
        x = 0
        while x < SCREEN_WIDTH * 5:
            y = SCREEN_HEIGHT - random.randint(100, 300)
            terrain.append((x, y))
            x += random.randint(50, 150)
        return terrain

    def get_ground_y(self, x):
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            if x1 <= x <= x2:
                t = (x - x1) / (x2 - x1)
                y = y1 + t * (y2 - y1)
                return y
        return SCREEN_HEIGHT

    def draw(self, surface, camera_x):
        points = []
        for x, y in self.points:
            points.append((x - camera_x, y))
        pygame.draw.lines(surface, GROUND_COLOR, False, points, 5)
