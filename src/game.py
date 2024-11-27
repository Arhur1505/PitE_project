import pygame
import numpy as np
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SKY_COLOR, RENDER_MODE, TIME_STEP
from src.car import Car
from src.terrain import Terrain

class Game:
    def __init__(self, render_mode=RENDER_MODE):
        self.render_mode = render_mode
        if self.render_mode:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.car = Car(100, SCREEN_HEIGHT - 200)
        self.terrain = Terrain()
        self.camera_x = 0
        self.total_distance = 0
        self.done = False

    def reset(self):
        self.car = Car(100, SCREEN_HEIGHT - 200)
        self.terrain = Terrain()
        self.camera_x = 0
        self.total_distance = 0
        self.done = False
        return self.get_state()

    def step(self, action):
        self.car.perform_action(action)
        self.update()
        state = self.get_state()
        reward = self.get_reward()
        done = self.is_done()
        info = {}
        return state, reward, done, info

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            if self.render_mode:
                self.draw()
                self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        self.car.handle_input()  # Wywołuj zawsze handle_input()

    def update(self):
        self.car.update(self.terrain)
        self.camera_x = self.car.x - 100
        self.total_distance += self.car.velocity_x * TIME_STEP
        if self.is_done():
            self.running = False

    def draw(self):
        self.screen.fill(SKY_COLOR)
        self.terrain.draw(self.screen, self.camera_x)
        self.car.draw(self.screen, self.camera_x)
        pygame.display.flip()

    def get_state(self):
        state = np.array([
            self.car.velocity,
            self.car.angle,
            self.car.angular_velocity,
            self.terrain.get_incline(self.car.x),
        ], dtype=np.float32)
        return state

    def get_reward(self):
        if self.car.crashed:
            return -100
        else:
            # Nagroda za ruch do przodu minus kara za kąt nachylenia
            return self.car.velocity_x * TIME_STEP - abs(self.car.angle) * 0.01

    def is_done(self):
        if self.car.crashed or self.car.y > SCREEN_HEIGHT:
            self.done = True
            return True
        return False

    def render(self):
        if self.render_mode:
            self.draw()
            self.clock.tick(60)