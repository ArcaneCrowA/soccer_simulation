import argparse
import json
import os
import random

import numpy as np

from src.logic.constants import FIELD_HEIGHT, FIELD_WIDTH
from src.logic.dqn import DQNAgent
from src.logic.game import Game
from src.models import Action, Player, PlayerRole, Team


def main(number_of_simulations: int, test_model: bool, train_model: bool):
    state_size = 8  # ball_x, ball_y, player_x, player_y, opponent_x, opponent_y, goal_x, goal_y
    action_size = 5  # Example action size (e.g., move_up, move_down, move_left, move_right, pass)

    agent_trained = DQNAgent(state_size, action_size)
    agent_opponent = DQNAgent(state_size, action_size)

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
        agent_trained.load("./src/storage/models/soccer_dqn.pth")
        agent_trained.epsilon = 0.0

        game = Game(team1, team2)
        state = game.get_state()
        for time in range(500):
            action_trained = agent_trained.act(state)
            action_untrained = agent_opponent.act(state)
            _, done = game.step(team1.players[0], Action(action_trained), 1)
            if done:
                break
            _, done = game.step(team2.players[0], Action(action_untrained), 2)
            if done:
                break
            state = game.get_state()

        print(f"Final score: {game.score}")

    elif train_model:
        print("Training model...")
        if os.path.exists("./src/storage/models/soccer_dqn.pth"):
            agent_trained.load("./src/storage/models/soccer_dqn.pth")

        results = []
        if os.path.exists("./src/storage/statistics/training_results.json"):
            with open(
                "./src/storage/statistics/training_results.json", "r"
            ) as f:
                results = json.load(f)

        pass_stats = {}
        if os.path.exists("./src/storage/player_stats.json"):
            with open("./src/storage/player_stats.json", "r") as f:
                pass_stats = json.load(f)

        opponent_models_dir = "./src/storage/models/opponents"
        os.makedirs(opponent_models_dir, exist_ok=True)

        goal_pos = np.array([FIELD_WIDTH, FIELD_HEIGHT / 2])
        opponent_goal_pos = np.array([0, FIELD_HEIGHT / 2])

        for e in range(number_of_simulations):
            opponent_models = os.listdir(opponent_models_dir)
            if opponent_models:
                opponent_model_path = os.path.join(
                    opponent_models_dir, random.choice(opponent_models)
                )
                agent_opponent.load(opponent_model_path)
            else:
                agent_opponent = DQNAgent(state_size, action_size)

            game = Game(team1, team2)
            state = game.get_state()
            for time in range(500):
                action_trained = agent_trained.act(state)
                action_opponent = agent_opponent.act(state)

                dist_before = np.linalg.norm(game.ball.position - goal_pos)
                reward_trained, done_trained = game.step(
                    team1.players[0], Action(action_trained), 1
                )
                dist_after = np.linalg.norm(game.ball.position - goal_pos)

                reward_trained += dist_before - dist_after

                dist_before = np.linalg.norm(
                    game.ball.position - opponent_goal_pos
                )
                reward_opponent, done_opponent = game.step(
                    team2.players[0], Action(action_opponent), 2
                )
                dist_after = np.linalg.norm(
                    game.ball.position - opponent_goal_pos
                )
                reward_opponent += dist_before - dist_after

                done = done_trained or done_opponent

                next_state = game.get_state()
                agent_trained.remember(
                    state, action_trained, reward_trained, next_state, done
                )
                agent_opponent.remember(
                    state, action_opponent, reward_opponent, next_state, done
                )

                state = next_state

                if done:
                    break

            if len(agent_trained.memory) > 32:
                agent_trained.replay(32)
            if len(agent_opponent.memory) > 32:
                agent_opponent.replay(32)

            if (e + 1) % 100 == 0:
                agent_trained.save(
                    os.path.join(opponent_models_dir, f"model_{e + 1}.pth")
                )

            print(
                f"episode: {e + 1}/{number_of_simulations}, score: {game.score}, e: {agent_trained.epsilon:.2}"
            )
            results.append({"episode": len(results) + 1, "score": game.score})

            for player_id, stats in game.pass_stats.items():
                if player_id not in pass_stats:
                    pass_stats[player_id] = {"success": 0, "fail": 0}
                pass_stats[player_id]["success"] += stats["success"]
                pass_stats[player_id]["fail"] += stats["fail"]

        for player in team1.players + team2.players:
            player_id = str(player.player_id)
            if player_id in pass_stats:
                total_passes = (
                    pass_stats[player_id]["success"]
                    + pass_stats[player_id]["fail"]
                )
                if total_passes > 0:
                    player.skill = (
                        pass_stats[player_id]["success"] / total_passes
                    )

        agent_trained.save("./src/storage/models/soccer_dqn.pth")
        with open("./src/storage/statistics/training_results.json", "w") as f:
            json.dump(results, f)

        with open("./src/storage/player_stats.json", "w") as f:
            json.dump(pass_stats, f)

    else:
        print(f"Simulating {number_of_simulations} games.")
        results = []
        if os.path.exists("./src/storage/statistics/simulation_results.json"):
            with open(
                "./src/storage/statistics/simulation_results.json", "r"
            ) as f:
                results = json.load(f)

        agent_trained.load("./src/storage/models/soccer_dqn.pth")
        agent_trained.epsilon = 0.0
        for e in range(number_of_simulations):
            game = Game(team1, team2)
            state = game.get_state()
            for time in range(500):
                action_trained = agent_trained.act(state)
                action_untrained = agent_opponent.act(state)
                _, done = game.step(team1.players[0], Action(action_trained), 1)
                if done:
                    break
                _, done = game.step(
                    team2.players[0], Action(action_untrained), 2
                )
                if done:
                    break
                state = game.get_state()
            results.append({"episode": len(results) + 1, "score": game.score})
            print(
                f"episode: {e + 1}/{number_of_simulations}, score: {game.score}"
            )

        os.makedirs("./src/storage/statistics", exist_ok=True)
        with open("./src/storage/statistics/simulation_results.json", "w") as f:
            json.dump(results, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Soccer simulation",
        description="Simulates soccer results",
    )
    parser.add_argument(
        "-t",
        "--train",
        type=int,
        default=0,
        help="Number of training simulations",
    )
    parser.add_argument(
        "--test", action="store_true", help="Test trained vs untrained model"
    )
    parser.add_argument(
        "-s",
        "--simulate",
        type=int,
        default=0,
        help="Number of simulations to run",
    )
    args = parser.parse_args()
    main(
        args.train or args.simulate,
        args.test,
        args.train > 0,
    )
