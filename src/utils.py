import pygame

import constants


def draw_field(screen):
    """Draw soccer field and markings."""
    screen.fill(constants.GREEN)
    # Slightly bigger size
    pygame.draw.rect(
        screen,
        constants.GREEN,
        (0, 0, constants.FIELD_WIDTH, constants.FIELD_HEIGHT),
        constants.LINE_THICKNESS,
    )
    # Outer field
    pygame.draw.rect(
        screen,
        constants.WHITE,
        (0, 0, constants.FIELD_WIDTH, constants.FIELD_HEIGHT),
        constants.LINE_THICKNESS,
    )

    # Midfield line
    pygame.draw.line(
        screen,
        constants.WHITE,
        (constants.FIELD_WIDTH // 2, 0),
        (constants.FIELD_WIDTH // 2, constants.FIELD_HEIGHT),
        constants.LINE_THICKNESS,
    )

    # Center circle and dot
    pygame.draw.circle(
        screen,
        constants.WHITE,
        (constants.FIELD_WIDTH // 2, constants.FIELD_HEIGHT // 2),
        constants.CENTER_CIRCLE_RADIUS,
        constants.LINE_THICKNESS,
    )
    pygame.draw.circle(
        screen,
        constants.WHITE,
        (constants.FIELD_WIDTH // 2, constants.FIELD_HEIGHT // 2),
        constants.LINE_THICKNESS // 2,
    )

    # Penalty areas
    left_rect = pygame.Rect(
        0,
        (constants.FIELD_HEIGHT - constants.PENALTY_AREA_LENGTH) // 2,
        constants.PENALTY_AREA_WIDTH,
        constants.PENALTY_AREA_LENGTH,
    )
    right_rect = pygame.Rect(
        constants.FIELD_WIDTH - constants.PENALTY_AREA_WIDTH,
        (constants.FIELD_HEIGHT - constants.PENALTY_AREA_LENGTH) // 2,
        constants.PENALTY_AREA_WIDTH,
        constants.PENALTY_AREA_LENGTH,
    )
    pygame.draw.rect(
        screen, constants.WHITE, left_rect, constants.LINE_THICKNESS
    )
    pygame.draw.rect(
        screen, constants.WHITE, right_rect, constants.LINE_THICKNESS
    )

    # Goals
    left_goal = pygame.Rect(
        0,
        (constants.FIELD_HEIGHT - constants.GOAL_HEIGHT) // 2,
        constants.GOAL_WIDTH,
        constants.GOAL_HEIGHT,
    )
    right_goal = pygame.Rect(
        constants.FIELD_WIDTH - constants.GOAL_WIDTH,
        (constants.FIELD_HEIGHT - constants.GOAL_HEIGHT) // 2,
        constants.GOAL_WIDTH,
        constants.GOAL_HEIGHT,
    )
    pygame.draw.rect(
        screen, constants.WHITE, left_goal, constants.LINE_THICKNESS
    )
    pygame.draw.rect(
        screen, constants.WHITE, right_goal, constants.LINE_THICKNESS
    )


def draw_scores(screen, real_madrid, kairat):
    real_text = constants.FONT.render(
        f"Real Madrid: {real_madrid.score}", True, constants.RED
    )
    kairat_text = constants.FONT.render(
        f"Kairat: {kairat.score}", True, constants.YELLOW
    )
    screen.blit(real_text, (20, 20))
    screen.blit(
        kairat_text, (constants.FIELD_WIDTH - kairat_text.get_width() - 20, 20)
    )


def draw_timer(screen, elapsed_seconds):
    minutes = int(elapsed_seconds) // 60
    seconds = int(elapsed_seconds) % 60
    time_text = constants.FONT.render(
        f"{minutes:02}:{seconds:02}", True, constants.WHITE
    )
    screen.blit(time_text, (constants.FIELD_WIDTH // 2 - 25, 20))
