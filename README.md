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
├── logs/                   # Directory for logs and evaluation metrics
│   ├── evaluations.npz     # Evaluation metrics for trained models
├── models/                 # Directory for saved models
│   ├── dqn_hill_climb.zip  # DQN model after training
│   ├── ppo_best_model.zip  # Best-trained PPO model during evaluation
│   ├── ppo_model.zip       # PPO model after training
├── modules/                # Core modules for game logic and environment
│   ├── __init__.py         # Module initializer
│   ├── car.py              # Handles car object creation
│   ├── dqn_env.py          # Gym environment for DQN training
│   ├── game.py             # Rendering logic for the game
│   ├── physics.py          # Physics simulation and world creation
│   ├── ppo_env.py          # Gym environment for PPO training
│   └── settings.py         # Game settings and constants
├── tensorboard/            # Directory for TensorBoard logs
├── dqn_test.py             # Script for testing the DQN agent
├── dqn_train.py            # Script for training the DQN agent
├── main.py                 # Main script to run the game
├── ppo_test.py             # Script for testing the PPO agent
├── ppo_train.py            # Script for training the PPO agent
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## Getting Started

### Prerequisites

Ensure you have Python installed (version 3.8 or later). Install the required dependencies using:

```bash
pip install -r requirements.txt
```

### Running the Game

To manually control the vehicle and play the game:

```bash
python main.py
```

### Training the AI Agent

To train the AI agent using PPO:

```bash
python ppo_train.py
```

To train the AI agent using DQN:

```bash
python dqn_train.py
```

This will save the best model in the `models/` directory.

### Testing the AI Agent

To test the trained PPO model:

```bash
python ppo_test.py
```

To test the trained DQN model:

```bash
python dqn_test.py
```

### Viewing TensorBoard Logs

To visualize the training process using TensorBoard:

```bash
tensorboard --logdir=tensorboard/
```

---

## Key Features

- **Realistic Physics**: Simulates accurate vehicle dynamics.
- **Custom Environment**: A Gym-compatible environment for Reinforcement Learning.
- **Reinforcement Learning**: Train AI agents using PPO and DQN from Stable-Baselines3.
- **Visualization**: Includes TensorBoard integration for training monitoring.
- **Modular Design**: Easy-to-understand and extensible code structure.

---

## Acknowledgments

- Inspired by the popular *Hill Climb Racing* game.
- Built with Python, OpenAI Gym, Stable-Baselines3, and Pygame.

