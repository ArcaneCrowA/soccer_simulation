import argparse
import os

import numpy as np

from src.logic.dqn import DQNAgent
from src.logic.game import Game
from src.models import Action, Player, PlayerRole, Team


def main(number_of_simulations: int, test_model: bool):
    state_size = (
        4  # Example state size (e.g., ball_x, ball_y, player_x, player_y)
    )
    action_size = 5  # Example action size (e.g., move_up, move_down, move_left, move_right, shoot)

    agent = DQNAgent(state_size, action_size)

    team1_players = [
        Player(i, 1, PlayerRole.ATTACKER, np.array([20.0, 20.0]))
        for i in range(11)
    ]
    team2_players = [
        Player(i, 2, PlayerRole.ATTACKER, np.array([85.0, 48.0]))
        for i in range(11)
    ]

    team1 = Team(1, team1_players)
    team2 = Team(2, team2_players)

    if test_model:
        print("Testing model...")
        agent.load("./src/storage/models/soccer_dqn.pth")
        agent.epsilon = 0.0

        for e in range(number_of_simulations):
            game = Game(team1, team2)
            state = game.get_state()
            for time in range(500):
                action = agent.act(state)
                game.step(team1.players[0], Action(action))
                state = game.get_state()
                done = False  # Placeholder for done flag
                if done:
                    break
            print(f"episode: {e + 1}/{number_of_simulations}, score: {time}")
    else:
        print("Training model...")
        for e in range(number_of_simulations):
            game = Game(team1, team2)
            state = game.get_state()
            for time in range(500):
                action = agent.act(state)
                game.step(team1.players[0], Action(action))
                next_state = game.get_state()
                reward = -np.linalg.norm(
                    game.ball.position - team1.players[0].position
                )
                done = False  # Placeholder for done flag
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    break
            if len(agent.memory) > 32:
                agent.replay(32)
            print(
                f"episode: {e + 1}/{number_of_simulations}, score: {time}, e: {agent.epsilon:.2}"
            )
        os.makedirs("./src/storage/models", exist_ok=True)
        agent.save("./src/storage/models/soccer_dqn.pth")

    print(f"Simulating {number_of_simulations} games.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Soccer simulation",
        description="Simulates soccer results",
    )
    parser.add_argument(
        "-t", type=int, default=1, help="uv run -m src.main.py -t [n]"
    )
    parser.add_argument(
        "--test", action="store_true", help="uv run -m src.main.py --test"
    )
    args = parser.parse_args()
    main(args.t, args.test)
