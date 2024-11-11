# src/physics.py

import math
from settings import GRAVITY

class Physics:
    def __init__(self, mass, engine_force, brake_force, friction, air_resistance):
        self.mass = mass  # Masa pojazdu
        self.engine_force = engine_force  # Maksymalna siła silnika
        self.brake_force = brake_force  # Siła hamowania
        self.friction = friction  # Współczynnik tarcia
        self.air_resistance = air_resistance  # Opór powietrza
        self.gravity = GRAVITY  # Przyspieszenie grawitacyjne

        self.velocity = 0  # Prędkość pojazdu
        self.throttle = 0  # Poziom gazu (0-1)
        self.brake = 0  # Poziom hamowania (0-1)

    def update(self, incline, delta_time):
        # Siła napędowa (działa w kierunku jazdy)
        force_engine = self.throttle * self.engine_force

        # Siła hamowania (przeciwdziała ruchowi)
        force_brake = self.brake * self.brake_force

        # Siła grawitacji na zboczu (działa w dół zbocza)
        force_gravity = self.mass * self.gravity * math.sin(math.radians(incline))

        # Siła tarcia (przeciwdziała ruchowi)
        force_friction = self.friction * self.mass * self.gravity * math.cos(math.radians(incline))

        # Opór powietrza (przeciwdziała ruchowi)
        force_air_resistance = self.air_resistance * self.velocity ** 2

        # Suma sił
        net_force = force_engine - force_brake - force_friction - force_air_resistance - force_gravity

        # Przyspieszenie
        acceleration = net_force / self.mass

        # Aktualizacja prędkości
        self.velocity += acceleration * delta_time

        # Ograniczenie prędkości
        self.velocity = max(min(self.velocity, 50), -20)
