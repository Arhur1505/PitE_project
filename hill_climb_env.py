import pickle
import gym
from gym import spaces
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

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(
            low=np.array([-np.inf] * 6),
            high=np.array([np.inf] * 6),
            dtype=np.float32
        )

        self.clock = pygame.time.Clock()
        self.offset_x = 0
        self.episode_rewards = []  # Przechowujemy wyniki epizodów
        self.current_reward = 0

        # Inicjalizacja dodatkowych zmiennych
        self.gas_cooldown = 0  # Licznik opóźnienia gazu
        self.gas_streak = 0  # Licznik ciągłego gazowania

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hill Climb Racing RL")
        self.is_rendering = False

    def reset(self):
        self.world, self.ground_body = create_world()
        self.car_body, self.wheel1, self.wheel2, self.driver_body, self.joint1, self.joint2 = create_car(self.world)

        self.offset_x = 0
        self.current_step = 0
        self.current_reward = 0
        self.last_x = 0

        # Resetujemy zmienne pomocnicze
        self.gas_cooldown = 0
        self.gas_streak = 0

        return self._get_observation()

    def step(self, action):
        self.current_step += 1

        # Sprawdź, czy pojazd dotyka ziemi
        touching_ground = self._is_touching_ground()

        # Opóźnienie gazu po lądowaniu
        if touching_ground:
            self.gas_cooldown = 0  # Reset cooldown, jeśli pojazd dotyka ziemi
        else:
            self.gas_cooldown += 1

        # Ustal prędkość kół w zależności od wybranej akcji
        if action == 0:  # Brak akcji
            self.joint1.motorSpeed = 0.0
            self.joint2.motorSpeed = 0.0
            self.gas_streak = 0  # Resetuj licznik gazu
        elif action == 1 and touching_ground and self.gas_cooldown <= 5:  # Jedź w prawo
            self.joint1.motorSpeed = -30.0
            self.joint2.motorSpeed = -30.0
            self.gas_streak += 1
        elif action == 2 and touching_ground and self.gas_cooldown <= 5:  # Jedź w lewo
            self.joint1.motorSpeed = 30.0
            self.joint2.motorSpeed = 30.0
            self.gas_streak += 1
        else:  # Wymuszony reset gazu w przypadku cooldownu
            self.joint1.motorSpeed = 0.0
            self.joint2.motorSpeed = 0.0
            self.gas_streak = 0

        # Kara za zbyt długie gazowanie
        if self.gas_streak > 50:
            self.current_reward -= 10.0

        # Wykonaj krok symulacji fizyki
        self.world.Step(1 / 60, 6, 2)

        # Obserwacje
        obs = self._get_observation()

        # Nagrody
        reward = 0.0

        # 1. **Nagroda za poruszanie się do przodu**
        current_x = self.car_body.position[0]
        delta_x = current_x - self.last_x
        self.last_x = current_x

        if delta_x > 0:
            reward += delta_x * 10.0

        # 2. **Nagroda za stabilność**
        angle = abs(self.car_body.angle)
        if angle <= np.pi / 12:  # 15 stopni
            reward += 10.0
        elif angle <= np.pi / 6:  # 30 stopni
            reward += 5.0

        # 3. **Nagroda za prędkość**
        current_speed = self.car_body.linearVelocity[0]
        target_speed = 5.0
        speed_diff = abs(current_speed - target_speed)
        if 4.0 <= current_speed <= 6.0:  # Optymalna prędkość
            reward += 15.0
        else:
            reward += max(0, 10.0 - speed_diff)

        # 4. **Nagroda za dłuższą jazdę bez błędów**
        if self.current_step % 50 == 0:
            reward += 10.0

        # 5. **Kary**
        if not touching_ground:  # Kara za bycie w powietrzu
            reward -= 2.0
        if self.car_body.position[1] < 0:  # Spadek poniżej poziomu terenu
            reward -= 100.0

        # Suma nagród
        self.current_reward += reward

        # Sprawdzenie, czy epizod się kończy
        done = self._is_done()

        # Maksymalna liczba kroków
        if self.current_step >= self.max_steps:
            done = True

        # Zapis wyników po zakończeniu epizodu
        if done:
            self.episode_rewards.append(self.current_reward)
            self._save_results()

        # Debugowanie
        if self.debug:
            print(f"Step: {self.current_step}, Reward: {reward:.2f}, Total Reward: {self.current_reward:.2f}")

        return obs, reward, done, {}

    def _is_touching_ground(self):
        for contact_edge in self.wheel1.contacts:
            if contact_edge.contact.touching:
                return True
        for contact_edge in self.wheel2.contacts:
            if contact_edge.contact.touching:
                return True
        return False

    def _save_results(self):
        with open("results.pkl", "wb") as f:
            pickle.dump(self.episode_rewards, f)
        print(f"Wyniki zapisane: {self.episode_rewards}")

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

    def _get_observation(self):
        car_pos = self.car_body.position
        car_vel = self.car_body.linearVelocity
        wheel_angle1 = self.joint1.angle
        wheel_angle2 = self.joint2.angle
        return np.array([car_pos[0], car_pos[1], car_vel[0], car_vel[1], wheel_angle1, wheel_angle2], dtype=np.float32)

    def _is_done(self):
        if self.driver_body.position[1] < 0:
            return True
        if abs(self.car_body.angle) > np.pi / 2:
            return True
        return False
