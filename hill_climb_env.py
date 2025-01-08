import pickle
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from car import create_car
from physics import create_world
from game import draw_body
from settings import WIDTH, HEIGHT, WHITE, CAR_COLOR, WHEEL_COLOR, DRIVER_COLOR, GROUND_COLOR
import pygame


class HillClimbEnv(gym.Env):
    def __init__(self, max_steps=1000, debug=False):
        super(HillClimbEnv, self).__init__()
        self.max_steps = max_steps
        self.current_step = 0
        self.debug = debug

        self.last_x = 0
        self.world, self.ground_body = create_world()
        self.car_body, self.wheel1, self.wheel2, self.driver_body, self.joint1, self.joint2 = create_car(self.world)

        # Ciągła przestrzeń akcji: sterowanie dla dwóch kół
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0]),  # Minimalna wartość akcji
            high=np.array([1.0, 1.0]),  # Maksymalna wartość akcji
            dtype=np.float32
        )

        # Przestrzeń obserwacji
        self.observation_space = spaces.Box(
            low=np.array([-np.inf] * 6),  # Pozycja, prędkość, kąty itp.
            high=np.array([np.inf] * 6),
            dtype=np.float32
        )

        self.clock = pygame.time.Clock()
        self.offset_x = 0
        self.episode_rewards = []
        self.current_reward = 0

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hill Climb Racing RL")
        self.is_rendering = False

    def reset(self, **kwargs):
        self.world, self.ground_body = create_world()
        self.car_body, self.wheel1, self.wheel2, self.driver_body, self.joint1, self.joint2 = create_car(self.world)

        self.offset_x = 0
        self.current_step = 0
        self.current_reward = 0
        self.last_x = 0

        observation = self._get_observation()
        info = {}  # Dodaj pusty słownik jako informację dodatkową
        return observation, info

    def step(self, action):
        self.current_step += 1

        # Przekształcenie akcji do prędkości silników kół
        motor_speed1 = action[0] * 30.0  # Akcja przeskalowana do prędkości
        motor_speed2 = action[1] * 30.0
        self.joint1.motorSpeed = motor_speed1
        self.joint2.motorSpeed = motor_speed2

        # Aktualizacja świata fizyki
        self.world.Step(1 / 60, 6, 2)

        obs = self._get_observation()
        reward = self._calculate_reward()
        done = self._is_done()

        # Nowy element: truncated - czy epizod zakończył się z innych powodów niż done
        truncated = self.current_step >= self.max_steps

        # Puste pole info
        info = {}

        if done or truncated:
            self.episode_rewards.append(self.current_reward)
            self._save_results()

        if self.debug:
            print(f"Step: {self.current_step}, Reward: {reward:.2f}, Total Reward: {self.current_reward:.2f}")

        # Zwróć 5 elementów
        return obs, reward, done, truncated, info

    def _calculate_reward(self):
        reward = 0.0

        # Nagroda za poruszanie się do przodu
        current_x = self.car_body.position[0]
        delta_x = current_x - self.last_x
        self.last_x = current_x

        if delta_x > 0:
            reward += delta_x * 20.0  # Zwiększona nagroda za pokonywanie dystansu

        # Kara za zbyt niską prędkość
        current_speed = self.car_body.linearVelocity[0]
        if current_speed < 2.0:
            reward -= 10.0  # Kara za zatrzymywanie się lub zbyt wolny ruch

        # Nagroda za utrzymanie wysokiej prędkości
        target_speed = 8.0  # Podnieś docelową prędkość
        speed_diff = abs(current_speed - target_speed)
        if current_speed >= 6.0:
            reward += 20.0  # Zachęta za przekroczenie prędkości progowej
        else:
            reward += max(0, 10.0 - speed_diff)  # Mniejsza nagroda dla mniejszych prędkości

        # Kara za przechylenie pojazdu
        angle = abs(self.car_body.angle)
        if angle > np.pi / 6:  # Łagodniejszy limit kąta
            reward -= 15.0  # Zwiększona kara za niestabilność
        elif angle > np.pi / 12:
            reward -= 5.0  # Łagodniejsza kara dla mniejszych kątów

        # Nagroda za utrzymanie stabilności w szybkim ruchu
        if delta_x > 0 and current_speed >= 6.0 and angle < np.pi / 12:
            reward += 30.0  # Duża nagroda za stabilność przy szybkiej jeździe

        self.current_reward += reward
        return reward

    def _get_observation(self):
        car_pos = self.car_body.position
        car_vel = self.car_body.linearVelocity
        wheel_angle1 = self.joint1.angle
        wheel_angle2 = self.joint2.angle
        return np.array([car_pos[0], car_pos[1], car_vel[0], car_vel[1], wheel_angle1, wheel_angle2], dtype=np.float32)

    def _is_done(self):
        # Zakończ, jeśli samochód upadnie lub osiągnie limit kroków
        if self.car_body.position[1] < 0 or abs(self.car_body.angle) > np.pi / 2:
            return True
        return False

    def _save_results(self):
        with open("results.pkl", "ab") as f:
            pickle.dump(self.episode_rewards, f)

    def render(self, mode="human"):
        if mode == "human":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.screen.fill(WHITE)
            self.offset_x = self.car_body.position[0] * 20 - WIDTH / 2

            draw_body(self.ground_body, GROUND_COLOR, self.offset_x)
            draw_body(self.car_body, CAR_COLOR, self.offset_x)
            draw_body(self.wheel1, WHEEL_COLOR, self.offset_x)
            draw_body(self.wheel2, WHEEL_COLOR, self.offset_x)
            draw_body(self.driver_body, DRIVER_COLOR, self.offset_x)

            pygame.display.flip()
            self.clock.tick(60)

    def close(self):
        pygame.quit()
