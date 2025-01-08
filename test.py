from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv

# Inicjalizacja środowiska i wczytanie wytrenowanego modelu
env = HillClimbEnv(max_steps=10000, debug=True)
model = PPO.load("quick_ppo_hill_climb")

# Gymnasium: reset zwraca (obs, info)
obs, info = env.reset()

# Dwa boole do monitorowania stanu epizodu wg Gymnasium
terminated = False
truncated = False

total_reward = 0.0

print("Starting the testing of the trained agent...")

while not (terminated or truncated):
    # Model SB3 przewiduje akcję na podstawie stanu obserwacji
    action, _ = model.predict(obs, deterministic=True)

    # Zwróć uwagę, że step w Gymnasium to: obs, reward, terminated, truncated, info
    obs, reward, terminated, truncated, info = env.step(action)

    # Render, jeśli chcesz widzieć przebieg symulacji
    env.render()

    # Zliczaj nagrody
    total_reward += reward

# Na koniec zamknij środowisko (jeśli masz metodę close) i wydrukuj podsumowanie
env.close()
print(f"Test completed. Total reward: {total_reward:.2f}")
