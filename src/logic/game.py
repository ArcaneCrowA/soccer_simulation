import logging

import numpy as np

from src.logic.constants import (
    BALL_RADIUS,
    FIELD_HEIGHT,
    FIELD_WIDTH,
    MAX_BALL_SPEED,
    MAX_PLAYER_SPEED,
    PLAYER_RADIUS,
)
from src.models import Action, Ball, Player, Team

logging.basicConfig(level=logging.INFO)


class Game:
    def __init__(self, team1: Team, team2: Team):
        self.team1 = team1
        self.team2 = team2
        self.ball = Ball(np.array([FIELD_WIDTH / 2, FIELD_HEIGHT / 2]))
        self.ticks = 0
        self.score = {1: 0, 2: 0}

    def get_state(self):
        player_pos = self.team1.players[0].position
        opponent_pos = self.team2.players[0].position
        goal_pos = np.array([FIELD_WIDTH, FIELD_HEIGHT / 2])
        return np.concatenate(
            [self.ball.position, player_pos, opponent_pos, goal_pos]
        )

    def step(self, player: Player, action: Action, team_id: int):
        logging.info(
            f"Team {team_id} player {player.player_id} action: {action}"
        )
        # Update player velocity based on action
        player.velocity = np.zeros(2)
        if action == Action.MOVE_UP:
            player.velocity = np.array([0, -MAX_PLAYER_SPEED])
        elif action == Action.MOVE_DOWN:
            player.velocity = np.array([0, MAX_PLAYER_SPEED])
        elif action == Action.MOVE_LEFT:
            player.velocity = np.array([-MAX_PLAYER_SPEED, 0])
        elif action == Action.MOVE_RIGHT:
            player.velocity = np.array([MAX_PLAYER_SPEED, 0])
        elif action == Action.SHOOT:
            if (
                np.linalg.norm(player.position - self.ball.position)
                < PLAYER_RADIUS + BALL_RADIUS
            ):
                if team_id == 1:
                    goal_pos = np.array([FIELD_WIDTH, FIELD_HEIGHT / 2])
                else:
                    goal_pos = np.array([0, FIELD_HEIGHT / 2])
                direction = goal_pos - self.ball.position
                self.ball.velocity = (
                    direction / np.linalg.norm(direction)
                ) * MAX_BALL_SPEED

        # Move players
        for p in self.team1.players + self.team2.players:
            p.move()

        # Move ball
        self.ball.move()

        # Check for goal
        reward = 0
        done = False
        if self.ball.position[0] < 0:
            self.score[2] += 1
            reward = -100
            done = True
            logging.info(f"Team 2 scored! Score: {self.score}")
        elif self.ball.position[0] > FIELD_WIDTH:
            self.score[1] += 1
            reward = 100
            done = True
            logging.info(f"Team 1 scored! Score: {self.score}")

        self.ticks += 1
        logging.info(
            f"Ball position: {self.ball.position}, Ball velocity: {self.ball.velocity}"
        )
        return reward, done
