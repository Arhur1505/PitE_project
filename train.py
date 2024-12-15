from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from hill_climb_env import HillClimbEnv


def make_env():
    return Monitor(HillClimbEnv(max_steps=10000, debug=False))


env = DummyVecEnv([make_env])
eval_env = DummyVecEnv([make_env])

eval_callback = EvalCallback(
    eval_env,
    best_model_save_path="./logs/",
    log_path="./logs/",
    eval_freq=5000,
    deterministic=True,
    render=False,
)

model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    n_steps=2048,
    batch_size=64,
    gamma=0.99,
    learning_rate=0.0003,
    tensorboard_log="./ppo_tensorboard/"
)

model.learn(total_timesteps=200000, callback=eval_callback)
model.save("ppo_hill_climb")
