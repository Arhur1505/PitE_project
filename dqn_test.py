from stable_baselines3 import DQN
from modules.hill_climb_env import HillClimbEnv

# Inicjalizacja środowiska
env = HillClimbEnv(max_steps=10000, debug=False)

# Wczytanie modelu DQN
model = DQN.load("models/dqn_hill_climb.zip")

# Reset środowiska
obs, info = env.reset()
terminated = False
truncated = False
total_reward = 0.0

# Główna pętla testowa
while not (terminated or truncated):
    # Przewidywanie akcji przy użyciu modelu DQN
    action, _ = model.predict(obs, deterministic=True)

    # Wykonanie akcji w środowisku
    obs, reward, terminated, truncated, info = env.step(action)

    # Renderowanie środowiska
    env.render()

    # Aktualizacja całkowitej nagrody
    total_reward += reward

# Zamknięcie środowiska po zakończeniu testu
env.close()

# Wynik testu
print(f"Test completed. Total reward: {total_reward:.2f}")
