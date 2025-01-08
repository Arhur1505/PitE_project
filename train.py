import gymnasium as gym
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback

from hill_climb_env import HillClimbEnv


def make_env():
    """Funkcja zwracająca pojedyncze środowisko z monitorem."""
    return Monitor(HillClimbEnv(max_steps=10000, debug=True))


if __name__ == "__main__":
    # Tworzymy środowisko treningowe i walidacyjne
    env = DummyVecEnv([make_env])
    eval_env = DummyVecEnv([make_env])

    # Callback do oceny modelu
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./logs/",
        log_path="./logs/",
        eval_freq=5000,
        deterministic=True,
        render=False,
    )

    # Konfiguracja modelu PPO
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        n_steps=2048,
        batch_size=64,
        gamma=0.99,
        learning_rate=0.0003,
        # tensorboard_log="./ppo_tensorboard/"
    )

    print(">>> Rozpoczynam trening PPO...")

    # Uruchamiamy trening
    model.learn(total_timesteps=200000, callback=eval_callback)

    print(">>> Trening zakończony. Zapisuję model...")

    # Zapisanie modelu
    model.save("ppo_hill_climb")

    print(">>> Model zapisany jako 'ppo_hill_climb'.")
