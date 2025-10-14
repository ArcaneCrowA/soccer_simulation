import os

from pygame import Vector2

import constants
import helping

from .models.ball import Ball
from .models.players import Defender, Goalkeeper, Midfielder
from .models.team import Team


def run_training(num_episodes, speed_multiplier=10):
    """
    Runs the simulation in headless mode for training.

    Args:
        num_episodes: Number of training episodes
        speed_multiplier: How much faster to run the simulation (1 = normal speed)
    """
    print(
        f"Starting training for {num_episodes} episodes (speed: {speed_multiplier}x)..."
    )

    # Initialize game objects
    real_madrid = Team("Real Madrid", constants.RED, 0.8, 0.7)
    kairat = Team("Kairat", constants.YELLOW, 0.6, 0.5)
    real_madrid.create_players(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    kairat.create_players(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    all_players = real_madrid.team_members + kairat.team_members

    # Load existing models if they exist
    for player in all_players:
        model_path = f"models/{player.name.replace(' ', '_')}_dqn.pth"
        if os.path.exists(model_path):
            try:
                player.load_model(model_path, for_training=True)
            except Exception as e:
                print(f"Could not load model for {player.name}: {e}")

    for episode in range(num_episodes):
        # --- Episode Setup ---
        ball = Ball(
            (constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2),
            7,
            constants.BALL_COLOR,
        )
        for player in all_players:
            player.position = player.start_position.copy()
            player.velocity = Vector2(0, 0)

        real_madrid.score = 0
        kairat.score = 0

        player_memory = {}
        game_ticks = 0
        max_ticks = int(
            constants.ROUND_DURATION * constants.MAX_ROUNDS * constants.FPS
        )

        # --- Fast, Headless Game Loop for one episode ---
        while game_ticks < max_ticks:
            # Process multiple ticks in a batch for speed
            for _ in range(speed_multiplier):
                if game_ticks >= max_ticks:
                    break

                goal_scored_team_name = None

                # Player decision and action execution
                for player in all_players:
                    team = (
                        real_madrid
                        if player in real_madrid.team_members
                        else kairat
                    )
                    opponent_team = (
                        kairat if team is real_madrid else real_madrid
                    )

                    current_state = helping.get_player_state(
                        player, ball, team, opponent_team
                    )

                    if player in player_memory:
                        prev_state, prev_action = player_memory[player]
                        reward = helping.calculate_reward(
                            player,
                            ball,
                            team.team_members,
                            goal_scored_team_name,
                            team.name,
                        )
                        done = goal_scored_team_name is not None

                        player.remember(
                            prev_state,
                            prev_action,
                            reward,
                            current_state,
                            done,
                        )
                        if hasattr(player, "replay"):
                            player.replay()

                    action = player.choose_action(current_state)
                    player_memory[player] = (current_state, action)

                    if isinstance(player, Goalkeeper):
                        player.update(
                            action,
                            ball,
                            constants.SCREEN_WIDTH,
                            constants.SCREEN_HEIGHT,
                            team.team_members,
                        )
                    elif isinstance(player, Defender):
                        player.update(
                            action,
                            ball,
                            constants.SCREEN_WIDTH,
                            constants.SCREEN_HEIGHT,
                            opponent_team.team_members,
                        )
                    else:
                        player.update(
                            action,
                            ball,
                            team.team_members,
                            constants.SCREEN_WIDTH,
                            constants.SCREEN_HEIGHT,
                            constants.SPEED,
                        )

                # Player positioning and constraints
                for player in all_players:
                    team = (
                        real_madrid
                        if player in real_madrid.team_members
                        else kairat
                    )
                    if isinstance(player, Midfielder):
                        player.separate_from_others(
                            team.team_members,
                            min_distance=120,
                            push_strength=2.0,
                        )
                    else:
                        player.separate_from_others(team.team_members)
                    player.stay_in_zone(
                        constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
                    )

                # Ball physics
                ball.move()
                ball.check_bounds(
                    constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
                )

                # Goal detection
                goal_top = (
                    constants.SCREEN_HEIGHT - constants.GOAL_HEIGHT
                ) // 2
                goal_bottom = (
                    constants.SCREEN_HEIGHT + constants.GOAL_HEIGHT
                ) // 2
                if (
                    ball.position.x - ball.radius <= 0
                    and goal_top <= ball.position.y <= goal_bottom
                ):
                    kairat.score += 1
                    goal_scored_team_name = "kairat"
                elif (
                    ball.position.x + ball.radius >= constants.SCREEN_WIDTH
                    and goal_top <= ball.position.y <= goal_bottom
                ):
                    real_madrid.score += 1
                    goal_scored_team_name = "real_madrid"

                # Reset after goal
                if goal_scored_team_name:
                    ball.position = Vector2(
                        constants.SCREEN_WIDTH // 2,
                        constants.SCREEN_HEIGHT // 2,
                    )
                    ball.velocity = Vector2(0, 0)
                    for p in all_players:
                        p.position = p.start_position.copy()
                        p.velocity = Vector2(0, 0)
                    player_memory.clear()

                game_ticks += 1

        if (episode + 1) % 10 == 0:
            print(
                f"Episode {episode + 1}/{num_episodes} finished. "
                f"Score: {real_madrid.name} {real_madrid.score} - "
                f"{kairat.name} {kairat.score}"
            )

        last_episode = helping.get_last_episode()
        episode_num = last_episode + 1  # continue numbering
        helping.append_score(episode_num, real_madrid, kairat)

    # --- Save Models ---
    print("Training complete. Saving models...")
    for player in all_players:
        model_path = f"models/{player.name.replace(' ', '_')}_dqn.pth"
        player.save_model(model_path)
        print(f"Saved model for {player.name} to {model_path}")
