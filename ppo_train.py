import time
import os
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from modules.ppo_env import HillClimbEnv
import os
import shutil

if __name__ == "__main__":
    try:
        log_dir = "./logs/"
        best_model_dir = "models/"
        tensorboard_dir = "./tensorboard/"

        os.makedirs(best_model_dir, exist_ok=True)
        os.makedirs(tensorboard_dir, exist_ok=True)

        train_env = DummyVecEnv([lambda: Monitor(HillClimbEnv(max_steps=1000, debug=False))])
        eval_env = DummyVecEnv([lambda: Monitor(HillClimbEnv(max_steps=1000, debug=False))])

        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path=best_model_dir,
            log_path=log_dir,
            eval_freq=10000,
            deterministic=True,
            render=False,
        )

        model = PPO(
            "MlpPolicy",
            train_env,
            verbose=1,
            device="cpu",
            n_steps=2048,
            batch_size=512,
            learning_rate=0.0001,
            ent_coef=0.01,
            policy_kwargs=dict(net_arch=[128, 128]),
            tensorboard_log=tensorboard_dir
        )

        print("Starting training...")
        start_time = time.time()

        model.learn(
            total_timesteps=500000,
            callback=eval_callback
        )

        end_time = time.time()
        training_time = end_time - start_time

        model.save("models/ppo_model")
        print("Training completed. Model saved.")
        print(f"Training time: {training_time:.2f} seconds.")

        best_model_path = os.path.join(best_model_dir, "best_model.zip")
        custom_model_path = os.path.join(best_model_dir, "ppo_best_model.zip")

        if os.path.exists(best_model_path):
            shutil.move(best_model_path, custom_model_path)
            print(f"Best model renamed to: {custom_model_path}")
        else:
            print("No best model found to rename.")

    except Exception as e:
        print("An error occurred during training:")
        print(e)