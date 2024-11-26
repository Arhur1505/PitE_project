# src/environment.py

import gym
from gym import spaces
import numpy as np
from src.game import Game

class HillClimbRacingEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(HillClimbRacingEnv, self).__init__()
        # Definicja przestrzeni akcji i stanu
        self.action_space = spaces.Discrete(5)  # 5 akcji
        # Przestrzeń stanów: [velocity, angle, angular_velocity, incline]
        low = np.array([-50, -180, -10, -90], dtype=np.float32)
        high = np.array([50, 180, 10, 90], dtype=np.float32)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        # Inicjalizacja gry
        self.game = Game(render_mode=False)

    def reset(self):
        state = self.game.reset()
        return state

    def step(self, action):
        state, reward, done, info = self.game.step(action)
        return state, reward, done, info

    def render(self, mode='human'):
        self.game.render()

    def close(self):
        pass
