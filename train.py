from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv

# Tworzymy środowisko
env = HillClimbEnv(max_steps=5000, debug=False)

# Tworzymy model PPO
model = PPO("MlpPolicy", env, verbose=1)

# Trening agenta
model.learn(total_timesteps=100000)

# Zapisujemy model
model.save("ppo_hill_climb")

# Testowanie agenta
obs = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, done, info = env.step(action)
    env.render()

env.close()
