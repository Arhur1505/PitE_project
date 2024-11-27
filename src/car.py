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
        self.velocity_y += self.physics.gravity * TIME_STEP

        # Aktualizacja pozycji
        self.x += self.velocity_x * TIME_STEP
        self.y += self.velocity_y * TIME_STEP

        # Dostosowanie kąta samochodu do nachylenia terenu
        target_angle = incline
        self.angle += (target_angle - self.angle) * 0.1  # Płynne dostosowanie kąta

        # Sprawdzenie kolizji z terenem (koło styka się krawędzią z ziemią)
        ground_y = terrain.get_ground_y(self.x)
        if self.y > ground_y - WHEEL_RADIUS:
            self.y = ground_y - WHEEL_RADIUS
            self.velocity_y = 0  # Zatrzymanie pionowej prędkości
            self.angular_velocity = 0
            if abs(self.angle) > 90:  # Unikaj przewracania
                self.crashed = True

    def draw(self, surface, camera_x):
        # Define wheel radius and bar length
        wheel_radius = 15
        bar_length = 100  # Increased distance between wheels

        # Calculate positions for the front and rear wheels
        front_wheel_x = self.x + (bar_length / 2) * math.cos(math.radians(self.angle)) - camera_x
        front_wheel_y = self.y - (bar_length / 2) * math.sin(math.radians(self.angle))
        rear_wheel_x = self.x - (bar_length / 2) * math.cos(math.radians(self.angle)) - camera_x
        rear_wheel_y = self.y + (bar_length / 2) * math.sin(math.radians(self.angle))

        # Calculate the center of the bar for driver positioning
        bar_center_x = self.x - camera_x
        bar_center_y = self.y

        # Create a surface for the car with alpha for rotation
        car_surface = pygame.Surface((bar_length + 40, wheel_radius * 2 + 40), pygame.SRCALPHA)
        car_rect = car_surface.get_rect(center=(bar_center_x, bar_center_y))

        # Draw the bar connecting the wheels
        pygame.draw.line(
            car_surface,
            (0, 0, 0),  # Bar color (black)
            (20, wheel_radius + 20),
            (bar_length + 20, wheel_radius + 20),
            4,  # Line thickness
        )

        # Draw the wheels
        pygame.draw.circle(
            car_surface,
            (0, 0, 0),  # Wheel color (black)
            (20, wheel_radius + 20),
            wheel_radius,
        )
        pygame.draw.circle(
            car_surface,
            (0, 0, 0),  # Wheel color (black)
            (bar_length + 20, wheel_radius + 20),
            wheel_radius,
        )

        # Draw the driver rectangle in the middle of the bar
        driver_width = 20
        driver_height = 40
        driver_rect = pygame.Rect(
            bar_length // 2 + 10,  # Center horizontally relative to the bar
            wheel_radius - driver_height // 2,  # Vertically centered on the bar
            driver_width,
            driver_height,
        )
        pygame.draw.rect(car_surface, (255, 0, 0), driver_rect)

        # Rotate the entire car surface
        rotated_car = pygame.transform.rotate(car_surface, -self.angle)
        rotated_rect = rotated_car.get_rect(center=(self.x - camera_x, self.y))
        surface.blit(rotated_car, rotated_rect)
