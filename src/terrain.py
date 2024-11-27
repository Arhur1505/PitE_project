import pygame
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_COLOR

class Terrain:
    def __init__(self):
        self.points = self.generate_terrain()
        self.smooth_points = self.smooth_terrain()

    def generate_terrain(self):
        terrain = []
        x = 0
        y = SCREEN_HEIGHT - 200  # Startowa wysokość
        max_height_change = 50  # Maksymalna różnica wysokości między punktami
        max_x_gap = 100         # Maksymalna odległość w osi X między punktami

        # Dodaj początkowy płaski odcinek
        terrain.append((x, y))
        x += max_x_gap
        terrain.append((x, y))

        # Reszta terenu generowana losowo
        while x < SCREEN_WIDTH * 5:
            y_change = random.randint(-max_height_change, max_height_change)
            y = max(min(y + y_change, SCREEN_HEIGHT - 100), SCREEN_HEIGHT - 300)  # Ograniczenie wysokości
            x += random.randint(50, max_x_gap)  # Ograniczenie odległości w osi X
            terrain.append((x, y))

        return terrain

    def smooth_terrain(self):
        # Wygładzanie przy pomocy interpolacji Catmull-Rom
        smooth_points = []
        for i in range(len(self.points) - 1):
            p0 = self.points[i - 1] if i > 0 else self.points[i]
            p1 = self.points[i]
            p2 = self.points[i + 1]
            p3 = self.points[i + 2] if i + 2 < len(self.points) else self.points[i + 1]
            segment = self.catmull_rom(p0, p1, p2, p3, 20)
            smooth_points.extend(segment)
        return smooth_points

    def catmull_rom(self, p0, p1, p2, p3, num_points):
        """Interpolacja Catmull-Rom dla 4 punktów"""
        points = []
        for t in range(num_points):
            t /= num_points
            t2 = t * t
            t3 = t2 * t

            # Współczynniki Catmull-Rom
            f0 = -0.5 * t3 + t2 - 0.5 * t
            f1 = 1.5 * t3 - 2.5 * t2 + 1
            f2 = -1.5 * t3 + 2 * t2 + 0.5 * t
            f3 = 0.5 * t3 - 0.5 * t2

            # Obliczenie nowych współrzędnych
            x = f0 * p0[0] + f1 * p1[0] + f2 * p2[0] + f3 * p3[0]
            y = f0 * p0[1] + f1 * p1[1] + f2 * p2[1] + f3 * p3[1]
            points.append((x, y))
        return points

    def get_ground_y(self, x):
        for i in range(len(self.smooth_points) - 1):
            x1, y1 = self.smooth_points[i]
            x2, y2 = self.smooth_points[i + 1]
            if x1 <= x <= x2:
                t = (x - x1) / (x2 - x1)
                y = y1 + t * (y2 - y1)
                return y
        return SCREEN_HEIGHT

    def get_incline(self, x):
        for i in range(len(self.smooth_points) - 1):
            x1, y1 = self.smooth_points[i]
            x2, y2 = self.smooth_points[i + 1]
            if x1 <= x <= x2:
                dx = x2 - x1
                dy = y2 - y1
                incline = math.degrees(math.atan2(dy, dx))
                return incline
        return 0

    def draw(self, surface, camera_x):
        points = []
        for px, py in self.smooth_points:
            points.append((px - camera_x, py))
        pygame.draw.lines(surface, GROUND_COLOR, False, points, 5)