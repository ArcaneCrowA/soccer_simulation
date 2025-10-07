import pygame
from pygame.math import Vector2


class Ball:
    def __init__(self, position: tuple, radius: int, color: tuple):
        self.position = Vector2(position)
        self.radius = radius
        self.color = color
        self.velocity = Vector2(0, 0)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )

    def move(self):
        self.position += self.velocity
        # Apply simple friction
        self.velocity *= 0.98
        # Limit speed
        if self.velocity.length() > 25:
            self.velocity.scale_to_length(25)
