from stable_baselines3 import DQN
from modules.ppo_env import HillClimbEnv

env = HillClimbEnv(max_steps=10000, debug=False)

model = DQN.load("models/dqn_hill_climb.zip")

obs, info = env.reset()
terminated = False
truncated = False
total_reward = 0.0

while not (terminated or truncated):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    env.render()
    total_reward += reward

env.close()

print(f"Test completed. Total reward: {total_reward:.2f}")