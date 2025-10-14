import os
import sys
import time

import pygame
from pygame import Vector2

from . import constants, helping
from .database import init_db
from .models.ball import Ball
from .models.players import Defender, Goalkeeper, Midfielder
from .models.team import Team
from .statistics import create_pass_network
from .utils import draw_field, draw_scores, draw_timer


def run_simulation(load_models=False):
    """Runs the simulation with graphical output."""
    init_db()
    pygame.init()
    pygame.display.set_caption("Soccer Simulation")
    SCREEN = pygame.display.set_mode(
        (constants.FIELD_WIDTH, constants.FIELD_HEIGHT)
    )
    CLOCK = pygame.time.Clock()

    # Initialize game objects
    real_madrid = Team("Real Madrid", constants.RED, 0.8, 0.7)
    kairat = Team("Kairat", constants.YELLOW, 0.6, 0.5)
    real_madrid.create_players(constants.FIELD_WIDTH, constants.FIELD_HEIGHT)
    kairat.create_players(constants.FIELD_WIDTH, constants.FIELD_HEIGHT)
    all_players = real_madrid.team_members + kairat.team_members
    ball = Ball(
        (constants.FIELD_WIDTH // 2, constants.FIELD_HEIGHT // 2),
        7,
        constants.BALL_COLOR,
    )

    pass_network = create_pass_network()
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
                        constants.FIELD_WIDTH // 2 - 25,
                        constants.FIELD_HEIGHT // 2 - 25,
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
                    constants.FIELD_WIDTH // 2, constants.FIELD_HEIGHT // 2
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
                        constants.FIELD_WIDTH // 2 - 150,
                        constants.FIELD_HEIGHT // 2 - 30,
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
                    constants.FIELD_WIDTH,
                    constants.FIELD_HEIGHT,
                    team.team_members,
                    opponent_team.team_members,
                )
            elif isinstance(player, Defender):
                player.update(
                    action,
                    ball,
                    constants.FIELD_WIDTH,
                    constants.FIELD_HEIGHT,
                    team.team_members,
                    opponent_team.team_members,
                )
            else:
                player.update(
                    action,
                    ball,
                    team.team_members,
                    opponent_team.team_members,
                    constants.FIELD_WIDTH,
                    constants.FIELD_HEIGHT,
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
            player.stay_in_zone(constants.FIELD_WIDTH, constants.FIELD_HEIGHT)

        ball.move()
        ball.check_bounds(constants.FIELD_WIDTH, constants.FIELD_HEIGHT)

        goal_top = (constants.FIELD_HEIGHT - constants.GOAL_HEIGHT) // 2
        goal_bottom = (constants.FIELD_HEIGHT + constants.GOAL_HEIGHT) // 2
        if (
            ball.position.x - ball.radius <= 0
            and goal_top <= ball.position.y <= goal_bottom
        ):
            kairat.score += 1
            goal_scored_team_name = "kairat"
        elif (
            ball.position.x + ball.radius >= constants.FIELD_WIDTH
            and goal_top <= ball.position.y <= goal_bottom
        ):
            real_madrid.score += 1
            goal_scored_team_name = "real_madrid"

        if goal_scored_team_name:
            print(f"Goal for {goal_scored_team_name}!")
            ball.position = Vector2(
                constants.FIELD_WIDTH // 2, constants.FIELD_HEIGHT // 2
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
                    constants.FIELD_WIDTH // 2 - 250,
                    constants.FIELD_HEIGHT // 2 - 50,
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
