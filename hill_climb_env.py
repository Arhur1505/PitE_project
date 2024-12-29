import pickle
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from car import create_car
from physics import create_world
from game import draw_body
from settings import WIDTH, HEIGHT, WHITE, CAR_COLOR, WHEEL_COLOR, DRIVER_COLOR, GROUND_COLOR
import pygame


def dynamic_max_speed(angle, velocity):
    """
    Funkcja ustalająca maksymalną wartość motorSpeed zależnie od kąta auta (angle)
    i aktualnej prędkości (velocity).

    angle: kąt auta (float, w radianach)
    velocity: prędkość liniowa auta w osi x (float)

    Zwraca (min_speed, max_speed) - obie dodatnie.
    W step() minus motorSpeed oznacza jazdę "do przodu", plus - do tyłu (lub odwrotnie).
    """
    MAX_SPEED_FLAT = 40.0
    MIN_SPEED_FLAT = 5.0
    MAX_SPEED_SLOPE = 15.0
    MIN_SPEED_SLOPE = 2.0

    limited_angle = min(abs(angle), np.pi / 2)  # [0, pi/2]
    alpha = limited_angle / (np.pi / 2)  # normalizacja [0..1]

    # interpolacja wartości w zależności od alpha
    max_speed = (1 - alpha) * MAX_SPEED_FLAT + alpha * MAX_SPEED_SLOPE
    min_speed = (1 - alpha) * MIN_SPEED_FLAT + alpha * MIN_SPEED_SLOPE

    # Jeśli jedziemy bardzo szybko (|v|>6), ogranicz max_speed
    if abs(velocity) > 6.0:
        max_speed *= 0.5

    return min_speed, max_speed


class HillClimbEnv(gym.Env):
    def __init__(self, max_steps=1000, debug=False):
        super(HillClimbEnv, self).__init__()
        self.prev_speed = 0
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
        self.episode_rewards = []
        self.current_reward = 0

        # Zmienna do liczenia "silnego startu"
        self.start_phase_steps = 50  # przez ile kroków wymuszamy jazdę do przodu
        self.start_speed = -15.0  # prędkość motorSpeed w fazie startu

        self.gas_cooldown = 0
        self.gas_streak = 0

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

        self.prev_speed = 0.0
        self.gas_cooldown = 0
        self.gas_streak = 0

        observation = self._get_observation()
        return observation, {}

    def step(self, action):
        self.current_step += 1

        touching_ground = self._is_touching_ground()
        if touching_ground:
            self.gas_cooldown = 0
        else:
            self.gas_cooldown += 1

        current_angle = self.car_body.angle
        slope_angle = self._calculate_ground_slope()
        angle_diff = abs(current_angle - slope_angle)

        # --- Faza startu: przez X kroków wymuszaj jazdę do przodu ---
        if self.current_step < self.start_phase_steps:
            self._apply_start_speed()
        else:
            # Blok anty-flip (jeśli kąt > 35 stopni => ±10)
            if abs(current_angle) > 0.61:
                if current_angle > 0:
                    self.joint1.motorSpeed = -10.0
                    self.joint2.motorSpeed = -10.0
                else:
                    self.joint1.motorSpeed = 10.0
                    self.joint2.motorSpeed = 10.0
                self.gas_streak = 0

            else:
                # Główna logika dynamiczna
                current_speed = self.car_body.linearVelocity.x
                min_spd, max_spd = dynamic_max_speed(current_angle, current_speed)

                if action == 0:
                    self.joint1.motorSpeed = 0.0
                    self.joint2.motorSpeed = 0.0
                    self.gas_streak = 0

                elif action == 1 and touching_ground and self.gas_cooldown <= 5:
                    # "Jedź do przodu" (minus => w przód)
                    self.joint1.motorSpeed = -max_spd
                    self.joint2.motorSpeed = -max_spd
                    self.gas_streak += 1

                elif action == 2 and touching_ground and self.gas_cooldown <= 5:
                    # "Jedź do tyłu" (plus => w tył)
                    self.joint1.motorSpeed = max_spd
                    self.joint2.motorSpeed = max_spd
                    self.gas_streak += 1

                else:
                    self.joint1.motorSpeed = 0.0
                    self.joint2.motorSpeed = 0.0
                    self.gas_streak = 0

        if self.gas_streak > 50:
            self.current_reward -= 10.0

        # Update Box2D
        self.world.Step(1 / 60, 6, 2)
        obs = self._get_observation()

        # ------------------ Obliczanie nagrody ------------------
        reward = 0.0

        # 1. Ruch w prawo
        current_x = self.car_body.position[0]
        delta_x = current_x - self.last_x
        self.last_x = current_x
        if delta_x > 0:
            reward += delta_x * 10.0

        # 2. Stabilność kąta
        if angle_diff <= np.pi / 12:
            reward += 75.0
        elif angle_diff <= np.pi / 6:
            reward += 37.5
        else:
            reward -= angle_diff * 2.0

        # 3. Utrzymywanie w miarę stałej prędkości (dla v > speed_threshold)
        speed_threshold = 5
        current_speed = self.car_body.linearVelocity[0]

        # O ile zmieniła się prędkość od poprzedniego kroku?
        speed_change = abs(current_speed - self.prev_speed)

        # [DOPISANE] - sprawdzamy warunek dopiero dla większej prędkości
        if abs(current_speed) > speed_threshold:
            if speed_change < 2.0:
                reward += 10.0
            else:
                # Możesz odejmować tym więcej, im większa zmiana prędkości
                reward -= speed_change * 2.0

        # Na koniec zapamiętaj bieżącą prędkość:
        self.prev_speed = current_speed

        # 4. Dodatkowy bonus co 50 kroków
        if self.current_step % 50 == 0:
            reward += 10.0

        # 5. Kary
        if not touching_ground:
            reward -= 2.0
        if self.car_body.position[1] < 0:
            reward -= 100.0

        # 6. Bonus za "odzyskanie równowagi" przy ~90 stopniach
        if np.pi / 2 - 0.1 <= abs(current_angle) <= np.pi / 2 + 0.1 and angle_diff <= np.pi / 12:
            reward += 100.0

        self.current_reward += reward

        done = self._is_done()
        truncated = False
        if self.current_step >= self.max_steps:
            done = True
            truncated = True

        if done:
            self.episode_rewards.append(self.current_reward)
            self._save_results()

        return obs, reward, done, truncated, {}

    # -------------------------------------
    # FUNKCJA: wymuszenie startu do przodu
    # -------------------------------------
    def _apply_start_speed(self):
        """
        Zamiast dynamicznego speedu, wymuszamy tu prostą jazdę do przodu
        z ustaloną prędkością (self.start_speed).
        """
        self.joint1.motorSpeed = self.start_speed
        self.joint2.motorSpeed = self.start_speed
        # Tutaj można ewentualnie zwiększać self.start_speed co krok,
        # żeby auto powoli się rozpędzało
        self.gas_streak += 1

    def _calculate_ground_slope(self):
        if not self._is_touching_ground():
            return 0.0

        terrain_points = self.ground_body.userData.get("points", [])
        if not terrain_points:
            return 0.0

        wheel1_pos = self.wheel1.position
        wheel2_pos = self.wheel2.position
        car_pos = self.car_body.position

        def find_closest_point(x_pos):
            return min(terrain_points, key=lambda p: abs(p[0] - x_pos))

        closest_wheel1 = find_closest_point(wheel1_pos[0])
        closest_wheel2 = find_closest_point(wheel2_pos[0])
        closest_car = find_closest_point(car_pos[0])

        wheel_ground_slope = np.arctan2(
            closest_wheel2[1] - closest_wheel1[1],
            closest_wheel2[0] - closest_wheel1[0]
        )
        car_ground_slope = np.arctan2(
            closest_car[1] - closest_wheel1[1],
            closest_car[0] - closest_wheel1[0]
        )
        average_ground_slope = (wheel_ground_slope + car_ground_slope) / 2

        car_angle = self.car_body.angle
        level_diff = abs(car_angle)
        slope_diff = abs(car_angle - average_ground_slope)

        if slope_diff < level_diff and slope_diff < np.pi / 6:
            return average_ground_slope

        if level_diff > np.pi / 3:
            return 0.0

        return average_ground_slope

    def _is_touching_ground(self):
        for contact_edge in self.wheel1.contacts:
            if contact_edge.contact.touching:
                return True
        for contact_edge in self.wheel2.contacts:
            if contact_edge.contact.touching:
                return True
        return False

    def _save_results(self):
        with open("results.pkl", "ab") as f:
            pickle.dump(self.episode_rewards, f)
        print(f"Results saved: {self.episode_rewards}")

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
        return np.array([car_pos[0], car_pos[1],
                         car_vel[0], car_vel[1],
                         wheel_angle1, wheel_angle2], dtype=np.float32)

    def _is_done(self):
        if self.driver_body.position[1] < 0:
            return True
        if abs(self.car_body.angle) >= np.pi / 3:
            self.current_reward -= 200.0
            return True
        if abs(self.car_body.angle) >= np.pi / 2:
            self.current_reward -= 50.0
            return True
        return False
