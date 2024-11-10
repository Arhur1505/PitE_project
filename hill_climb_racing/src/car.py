import pygame
import math
from settings import GRAVITY, CAR_ACCELERATION, CAR_FRICTION

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.speed = 0
        self.acceleration = 0
        self.angle = 0  # Kąt nachylenia pojazdu
        self.angular_velocity = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.acceleration += CAR_ACCELERATION
        if keys[pygame.K_LEFT]:
            self.acceleration -= CAR_ACCELERATION
        if keys[pygame.K_UP]:
            self.angular_velocity -= 1
        if keys[pygame.K_DOWN]:
            self.angular_velocity += 1

    def update(self, terrain):
        # Aktualizacja prędkości i pozycji
        self.speed += self.acceleration
        self.speed *= (1 - CAR_FRICTION)  # Tarcie
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle)) + GRAVITY
        self.angle += self.angular_velocity

        # Reset przyspieszenia po każdej aktualizacji
        self.acceleration = 0
        self.angular_velocity = 0

        # Interakcja z terenem
        ground_y = terrain.get_ground_y(self.x)
        if self.y > ground_y - self.height / 2:
            self.y = ground_y - self.height / 2
            self.speed = 0  # Zatrzymanie na ziemi

    def draw(self, surface, camera_x):
        rect = pygame.Rect(self.x - camera_x, self.y - self.height, self.width, self.height)
        pygame.draw.rect(surface, (255, 0, 0), rect)
