import pygame
import math
from settings import (
    CAR_MASS,
    CAR_ENGINE_FORCE,
    CAR_BRAKE_FORCE,
    CAR_FRICTION,
    CAR_AIR_RESISTANCE,
    WHEEL_RADIUS,
    TIME_STEP,
)
from src.physics import Physics

class Car:
    def __init__(self, x, y):
        self.physics = Physics(
            mass=CAR_MASS,
            engine_force=CAR_ENGINE_FORCE,
            brake_force=CAR_BRAKE_FORCE,
            friction=CAR_FRICTION,
            air_resistance=CAR_AIR_RESISTANCE,
        )
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.angle = 0  # Kąt nachylenia pojazdu
        self.angular_velocity = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.crashed = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.physics.throttle = 1.0
            self.physics.brake = 0.0
            # Debugowanie
            #print("Right arrow pressed")
        elif keys[pygame.K_LEFT]:
            self.physics.throttle = 0.0
            self.physics.brake = 1.0
            # Debugowanie
            #print("Left arrow pressed")
        else:
            self.physics.throttle = 0.0
            self.physics.brake = 0.0

        if keys[pygame.K_UP]:
            self.angular_velocity -= 0.05
        elif keys[pygame.K_DOWN]:
            self.angular_velocity += 0.05
        else:
            self.angular_velocity *= 0.9  # Tłumienie obrotu

    def perform_action(self, action):
        # Akcja 0: Brak akcji
        if action == 0:
            self.physics.throttle = 0.0
            self.physics.brake = 0.0
            self.angular_velocity *= 0.9
        # Akcja 1: Przyspieszanie
        elif action == 1:
            self.physics.throttle = 1.0
            self.physics.brake = 0.0
        # Akcja 2: Hamowanie
        elif action == 2:
            self.physics.throttle = 0.0
            self.physics.brake = 1.0
        # Akcja 3: Pochylanie w lewo
        elif action == 3:
            self.angular_velocity -= 0.05
        # Akcja 4: Pochylanie w prawo
        elif action == 4:
            self.angular_velocity += 0.05

    def update(self, terrain):
        # Aktualizacja fizyki pojazdu
        incline = terrain.get_incline(self.x)
        self.physics.update(incline, TIME_STEP)

        # Aktualizacja prędkości
        self.velocity_x = self.physics.velocity * math.cos(math.radians(self.angle))
        # Dodanie wpływu grawitacji do prędkości pionowej
        self.velocity_y += self.physics.gravity * TIME_STEP

        # Aktualizacja pozycji
        self.x += self.velocity_x * TIME_STEP
        self.y += self.velocity_y * TIME_STEP

        # Aktualizacja kąta
        self.angle += math.degrees(self.angular_velocity * TIME_STEP)

        # Sprawdzenie kolizji z terenem
        ground_y = terrain.get_ground_y(self.x)
        if self.y > ground_y - self.height / 2:
            self.y = ground_y - self.height / 2
            self.velocity_y = 0  # Zatrzymanie pionowej prędkości
            self.angular_velocity = 0
            if abs(self.angle) > 90:  # Zwiększenie tolerancji do 90 stopni
                self.crashed = True
                print(f"Angle after collision: {self.angle}")

    def draw(self, surface, camera_x):
        # Rysowanie pojazdu z uwzględnieniem obrotu
        car_rect = pygame.Rect(0, 0, self.width, self.height)
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, (255, 0, 0), car_rect)
        rotated_car = pygame.transform.rotate(car_surface, -self.angle)
        rect = rotated_car.get_rect(center=(self.x - camera_x, self.y - self.height / 2))
        surface.blit(rotated_car, rect)