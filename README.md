# Soccer Simulation

## Installation
```
uv sync
```

## How it works

This project is a simple soccer simulation that uses a Deep Q-Network (DQN) to train an agent to play soccer.

The simulation consists of two teams, each with 11 players. The DQN agent is trained to control one of the teams.

### Training

During training, the agent plays the game for a specified number of episodes. In each episode, it takes actions and receives rewards based on its performance. The reward function is designed to encourage the agent to score goals.

The agent stores its experiences (state, action, reward, next state, done) in a memory buffer and uses a process called "replay" to learn from these experiences and improve its decision-making.

The training results (episode number and score) are saved to `src/storage/statistics/training_results.json`.

### Testing

During testing, a pre-trained agent is loaded and plays against an untrained agent. The final score of the game is printed to the console.

### Simulation

You can also run a number of simulations between a trained and an untrained agent. The results of these simulations (episode number and score) are saved to `src/storage/statistics/simulation_results.json`.

## How to train

```bash
uv run -m src.main --train [n]
```

This will train the agent for `n` episodes.

## How to test

```bash
uv run -m src.main --test
```

This will run a single simulation between a trained and an untrained agent and print the final score.

## How to simulate

```bash
uv run -m src.main --simulate [n]
```

This will run `n` simulations between a trained and an untrained agent and save the results to `src/storage/statistics/simulation_results.json`.
