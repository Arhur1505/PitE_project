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
│   ├── best_model.zip      # Best-trained model during evaluation
│   ├── ppo_hill_climb.zip  # Final PPO model after training
├── modules/                # Core modules for game logic and environment
│   ├── __init__.py         # Module initializer
│   ├── car.py              # Handles car object creation
│   ├── game.py             # Rendering logic for the game
│   ├── hill_climb_env.py   # Custom Gym environment for Hill Climb Racing
│   ├── physics.py          # Physics simulation and world creation
│   └── settings.py         # Game settings and constants
├── tensorboard/            # Directory for TensorBoard logs
├── main.py                 # Main script to run the game
├── quick_train.py          # Script for training the RL agent
├── test.py                 # Script for testing the trained agent
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
python quick_train.py
```

This will save the best model in the `models/` directory.

### Testing the AI Agent

To test the trained model:

```bash
python test.py
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
- **Reinforcement Learning**: Train AI agents using PPO from Stable-Baselines3.
- **Visualization**: Includes TensorBoard integration for training monitoring.
- **Modular Design**: Easy-to-understand and extensible code structure.

---

## Acknowledgments

- Inspired by the popular *Hill Climb Racing* game.
- Built with Python, OpenAI Gym, Stable-Baselines3, and Pygame.

