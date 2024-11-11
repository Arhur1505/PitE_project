# train_agent.py

import gym
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy
from src.environment import HillClimbRacingEnv

def main():
    env = HillClimbRacingEnv()

    # Trenowanie agenta
    model = DQN('MlpPolicy', env, verbose=1, learning_rate=1e-3, buffer_size=50000, learning_starts=1000)
    model.learn(total_timesteps=50000)

    # Zapisywanie modelu
    model.save("hill_climb_racing_dqn")

    # Ewaluacja agenta
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
    print(f"Mean reward: {mean_reward}, Std reward: {std_reward}")

    # Testowanie agenta
    obs = env.reset()
    for _ in range(1000):
        action, _ = model.predict(obs)
        obs, reward, done, info = env.step(action)
        env.render()
        if done:
            obs = env.reset()

if __name__ == "__main__":
    main()
