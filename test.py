from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv

# Wczytujemy środowisko
env = HillClimbEnv(max_steps=10000, debug=False)

# Wczytujemy wytrenowany model
model = PPO.load("ppo_hill_climb")

# Resetujemy środowisko
obs = env.reset()
done = False
total_reward = 0

# Jednorazowa gra
while not done:
    # Model przewiduje akcję
    action, _ = model.predict(obs)

    # Wykonujemy krok w środowisku
    obs, reward, done, info = env.step(action)

    # Renderowanie gry
    env.render()

    # Sumujemy nagrody
    total_reward += reward

# Zamykamy środowisko
env.close()

# Wyświetlamy wyniki
print(f"Total Reward: {total_reward:.2f}")
