import math
import random

import pygame
from pygame.math import Vector2


class Player:
    def __init__(
        self, name, accuracy, defence, position, radius, color, team_name
    ):
        self.name = name
        self.accuracy = accuracy
        self.defence = defence
        self.position = Vector2(position)
        self.initial_position = Vector2(position)
        self.velocity = Vector2(0, 0)
        self.radius = radius
        self.color = color
        self.team_name = team_name

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )

    def move_towards(self, target, speed):
        direction = target - self.position
        if direction.length() > 0:
            direction = direction.normalize()
        self.position += direction * speed

    def distance_to(self, pos):
        return self.position.distance_to(pos)

    def can_reach_ball(self, ball, kick_range=15):
        return (
            self.distance_to(ball.position)
            <= self.radius + ball.radius + kick_range
        )

    def kick_ball(self, ball, target_position, kick_power):
        direction = (target_position - ball.position).normalize()
        angle_dev = (1 - self.accuracy) * 90
        deviation = random.uniform(
            -math.radians(angle_dev), math.radians(angle_dev)
        )
        actual_direction = direction.rotate(math.degrees(deviation))
        ball.velocity = actual_direction * kick_power


class Goalkeeper(Player):
    def update(self, ball, screen_width, screen_height):
        penalty_area_width = 150
        if self.team_name == "Real Madrid":
            min_x, max_x = self.radius, penalty_area_width // 2
        else:
            min_x = screen_width - penalty_area_width // 2
            max_x = screen_width - self.radius
        target_x = max(min_x, min(max_x, ball.position.x))
        target_y = max(
            (screen_height - 150) // 2,
            min((screen_height + 150) // 2, ball.position.y),
        )
        self.move_towards(Vector2(target_x, target_y), speed=3)
        if self.can_reach_ball(ball) and (
            (self.team_name == "Real Madrid" and ball.velocity.x < 0)
            or (self.team_name == "Kairat" and ball.velocity.x > 0)
        ):
            ball.velocity *= Vector2(-0.8, 0.8)


class Defender(Player):
    def update(self, ball, screen_width, screen_height):
        halfway = screen_width / 2
        def_x = (
            screen_width // 4
            if self.team_name == "Real Madrid"
            else screen_width - screen_width // 4
        )
        in_half = (
            self.team_name == "Real Madrid" and ball.position.x < halfway
        ) or (self.team_name == "Kairat" and ball.position.x > halfway)
        if in_half and self.distance_to(ball.position) < 200:
            self.move_towards(ball.position, 2.5)
        else:
            self.move_towards(Vector2(def_x, ball.position.y), 1.8)
        if self.can_reach_ball(ball):
            target_x = screen_width * (
                0.6 if self.team_name == "Real Madrid" else 0.4
            )
            self.kick_ball(
                ball, Vector2(target_x, random.uniform(0, screen_height)), 10
            )


class Midfielder(Player):
    def update(self, ball, teammates, screen_width, screen_height):
        halfway = screen_width / 2
        target = Vector2(self.initial_position.x, ball.position.y)
        self.move_towards(target, 2)
        in_half = (
            self.team_name == "Real Madrid" and ball.position.x < halfway + 50
        ) or (self.team_name == "Kairat" and ball.position.x > halfway - 50)
        if self.distance_to(ball.position) < 200 or in_half:
            self.move_towards(ball.position, 2.8)
        if self.can_reach_ball(ball):
            forwards = [
                p for p in teammates if p.__class__.__name__ == "Forwards"
            ]
            if forwards:
                closest = min(
                    forwards, key=lambda f: self.distance_to(f.position)
                )
                if (
                    self.team_name == "Real Madrid"
                    and closest.position.x > self.position.x - 20
                ) or (
                    self.team_name == "Kairat"
                    and closest.position.x < self.position.x + 20
                ):
                    self.kick_ball(ball, closest.position, 12)
                    return
            x_target = screen_width * (
                0.75 if self.team_name == "Real Madrid" else 0.25
            )
            self.kick_ball(
                ball, Vector2(x_target, random.uniform(0, screen_height)), 10
            )


class Forwards(Player):
    def update(self, ball, teammates, screen_width, screen_height):
        halfway = screen_width / 2
        opponent_goal_x = screen_width if self.team_name == "Real Madrid" else 0
        attack_x = screen_width * (
            0.75 if self.team_name == "Real Madrid" else 0.25
        )
        self.move_towards(Vector2(attack_x, ball.position.y), 2.5)
        if (self.team_name == "Real Madrid" and ball.position.x > halfway) or (
            self.team_name == "Kairat" and ball.position.x < halfway
        ):
            self.move_towards(ball.position, 3)
        if self.can_reach_ball(ball):
            in_range = (
                self.team_name == "Real Madrid"
                and self.position.x > screen_width * 0.8
            ) or (
                self.team_name == "Kairat"
                and self.position.x < screen_width * 0.2
            )
            goal_center = Vector2(opponent_goal_x, screen_height / 2)
            if in_range:
                self.kick_ball(ball, goal_center, 20)
            else:
                self.kick_ball(
                    ball,
                    Vector2(opponent_goal_x, random.uniform(0, screen_height)),
                    15,
                )
