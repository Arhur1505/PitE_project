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
        self.episode_rewards = []
        self.current_reward = 0

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

        self.gas_cooldown = 0
        self.gas_streak = 0

        observation = self._get_observation()

        return observation

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

        # 1. Reward for moving forward
        current_x = self.car_body.position[0]
        delta_x = current_x - self.last_x
        self.last_x = current_x

        if delta_x > 0:
            reward += delta_x * 10.0

        # 2. Reward for stability relative to terrain slope
        if angle_diff <= np.pi / 12:
            reward += 10.0
        elif angle_diff <= np.pi / 6:
            reward += 5.0
        else:
            reward -= angle_diff * 2.0

        # 3. Reward for maintaining optimal speed
        current_speed = self.car_body.linearVelocity[0]
        target_speed = 5.0
        speed_diff = abs(current_speed - target_speed)
        if 4.0 <= current_speed <= 6.0:
            reward += 15.0
        else:
            reward += max(0, 10.0 - speed_diff)

        # 4. Reward for consistent driving without errors
        if self.current_step % 50 == 0:
            reward += 10.0

        # 5. Penalties
        if not touching_ground:
            reward -= 2.0
        if self.car_body.position[1] < 0:
            reward -= 100.0

        # 6. Reward for recovering from a near 90-degree tilt
        if np.pi / 2 - 0.1 <= abs(current_angle) <= np.pi / 2 + 0.1 and abs(angle_diff) <= np.pi / 12:
            reward += 50.0

        self.current_reward += reward

        done = self._is_done()

        if self.current_step >= self.max_steps:
            done = True

        if done:
            self.episode_rewards.append(self.current_reward)
            self._save_results()

        if self.debug:
            print(f"Step: {self.current_step}, Reward: {reward:.2f}, Total Reward: {self.current_reward:.2f}")

        return obs, reward, done, {}

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
        return np.array([car_pos[0], car_pos[1], car_vel[0], car_vel[1], wheel_angle1, wheel_angle2], dtype=np.float32)

    def _is_done(self):
        if self.driver_body.position[1] < 0:
            return True
        if abs(self.car_body.angle) >= np.pi / 2:
            self.current_reward -= 50.0
            return True
        return False
