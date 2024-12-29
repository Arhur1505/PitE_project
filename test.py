from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv

env = HillClimbEnv(max_steps=10000, debug=False)
model = PPO.load("quick_ppo_hill_climb.zip")

obs, info = env.reset()
done = False
truncated = False
total_reward = 0

print("Starting the testing of the trained agent...")

while not done:
    action, _ = model.predict(obs)
    obs, reward, done, truncated, info = env.step(action)
    env.render()
    total_reward += reward

env.close()
print(f"Test completed. Total reward: {total_reward:.2f}")
