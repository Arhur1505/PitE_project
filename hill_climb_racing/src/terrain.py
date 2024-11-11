# src/terrain.py

import pygame
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_COLOR

class Terrain:
    def __init__(self):
        self.points = self.generate_terrain()

    def generate_terrain(self):
        terrain = []
        x = 0
        y = SCREEN_HEIGHT - 200
        # Dodaj początkowy płaski odcinek
        terrain.append((x, y))
        x += 100
        terrain.append((x, y))
        # Reszta terenu generowana losowo
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

    def get_incline(self, x):
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            if x1 <= x <= x2:
                dx = x2 - x1
                dy = y2 - y1
                incline = math.degrees(math.atan2(dy, dx))
                return incline
        return 0

    def draw(self, surface, camera_x):
        points = []
        for px, py in self.points:
            points.append((px - camera_x, py))
        pygame.draw.lines(surface, GROUND_COLOR, False, points, 5)
