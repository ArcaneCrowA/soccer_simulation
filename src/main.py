import sys
import time

import pygame
from pygame import Vector2

import constants
from models.ball import Ball
from models.players import Forwards, Midfielder
from models.team import Team
from utils import draw_field, draw_scores, draw_timer

GAME_DURATION = 300  # seconds (5 minutes)
RESET_TIME = 60  # reset players when 60 seconds left
COUNTDOWN_TIME = 5  # countdown before each start


start_time = time.time()
countdown_active = True
countdown_start = start_time


pygame.init()
SCREEN = pygame.display.set_mode(
    (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
)
pygame.display.set_caption("Soccer Simulation")
CLOCK = pygame.time.Clock()

real_madrid = Team("Real Madrid", constants.RED, 0.8, 0.7)
kairat = Team("Kairat", constants.YELLOW, 0.6, 0.5)
real_madrid.create_players(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
kairat.create_players(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
ball = Ball(
    (constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2),
    7,
    constants.BALL_COLOR,
)
start_ticks = pygame.time.get_ticks()

running = True
previous_reset_triggered = (
    False  # <-- place this before the loop (after start_time)
)

while running:
    # --- Check for goals ---
    goal_top = (constants.SCREEN_HEIGHT - constants.GOAL_HEIGHT) // 2
    goal_bottom = (constants.SCREEN_HEIGHT + constants.GOAL_HEIGHT) // 2

    current_time = time.time()
    elapsed = current_time - start_time
    remaining_time = max(GAME_DURATION - elapsed, 0)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # --- Handle countdown phase ---
    if countdown_active:
        countdown_elapsed = current_time - countdown_start
        countdown_left = COUNTDOWN_TIME - countdown_elapsed

        # Clear screen before drawing countdown
        draw_field(SCREEN)
        draw_scores(SCREEN, real_madrid, kairat)
        draw_timer(SCREEN, start_ticks)

        if countdown_left > 0:
            font = pygame.font.SysFont(None, 96)
            text = font.render(
                str(int(countdown_left) + 1), True, (255, 255, 255)
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
            continue  # ⛔ Skip gameplay updates
        else:
            countdown_active = False

    # --- Restart game at 60 seconds ---
    if remaining_time == 60:
        real_madrid.score = 0
        kairat.score = 0
        for team in (real_madrid, kairat):
            team.reset_positions()
        ball.position = Vector2(
            constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2
        )
        ball.velocity = Vector2(0, 0)
        start_time = time.time()
        start_ticks = pygame.time.get_ticks()
        countdown_active = True
        countdown_start = time.time()
        previous_reset_triggered = False
        continue

    # --- Handle timed reset at 60 seconds remaining ---
    if remaining_time <= RESET_TIME and not previous_reset_triggered:
        kairat.reset_positions()
        real_madrid.reset_positions()
        ball.position = Vector2(
            constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2
        )
        ball.velocity = Vector2(0, 0)
        countdown_active = True
        countdown_start = time.time()
        previous_reset_triggered = True  # ensure this runs only once
    elif remaining_time > RESET_TIME:
        previous_reset_triggered = False  # allow next reset on future rounds

    # --- End game condition ---
    if remaining_time <= 0:
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

    # --- Team logic ---
    for team in (real_madrid, kairat):
        for player in team.team_members:
            if isinstance(player, (Midfielder, Forwards)):
                player.update(
                    ball,
                    team.team_members,
                    constants.SCREEN_WIDTH,
                    constants.SCREEN_HEIGHT,
                )
            else:
                player.update(
                    ball, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
                )
            player.stay_in_zone(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        for player in team.team_members:
            player.separate_from_others(team.team_members)

    # --- Ball and collisions ---
    ball.move()
    ball.check_bounds(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

    goal_top = (constants.SCREEN_HEIGHT - constants.GOAL_HEIGHT) // 2
    goal_bottom = (constants.SCREEN_HEIGHT + constants.GOAL_HEIGHT) // 2
    goal_scored = None

    # LEFT goal
    if (
        ball.position.x - ball.radius <= 0  # crosses left edge
        and goal_top <= ball.position.y <= goal_bottom  # inside goal range
    ):
        kairat.score += 1
        goal_scored = "kairat"

    # RIGHT goal
    elif (
        ball.position.x + ball.radius >= constants.SCREEN_WIDTH
        and goal_top <= ball.position.y <= goal_bottom
    ):
        real_madrid.score += 1
        goal_scored = "real_madrid"

    # If goal detected → reset and countdown
    if goal_scored:
        print(f"⚽ Goal for {goal_scored}!")

        # reset ball to center
        ball.position = Vector2(
            constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2
        )
        ball.velocity = Vector2(0, 0)

        # reset all players
        for team in (real_madrid, kairat):
            for p in team.team_members:
                p.position = p.start_position.copy()
                p.velocity = Vector2(0, 0)

        # pause and show GOAL text
        draw_field(SCREEN)
        font = pygame.font.SysFont(None, 96)
        text = font.render(
            f"GOAL for {goal_scored.upper()}!", True, (255, 255, 0)
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

        # restart countdown
        countdown_active = True
        countdown_start = time.time()
        start_ticks = pygame.time.get_ticks()
        continue

    # --- Draw Everything ---
    draw_field(SCREEN)
    for t in (real_madrid, kairat):
        for p in t.team_members:
            p.draw(SCREEN)
    ball.draw(SCREEN)
    draw_scores(SCREEN, real_madrid, kairat)
    draw_timer(SCREEN, start_ticks)

    pygame.display.flip()
    CLOCK.tick(constants.FPS)


pygame.quit()
sys.exit()
