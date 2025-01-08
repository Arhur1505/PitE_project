import pickle
import pygame
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from car import create_car
from physics import create_world
from game import draw_body
from settings import WIDTH, HEIGHT, WHITE, CAR_COLOR, WHEEL_COLOR, DRIVER_COLOR, GROUND_COLOR


class HillClimbEnv(gym.Env):
    """
    Przykładowe środowisko stylizowane na 'Hill Climb Racing',
    wykorzystujące Box2D i generujące teren z modulem noise.
    """

    def __init__(self, max_steps=1000, debug=False):
        super().__init__()
        self.max_steps = max_steps
        self.current_step = 0
        self.debug = debug

        # Utworzenie Box2D world i pojazdu
        self.world, self.ground_body = create_world()
        (self.car_body,
         self.wheel1,
         self.wheel2,
         self.driver_body,
         self.joint1,
         self.joint2) = create_car(self.world)

        # Akcje: 0=nic, 1=cofanie, 2=przód
        self.action_space = spaces.Discrete(3)
        # Obserwacja: 6 wartości (pozycja x,y; prędkość vx, vy; kąt wheel1, kąt wheel2)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(6,),
            dtype=np.float32
        )

        # Przydatne zmienne do zliczania nagrody, offsety rysowania itp.
        self.clock = pygame.time.Clock()
        self.offset_x = 0
        self.episode_rewards = []
        self.current_reward = 0

        self.gas_cooldown = 0
        self.gas_streak = 0

        # Inicjalizacja Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hill Climb Racing RL")
        self.is_rendering = False

        if self.debug:
            print(">>> HillClimbEnv: konstruktor wywołany")

    def reset(self, *, seed=None, options=None):
        """
        Zgodnie z Gymnasium zwracamy (observation, info).
        """
        super().reset(seed=seed)
        if self.debug:
            print(">>> [RESET] Wywołanie reset()")

        self.world, self.ground_body = create_world()
        (self.car_body,
         self.wheel1,
         self.wheel2,
         self.driver_body,
         self.joint1,
         self.joint2) = create_car(self.world)

        self.offset_x = 0
        self.current_step = 0
        self.current_reward = 0
        self.last_x = 0
        self.gas_cooldown = 0
        self.gas_streak = 0

        obs = self._get_observation()
        return obs, {}

    def step(self, action):
        """
        Zgodnie z Gymnasium zwracamy:
        obs, reward, terminated, truncated, info
        """
        self.current_step += 1

        # 1. Czy koła dotykają ziemi?
        touching_ground = self._is_touching_ground()

        if touching_ground:
            self.gas_cooldown = 0
        else:
            self.gas_cooldown += 1

        # 2. Wylicz kąt terenu, sprawdź różnicę do kąta samochodu
        optimal_slope = self._calculate_ground_slope()
        current_angle = self.car_body.angle
        angle_diff = abs(current_angle - optimal_slope)

        # 3. Logika wspomagania, jeśli samochód jest bliski wywrócenia
        if np.pi / 2 - 0.1 <= abs(current_angle) <= np.pi / 2 + 0.1:
            self.current_reward += 5.0
            if current_angle > 0:
                action = 2  # jedź do przodu
            else:
                action = 1  # jedź do tyłu

        if angle_diff > np.pi / 6:
            if current_angle > optimal_slope:
                action = 2
            elif current_angle < optimal_slope:
                action = 1

        # 4. Obsługa akcji sterujących samochodem
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
            # Domyślnie brak ruchu
            self.joint1.motorSpeed = 0.0
            self.joint2.motorSpeed = 0.0
            self.gas_streak = 0

        # Kara za zbyt długie przytrzymywanie gazu
        if self.gas_streak > 50:
            self.current_reward -= 10.0

        # 5. Aktualizacja Box2D
        self.world.Step(1 / 60, 6, 2)

        # 6. Obserwacja i nagrody
        obs = self._get_observation()
        reward = 0.0

        #    a) Ruch do przodu
        current_x = self.car_body.position[0]
        delta_x = current_x - getattr(self, "last_x", 0)
        self.last_x = current_x
        if delta_x > 0:
            reward += delta_x * 10.0

        #    b) Stabilność
        if angle_diff <= np.pi / 12:
            reward += 10.0
        elif angle_diff <= np.pi / 6:
            reward += 5.0
        else:
            reward -= angle_diff * 2.0

        #    c) Prędkość około 5.0
        current_speed = self.car_body.linearVelocity[0]
        target_speed = 5.0
        speed_diff = abs(current_speed - target_speed)
        if 4.0 <= current_speed <= 6.0:
            reward += 15.0
        else:
            reward += max(0, 10.0 - speed_diff)

        #    d) Bonus co 50 kroków
        if self.current_step % 50 == 0:
            reward += 10.0

        #    e) Kary
        if not touching_ground:
            reward -= 2.0
        if self.car_body.position[1] < 0:
            reward -= 100.0

        #    f) Bonus za wyprostowanie się z prawie 90° nachylenia
        if np.pi / 2 - 0.1 <= abs(current_angle) <= np.pi / 2 + 0.1 and abs(angle_diff) <= np.pi / 12:
            reward += 50.0

        self.current_reward += reward

        # Rozróżnienie Gymnasium: terminated vs truncated
        # terminated = "naturalne" zakończenie epizodu (np. rozbicie, spadnięcie)
        # truncated = koniec z powodu max_steps
        terminated = self._is_done()
        truncated = self.current_step >= self.max_steps

        if terminated or truncated:
            self.episode_rewards.append(self.current_reward)
            self._save_results()

        if self.debug:
            print(f"Step: {self.current_step}, reward: {reward:.2f}, total: {self.current_reward:.2f}, "
                  f"terminated={terminated}, truncated={truncated}")

        return obs, reward, terminated, truncated, {}

    def render(self, mode="human"):
        """
        Render z użyciem PyGame. Wywołuj ręcznie (np. w pętli testowej) lub przez Monitor (opcjonalnie).
        """
        if mode == "human":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.screen.fill(WHITE)
            # offset_x to przesunięcie "kamery"
            self.offset_x = self.car_body.position[0] * 20 - WIDTH / 2

            draw_body(self.ground_body, GROUND_COLOR, self.offset_x)
            draw_body(self.car_body, CAR_COLOR, self.offset_x)
            draw_body(self.wheel1, WHEEL_COLOR, self.offset_x)
            draw_body(self.wheel2, WHEEL_COLOR, self.offset_x)
            draw_body(self.driver_body, DRIVER_COLOR, self.offset_x)

            pygame.display.flip()
            self.clock.tick(60)

    def _is_done(self):
        """
        Sprawdza, czy epizod powinien się zakończyć "naturalnie".
        """
        # driver spadł poniżej y=0
        if self.driver_body.position[1] < 0:
            return True
        # kąt >= 90 stopni => przewrócenie
        if abs(self.car_body.angle) >= np.pi / 2:
            self.current_reward -= 50.0
            return True

        return False

    def _calculate_ground_slope(self):
        """
        Przybliżenie kąta nachylenia terenu w okolicy kół i karoserii samochodu.
        """
        # Jeśli koła nie dotykają ziemi, przyjmujemy nachylenie = 0
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
        """
        Sprawdza, czy którekolwiek z kół styka się z podłożem.
        """
        for contact_edge in self.wheel1.contacts:
            if contact_edge.contact.touching:
                return True
        for contact_edge in self.wheel2.contacts:
            if contact_edge.contact.touching:
                return True
        return False

    def _save_results(self):
        """
        Przykładowe zapisywanie wyników do pliku .pkl (pickle).
        """
        # Tu lepiej użyć CSV lub JSON, ale dla przykładu:
        with open("results.pkl", "ab") as f:
            pickle.dump(self.episode_rewards, f)

        if self.debug:
            print(f"Results saved: {self.episode_rewards}")

    def _get_observation(self):
        """
        Konstruuje wektor obserwacji z pozycji i prędkości ciała.
        """
        car_pos = self.car_body.position
        car_vel = self.car_body.linearVelocity
        wheel_angle1 = self.joint1.angle
        wheel_angle2 = self.joint2.angle

        return np.array(
            [car_pos[0],
             car_pos[1],
             car_vel[0],
             car_vel[1],
             wheel_angle1,
             wheel_angle2],
            dtype=np.float32
        )
