import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from car import create_car
from physics import create_world
from game import draw_body
from settings import WIDTH, HEIGHT, WHITE, CAR_COLOR, WHEEL_COLOR, DRIVER_COLOR, GROUND_COLOR


class HillClimbEnv(gym.Env):
    def __init__(self, max_steps=1000, debug=False):
        super(HillClimbEnv, self).__init__()
        self.max_steps = max_steps
        self.current_step = 0
        self.debug = debug

        self.last_x = 0
        self.world, self.ground_body = create_world()
        (
            self.car_body,
            self.wheel1,
            self.wheel2,
            self.driver_body,
            self.joint1,
            self.joint2
        ) = create_car(self.world)

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

        self.gas_cooldown = 0
        self.gas_streak = 0

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 18)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hill Climb Racing RL")
        self.is_rendering = False

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.world, self.ground_body = create_world()
        (
            self.car_body,
            self.wheel1,
            self.wheel2,
            self.driver_body,
            self.joint1,
            self.joint2
        ) = create_car(self.world)

        self.offset_x = 0
        self.current_step = 0
        self.current_reward = 0
        self.last_x = 0

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

        optimal_slope = self._calculate_ground_slope()
        current_angle = self.car_body.angle
        angle_diff = abs(current_angle - optimal_slope)

        if np.pi / 2 - 0.1 <= abs(current_angle) <= np.pi / 2 + 0.1:
            self.current_reward += 5.0
            if current_angle > 0:
                action = 2
            else:
                action = 1

        if angle_diff > np.pi / 6:
            if current_angle > optimal_slope:
                action = 2
            elif current_angle < optimal_slope:
                action = 1


        current_speed = abs(self.car_body.linearVelocity[0])
        if current_speed > 12.0:
            if action == 1 or action == 2:
                self.current_reward -= 5.0
                action = 0

        if action == 0:
            self.joint1.motorSpeed = 0.0
            self.joint2.motorSpeed = 0.0
            self.gas_streak = 0
        elif action == 1 and touching_ground and self.gas_cooldown <= 5:
            self.joint1.motorSpeed = -30.0
            self.joint2.motorSpeed = -30.0
            self.gas_streak += 1
        elif action == 2 and touching_ground and self.gas_cooldown <= 5:
            self.joint1.motorSpeed = 30.0
            self.joint2.motorSpeed = 30.0
            self.gas_streak += 1
        else:
            self.joint1.motorSpeed = 0.0
            self.joint2.motorSpeed = 0.0
            self.gas_streak = 0

        if self.gas_streak > 50:
            self.current_reward -= 10.0

        self.world.Step(1 / 60, 6, 2)

        obs = self._get_observation()

        reward = 0.0

        current_x = self.car_body.position[0]
        delta_x = current_x - self.last_x
        self.last_x = current_x
        if delta_x > 0:
            reward += delta_x * 10.0

        if angle_diff <= np.pi / 12:
            reward += 10.0
        elif angle_diff <= np.pi / 6:
            reward += 5.0
        else:
            reward -= angle_diff * 2.0

        current_speed = self.car_body.linearVelocity[0]
        target_speed = 5.0
        speed_diff = abs(current_speed - target_speed)
        if 6.0 <= current_speed:
            reward += 15.0
        else:
            reward += max(0, 10.0 - speed_diff)

        if self.current_step % 50 == 0:
            reward += 10.0

        if not touching_ground:
            reward -= 2.0

        if self.car_body.position[1] < 0:
            reward -= 100.0

        if np.pi / 2 - 0.1 <= abs(current_angle) <= np.pi / 2 + 0.1 and abs(angle_diff) <= np.pi / 12:
            reward += 50.0

        self.current_reward += reward

        done = self._is_done()

        if self.current_step >= self.max_steps:
            done = True

        if done:
            self.episode_rewards.append(self.current_reward)

        ground_slope = self._calculate_ground_slope()
        angle_diff = self._calculate_angle_diff()

        info = {
            "ground_slope": ground_slope,
            "angle_diff": angle_diff
        }

        terminated = self._is_done()
        truncated = False
        if self.current_step >= self.max_steps:
            truncated = True

        return obs, reward, terminated, truncated, info

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        self.screen.fill(WHITE)
        self.offset_x = self.car_body.position[0] * 20 - WIDTH / 2

        draw_body(self.ground_body, GROUND_COLOR, self.offset_x)
        draw_body(self.car_body, CAR_COLOR, self.offset_x)
        draw_body(self.wheel1, WHEEL_COLOR, self.offset_x)
        draw_body(self.wheel2, WHEEL_COLOR, self.offset_x)
        draw_body(self.driver_body, DRIVER_COLOR, self.offset_x)

        car_pos = self.car_body.position
        car_vel = self.car_body.linearVelocity
        ground_slope = self._calculate_ground_slope()
        angle_diff = self._calculate_angle_diff()

        self._draw_text(f"Car Position: x={car_pos[0]:.2f}, y={car_pos[1]:.2f}", 10, 10)
        self._draw_text(f"Car Velocity: x={car_vel[0]:.2f}, y={car_vel[1]:.2f}", 10, 30)
        self._draw_text(f"Ground Slope: {ground_slope:.2f}", 10, 50)
        self._draw_text(f"Angle Difference: {angle_diff:.2f}", 10, 70)

        pygame.display.flip()
        self.clock.tick(60)

    def _calculate_ground_slope(self):
        terrain_points = self.ground_body.userData.get("points", [])
        if not terrain_points:
            return 0.0

        car_pos = self.car_body.position

        def find_closest_point(x_pos):
            return min(terrain_points, key=lambda p: abs(p[0] - x_pos))

        closest_point = find_closest_point(car_pos[0])
        left_point = find_closest_point(car_pos[0] - 1)
        right_point = find_closest_point(car_pos[0] + 1)
        ground_slope = np.arctan2(right_point[1] - left_point[1], right_point[0] - left_point[0])
        return ground_slope

    def _calculate_angle_diff(self):
        ground_slope = self._calculate_ground_slope()
        car_angle = self.car_body.angle
        return car_angle - ground_slope

    def _is_touching_ground(self):
        for contact_edge in self.wheel1.contacts:
            if contact_edge.contact.touching:
                return True
        for contact_edge in self.wheel2.contacts:
            if contact_edge.contact.touching:
                return True
        return False

    def _is_done(self):
        if self.driver_body.position[1] < 0:
            return True
        if abs(self.car_body.angle) >= np.pi / 2:
            self.current_reward -= 50.0
            return True
        return False

    def _draw_text(self, text, x, y, color=(0, 0, 0)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def _get_observation(self):
        car_pos = self.car_body.position
        car_vel = self.car_body.linearVelocity
        wheel_angle1 = self.joint1.angle
        wheel_angle2 = self.joint2.angle
        return np.array(
            [car_pos[0], car_pos[1], car_vel[0], car_vel[1], wheel_angle1, wheel_angle2],
            dtype=np.float32
        )