import pygame
from pygame.math import Vector2

import constants


class Ball:
    def __init__(self, position: tuple, radius: int, color: tuple):
        self.position = Vector2(position)
        self.radius = radius
        self.color = color
        self._velocity = Vector2(0, 0)

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        if isinstance(value, (int, float)):
            value = Vector2(0, 0)  # auto-correct invalid velocity
        elif not isinstance(value, Vector2):
            print("⚠️ Velocity assigned invalid type:", type(value))
            value = Vector2(0, 0)
        self._velocity = value

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

    def check_bounds(self, screen_width, screen_height):
        goal_top = (screen_height - constants.GOAL_HEIGHT) // 2
        goal_bottom = (screen_height + constants.GOAL_HEIGHT) // 2

        bounced = False

        # Left/right walls — skip goal areas
        if self.position.x - self.radius < 0:
            if not goal_top < self.position.y < goal_bottom:
                self.position.x = self.radius
                self.velocity.x *= -0.8
                bounced = True
        elif self.position.x + self.radius > screen_width:
            if not goal_top < self.position.y < goal_bottom:
                self.position.x = screen_width - self.radius
                self.velocity.x *= -0.8
                bounced = True

        # Top/bottom walls
        if self.position.y - self.radius < 0:
            self.position.y = self.radius
            self.velocity.y *= -0.8
            bounced = True
        elif self.position.y + self.radius > screen_height:
            self.position.y = screen_height - self.radius
            self.velocity.y *= -0.8
            bounced = True

        if bounced and self.velocity.length() < 0.5:
            self.velocity = Vector2(0, 0)
