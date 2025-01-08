from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv

BEST_MODEL_PATH = "./logs/best_model/best_model.zip"

env = HillClimbEnv(max_steps=10000, debug=False)

model = PPO.load(BEST_MODEL_PATH)

obs, _ = env.reset()
done = False
total_reward = 0

print("Starting the testing of the trained agent...")

while not done:
    action, _ = model.predict(obs)
    obs, reward, done, truncated, info = env.step(action)
    env.render()
    total_reward += reward

env.close()
print(f"Test completed. Total reward: {total_reward:.2f}")