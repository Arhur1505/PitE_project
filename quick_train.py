import time
import os
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from hill_climb_env import HillClimbEnv

if __name__ == "__main__":
    try:
        log_dir = "./logs/"
        best_model_dir = os.path.join(log_dir, "best_model/")
        tensorboard_dir = "./ppo_tensorboard/"

        os.makedirs(best_model_dir, exist_ok=True)
        os.makedirs(tensorboard_dir, exist_ok=True)

        train_env = Monitor(HillClimbEnv(max_steps=1000, debug=False))
        train_env = DummyVecEnv([lambda: train_env])

        eval_env = Monitor(HillClimbEnv(max_steps=1000, debug=False))
        eval_env = DummyVecEnv([lambda: eval_env])

        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=best_model_dir,
            log_path=log_dir,
            eval_freq=5000,
            deterministic=True,
            render=False,
        )

        # Initialize PPO model
        model = PPO(
            "MlpPolicy",
            train_env,
            verbose=1,
            device="cpu",
            n_steps=4096,
            batch_size=512,
            learning_rate=0.0001,
            ent_coef=0.01,
            policy_kwargs=dict(net_arch=[128, 128]),
            tensorboard_log=tensorboard_dir
        )

        print("Starting training...")
        start_time = time.time()

        model.learn(
            total_timesteps=50000,
            callback=eval_callback
        )

        end_time = time.time()
        training_time = end_time - start_time

        model.save("ppo_hill_climb")
        print("Training completed. Model saved.")
        print(f"Training time: {training_time:.2f} seconds.")

    except Exception as e:
        print("An error occurred during training:")
        print(e)