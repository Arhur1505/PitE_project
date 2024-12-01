import pygame

BLUE = (0, 0, 255)

class Circle:
    def __init__(self, radius, position):
        self.radius = radius
        self.x = position[0]
        self.y = position[1]
    def draw(self, screen):
        pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius, width=100)
    def accelerate():
        x += 5
    def decrease_speed():
        x -=5