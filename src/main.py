import sys

import pygame

from models import Ball, Team

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 680
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Soccer Simulation")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)  # For the soccer field
RED = (255, 0, 0)  # Color for Real Madrid
YELLOW = (255, 255, 0)  # Color for Kairat
BALL_COLOR = (255, 255, 255)  # White

# New constants for field markings
LINE_THICKNESS = 5
GOAL_WIDTH = 50  # Depth of the goal
GOAL_HEIGHT = 150  # Height of the goal mouth
PENALTY_AREA_WIDTH = 150  # How far the penalty area extends into the field
PENALTY_AREA_LENGTH = 300  # Vertical length of the penalty area
CENTER_CIRCLE_RADIUS = 60

# Create teams
real_madrid = Team("Real Madrid", RED, accuracy=0.8, saves=0.7)
kairat = Team("Kairat", YELLOW, accuracy=0.6, saves=0.5)

# Create players for each team
real_madrid.create_players(SCREEN_WIDTH, SCREEN_HEIGHT)
kairat.create_players(SCREEN_WIDTH, SCREEN_HEIGHT)

# Create the ball
ball = Ball(
    position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius=7, color=BALL_COLOR
)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background (soccer field)
    SCREEN.fill(GREEN)

    # Drawing field lines and goals

    # Outer field boundary
    pygame.draw.rect(
        SCREEN, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), LINE_THICKNESS
    )

    # Midfield line
    pygame.draw.line(
        SCREEN,
        WHITE,
        (SCREEN_WIDTH // 2, 0),
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT),
        LINE_THICKNESS,
    )

    # Center circle
    pygame.draw.circle(
        SCREEN,
        WHITE,
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        CENTER_CIRCLE_RADIUS,
        LINE_THICKNESS,
    )

    # Center mark (small dot)
    pygame.draw.circle(
        SCREEN,
        WHITE,
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        LINE_THICKNESS // 2,
    )

    # Left Goal Area (Penalty Box)
    left_penalty_area_rect = pygame.Rect(
        0,
        (SCREEN_HEIGHT - PENALTY_AREA_LENGTH) // 2,
        PENALTY_AREA_WIDTH,
        PENALTY_AREA_LENGTH,
    )
    pygame.draw.rect(SCREEN, WHITE, left_penalty_area_rect, LINE_THICKNESS)

    # Right Goal Area (Penalty Box)
    right_penalty_area_rect = pygame.Rect(
        SCREEN_WIDTH - PENALTY_AREA_WIDTH,
        (SCREEN_HEIGHT - PENALTY_AREA_LENGTH) // 2,
        PENALTY_AREA_WIDTH,
        PENALTY_AREA_LENGTH,
    )
    pygame.draw.rect(SCREEN, WHITE, right_penalty_area_rect, LINE_THICKNESS)

    # Left Goal (outer rectangle representing the goal posts/structure)
    left_goal_rect = pygame.Rect(
        0,
        (SCREEN_HEIGHT - GOAL_HEIGHT) // 2,
        GOAL_WIDTH,
        GOAL_HEIGHT,
    )
    pygame.draw.rect(SCREEN, WHITE, left_goal_rect, LINE_THICKNESS)

    # Right Goal (outer rectangle representing the goal posts/structure)
    right_goal_rect = pygame.Rect(
        SCREEN_WIDTH - GOAL_WIDTH,
        (SCREEN_HEIGHT - GOAL_HEIGHT) // 2,
        GOAL_WIDTH,
        GOAL_HEIGHT,
    )
    pygame.draw.rect(SCREEN, WHITE, right_goal_rect, LINE_THICKNESS)

    # Draw Real Madrid players
    for player in real_madrid.team_members:
        player.draw(SCREEN)

    # Draw Kairat players
    for player in kairat.team_members:
        player.draw(SCREEN)

    # Draw the ball
    ball.draw(SCREEN)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
