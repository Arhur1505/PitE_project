from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO
from hill_climb_env import HillClimbEnv


def make_env():
    return HillClimbEnv(max_steps=5000, debug=False)


env = DummyVecEnv([make_env])

model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    n_steps=512,
    batch_size=32,
    gamma=0.95,
    learning_rate=0.001,
)

model.learn(total_timesteps=50000)
model.save("quick_ppo_hill_climb")
