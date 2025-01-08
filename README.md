# Hill Climb Racing-Inspired Game

A Python-based game inspired by **Hill Climb Racing**, featuring integration of **Reinforcement Learning** using Stable-Baselines3 and OpenAI Gym. The project combines realistic physics-based gameplay with AI-driven decision-making to create an engaging and educational experience.

---

## About the Project

This project is a game inspired by the popular *Hill Climb Racing*, enhanced with **Reinforcement Learning** capabilities. Players can either manually control the vehicle or allow an AI agent to autonomously play and optimize its performance through training.

The primary goal is to explore the intersection of game development and machine learning, providing a platform for experimentation with AI techniques in a simulated environment.

---

## Project Structure

```
.
├── car.py                 # Handles car object creation and physics
├── game.py                # Rendering logic for the game
├── hill_climb_env.py      # Custom Gym environment for Hill Climb Racing
├── physics.py             # Physics simulation and world creation
├── settings.py            # Game settings and constants
├── quick_train.py         # Script for training the RL agent
├── test.py                # Script for testing the trained agent
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── logs/                  # Directory for logs and best models
├── ppo_tensorboard/       # Directory for TensorBoard logs
└── quick_ppo_hill_climb.zip # Trained model
```