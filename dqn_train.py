from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from modules.dqn_env import HillClimbEnv

env = Monitor(HillClimbEnv(max_steps=1000, debug=False))
vec_env = DummyVecEnv([lambda: env])

tensorboard_dir = "./tensorboard/"

model = DQN(
    "MlpPolicy",
    vec_env,
    learning_rate=1e-4,
    buffer_size=50000,
    learning_starts=1000,
    batch_size=32,
    target_update_interval=500,
    train_freq=4,
    gamma=0.99,
    verbose=1,
    tensorboard_log=tensorboard_dir,
)

model.learn(total_timesteps=500000, log_interval=10)
model.save("models/dqn_hill_climb")

obs, _ = env.reset()
for _ in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, _ = env.step(action)
    env.render()
    if done or truncated:
        obs, _ = env.reset()