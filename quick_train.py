import time
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from hill_climb_env import HillClimbEnv

if __name__ == "__main__":
    env = Monitor(HillClimbEnv(max_steps=1000, debug=False))
    env = DummyVecEnv([lambda: env])

    eval_env = Monitor(HillClimbEnv(max_steps=1000, debug=False))
    eval_env = DummyVecEnv([lambda: eval_env])

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./logs/best_model/",
        log_path="./logs/",
        eval_freq=5000,
        deterministic=True,
        render=False,
    )

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        device="cpu",
        n_steps=4096,
        batch_size=512,
        learning_rate=0.0001,
        ent_coef=0.01,
        policy_kwargs=dict(net_arch=[128, 128]),
        tensorboard_log="./ppo_tensorboard/"
    )

    print("Rozpoczynam trening...")
    start_time = time.time()

    model.learn(
        total_timesteps=50000,
        callback=eval_callback
    )

    end_time = time.time()
    training_time = end_time - start_time

    model.save("ppo_hill_climb")

    print(f"Trening zakończony. Model zapisany.")
    print(f"Czas nauki: {training_time:.2f} sekund.")