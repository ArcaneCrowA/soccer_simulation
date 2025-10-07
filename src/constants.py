import pygame

# Screen dimensions
SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 680

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BALL_COLOR = (255, 255, 255)

# Field markings
LINE_THICKNESS = 5
GOAL_WIDTH = 50
GOAL_HEIGHT = 150
PENALTY_AREA_WIDTH = 150
PENALTY_AREA_LENGTH = 300
CENTER_CIRCLE_RADIUS = 60

# Frame rate
FPS = 60

# Game timing
ROUND_DURATION = 45  # seconds
MAX_ROUNDS = 2
COUNTDOWN_TIME = 3

pygame.font.init()
FONT = pygame.font.Font(None, 36)
SPEED = 3
