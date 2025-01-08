from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv

# Ścieżka do najlepszego modelu
BEST_MODEL_PATH = "./logs/best_model/best_model.zip"

# Załaduj środowisko
env = HillClimbEnv(max_steps=10000, debug=False)

# Załaduj najlepszy model
model = PPO.load(BEST_MODEL_PATH)

# Resetuj środowisko i pobierz tylko `obs`
obs, _ = env.reset()
done = False
total_reward = 0

print("Starting the testing of the trained agent...")

# Testowanie modelu
while not done:
    # Przewidywanie akcji na podstawie obserwacji
    action, _ = model.predict(obs)
    # Wykonaj krok
    obs, reward, done, truncated, info = env.step(action)
    env.render()
    total_reward += reward

env.close()
print(f"Test completed. Total reward: {total_reward:.2f}")
