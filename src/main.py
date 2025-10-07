import argparse
import os
import sys
import time

import pygame
from pygame import Vector2

import constants
from models.ball import Ball
from models.players import Defender, Goalkeeper, Midfielder
from models.team import Team
from utils import draw_field, draw_scores, draw_timer

# --- Helper Functions for RL ---


def get_player_state(player, ball, team, opponent_team):
    """Gets the state for a player based on their type."""
    if isinstance(player, Goalkeeper):
        return player.get_state(
            ball,
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            team.team_members,
        )
    elif isinstance(player, Defender):
        return player.get_state(
            ball,
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            opponent_team.team_members,
        )
    else:  # Midfielder and Forwards
        return player.get_state(
            ball,
            team.team_members,
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
        )


def calculate_reward(
    player, ball, team_members, goal_scored_team_name, team_name
):
    """Calculates the reward for a player's last action."""
    reward = 0
    # Penalty for being out of bounds
    if not (
        5 < player.position.x < constants.SCREEN_WIDTH - 5
        and 5 < player.position.y < constants.SCREEN_HEIGHT - 5
    ):
        reward -= 0.09

    # Reward for distance from other midfielders
    if isinstance(player, Midfielder):
        min_dist = float("inf")
        for mate in team_members:
            if mate is not player and isinstance(mate, Midfielder):
                min_dist = min(min_dist, player.distance_to(mate.position))
        if min_dist < 75:
            reward -= 0.2
        else:
            reward += 0.05

    # Main game objective rewards
    if goal_scored_team_name:
        reward += 5 if goal_scored_team_name == team_name.lower() else -5
    elif player.can_reach_ball(ball):
        reward += 0.3
    elif player.distance_to(ball.position) < 150:
        reward += 0.2
    else:
        reward -= 0.02

    return reward


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

                    current_state = get_player_state(
                        player, ball, team, opponent_team
                    )

                    if player in player_memory:
                        prev_state, prev_action = player_memory[player]
                        reward = calculate_reward(
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

    # --- Save Models ---
    print("Training complete. Saving models...")
    for player in all_players:
        model_path = f"models/{player.name.replace(' ', '_')}_dqn.pth"
        player.save_model(model_path)
        print(f"Saved model for {player.name} to {model_path}")


def run_simulation(load_models=False):
    """Runs the simulation with graphical output."""
    pygame.init()
    pygame.display.set_caption("Soccer Simulation")
    SCREEN = pygame.display.set_mode(
        (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    )
    CLOCK = pygame.time.Clock()

    # Initialize game objects
    real_madrid = Team("Real Madrid", constants.RED, 0.8, 0.7)
    kairat = Team("Kairat", constants.YELLOW, 0.6, 0.5)
    real_madrid.create_players(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    kairat.create_players(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    all_players = real_madrid.team_members + kairat.team_members
    ball = Ball(
        (constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2),
        7,
        constants.BALL_COLOR,
    )

    if load_models:
        print("Loading pre-trained models for simulation...")
        for player in all_players:
            model_path = f"models/{player.name.replace(' ', '_')}_dqn.pth"
            if os.path.exists(model_path):
                try:
                    player.load_model(model_path, for_training=False)
                except Exception as e:
                    print(f"Could not load model for {player.name}: {e}")
            else:
                print(
                    f"Warning: Model file not found for {player.name}. Using untrained model."
                )

    # Game state variables
    current_round = 1
    time_offset = 0.0
    last_time = time.time()
    countdown_active = True
    countdown_start_time = time.time()
    player_memory = {}

    running = True
    while running:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        if not countdown_active:
            time_offset += delta_time

        round_elapsed_time = (
            time_offset - (current_round - 1) * constants.ROUND_DURATION
        )

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        if countdown_active:
            countdown_elapsed = current_time - countdown_start_time
            countdown_left = constants.COUNTDOWN_TIME - countdown_elapsed
            draw_field(SCREEN)
            draw_scores(SCREEN, real_madrid, kairat)
            draw_timer(SCREEN, time_offset)
            if countdown_left > 0:
                font = pygame.font.SysFont(None, 96)
                text = font.render(
                    str(int(countdown_left) + 1), True, constants.WHITE
                )
                SCREEN.blit(
                    text,
                    (
                        constants.SCREEN_WIDTH // 2 - 25,
                        constants.SCREEN_HEIGHT // 2 - 25,
                    ),
                )
                pygame.display.flip()
                CLOCK.tick(constants.FPS)
                continue
            else:
                countdown_active = False
                last_time = time.time()

        if round_elapsed_time >= constants.ROUND_DURATION:
            if current_round < constants.MAX_ROUNDS:
                current_round += 1
                for team in (real_madrid, kairat):
                    team.reset_positions()
                ball.position = Vector2(
                    constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2
                )
                ball.velocity = Vector2(0, 0)
                countdown_active = True
                countdown_start_time = time.time()
                continue
            else:
                draw_field(SCREEN)
                font = pygame.font.SysFont(None, 72)
                text = font.render("GAME OVER", True, (255, 0, 0))
                SCREEN.blit(
                    text,
                    (
                        constants.SCREEN_WIDTH // 2 - 150,
                        constants.SCREEN_HEIGHT // 2 - 30,
                    ),
                )
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False
                continue

        goal_scored_team_name = None

        for player in all_players:
            team = real_madrid if player in real_madrid.team_members else kairat
            opponent_team = kairat if team is real_madrid else real_madrid
            current_state = get_player_state(player, ball, team, opponent_team)
            if player in player_memory:
                prev_state, prev_action = player_memory[player]
                reward = calculate_reward(
                    player,
                    ball,
                    team.team_members,
                    goal_scored_team_name,
                    team.name,
                )
                done = (
                    round_elapsed_time >= constants.ROUND_DURATION
                    or goal_scored_team_name is not None
                )
                player.remember(
                    prev_state, prev_action, reward, current_state, done
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

        for player in all_players:
            team = real_madrid if player in real_madrid.team_members else kairat
            if isinstance(player, Midfielder):
                player.separate_from_others(
                    team.team_members, min_distance=120, push_strength=2.0
                )
            else:
                player.separate_from_others(team.team_members)
            player.stay_in_zone(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

        ball.move()
        ball.check_bounds(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

        goal_top = (constants.SCREEN_HEIGHT - constants.GOAL_HEIGHT) // 2
        goal_bottom = (constants.SCREEN_HEIGHT + constants.GOAL_HEIGHT) // 2
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

        if goal_scored_team_name:
            print(f"⚽ Goal for {goal_scored_team_name}!")
            ball.position = Vector2(
                constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2
            )
            ball.velocity = Vector2(0, 0)
            for p in all_players:
                p.position = p.start_position.copy()
                p.velocity = Vector2(0, 0)
            player_memory.clear()
            draw_field(SCREEN)
            font = pygame.font.SysFont(None, 96)
            text = font.render(
                f"GOAL for {goal_scored_team_name.upper()}!",
                True,
                (255, 255, 0),
            )
            SCREEN.blit(
                text,
                (
                    constants.SCREEN_WIDTH // 2 - 250,
                    constants.SCREEN_HEIGHT // 2 - 50,
                ),
            )
            draw_scores(SCREEN, real_madrid, kairat)
            pygame.display.flip()
            pygame.time.wait(2000)
            countdown_active = True
            countdown_start_time = time.time()
            continue

        draw_field(SCREEN)
        for p in all_players:
            p.draw(SCREEN)
        ball.draw(SCREEN)
        draw_scores(SCREEN, real_madrid, kairat)
        draw_timer(SCREEN, time_offset)
        pygame.display.flip()
        CLOCK.tick(constants.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train",
        type=int,
        metavar="N",
        help="Train the model for N episodes in headless mode.",
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=10,
        help="Training speed multiplier (default: 10). Processes multiple ticks per iteration.",
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load pre-trained models for simulation.",
    )
    args = parser.parse_args()

    if args.train:
        # In training mode, we don't need the full pygame video setup
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        run_training(args.train, speed_multiplier=args.speed)
    else:
        run_simulation(load_models=args.load)
