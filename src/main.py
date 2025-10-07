import sys

import pygame

import constants
from models.ball import Ball
from models.players import Forwards, Midfielder
from models.team import Team
from utils import draw_field, draw_scores, draw_timer

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
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    for player in real_madrid.team_members:
        if isinstance(player, (Midfielder, Forwards)):
            player.update(
                ball,
                real_madrid.team_members,
                constants.SCREEN_WIDTH,
                constants.SCREEN_HEIGHT,
            )
        else:
            player.update(ball, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

    for player in kairat.team_members:
        if isinstance(player, (Midfielder, Forwards)):
            player.update(
                ball,
                kairat.team_members,
                constants.SCREEN_WIDTH,
                constants.SCREEN_HEIGHT,
            )
        else:
            player.update(ball, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

    ball.move()

    # --- Collision & Goals ---
    goal_top, goal_bottom = (
        (constants.SCREEN_HEIGHT - constants.GOAL_HEIGHT) // 2,
        (constants.SCREEN_HEIGHT + constants.GOAL_HEIGHT) // 2,
    )
    goal_scored = False
    if (
        ball.position.x - ball.radius < 0
        and goal_top < ball.position.y < goal_bottom
    ):
        kairat.score += 1
        goal_scored = True
    elif (
        ball.position.x + ball.radius > constants.SCREEN_WIDTH
        and goal_top < ball.position.y < goal_bottom
    ):
        real_madrid.score += 1
        goal_scored = True

    if goal_scored:
        ball.position = pygame.Vector2(
            constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT // 2
        )
        ball.velocity = pygame.Vector2(0, 0)
        for t in (real_madrid, kairat):
            for p in t.team_members:
                p.position = p.initial_position.copy()
        pygame.time.wait(1000)

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
