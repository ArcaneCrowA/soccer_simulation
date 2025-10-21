import logging

import numpy as np

from src.logic.bayesian_network import PassSuccessPredictor
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
        self.pass_predictor = PassSuccessPredictor()
        self.ball_owner = None
        self.pass_stats = {}  # {player_id: {"success": 0, "fail": 0}}

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
        elif action == Action.PASS:
            if (
                np.linalg.norm(player.position - self.ball.position)
                < PLAYER_RADIUS + BALL_RADIUS
            ):
                teammates = (
                    self.team1.players if team_id == 1 else self.team2.players
                )
                closest_teammate = min(
                    [p for p in teammates if p.player_id != player.player_id],
                    key=lambda p: np.linalg.norm(p.position - player.position),
                )
                distance = np.linalg.norm(
                    closest_teammate.position - player.position
                )
                passer_speed = np.linalg.norm(player.velocity)

                if passer_speed > 0:
                    player_direction = player.velocity / passer_speed
                    teammate_direction = (
                        closest_teammate.position - player.position
                    ) / distance
                    angle = np.arccos(
                        np.clip(
                            np.dot(player_direction, teammate_direction),
                            -1.0,
                            1.0,
                        )
                    )
                else:
                    angle = 0.0

                opponents = (
                    self.team2.players if team_id == 1 else self.team1.players
                )
                closest_defender = min(
                    opponents,
                    key=lambda p: np.linalg.norm(p.position - player.position),
                )
                defender_proximity = np.linalg.norm(
                    closest_defender.position - player.position
                )
                target_speed = np.linalg.norm(closest_teammate.velocity)

                if distance < 30:
                    pass_type = PassType.SHORT
                else:
                    pass_type = PassType.LONG

                pressure = (
                    1 / defender_proximity if defender_proximity > 0 else 1.0
                )

                pass_success_prob = self.pass_predictor.predict(
                    player.skill,
                    distance,
                    player.role,
                    closest_teammate.role,
                    angle,
                    passer_speed,
                    defender_proximity,
                    target_speed,
                    pass_type,
                    pressure,
                )
                logging.info(
                    f"Pass success probability: {pass_success_prob:.2f}"
                )

                self.intended_recipient = closest_teammate

                direction = closest_teammate.position - self.ball.position
                self.ball.velocity = (
                    direction / np.linalg.norm(direction)
                ) * MAX_BALL_SPEED

        # Check for ball possession
        for p in self.team1.players + self.team2.players:
            if (
                np.linalg.norm(p.position - self.ball.position)
                < PLAYER_RADIUS + BALL_RADIUS
            ):
                if self.ball_owner and self.ball_owner.player_id != p.player_id:
                    if (
                        self.intended_recipient
                        and self.intended_recipient.player_id == p.player_id
                    ):
                        passer_id = self.ball_owner.player_id
                        if passer_id not in self.pass_stats:
                            self.pass_stats[passer_id] = {
                                "success": 0,
                                "fail": 0,
                            }
                        self.pass_stats[passer_id]["success"] += 1
                    elif self.intended_recipient:
                        passer_id = self.ball_owner.player_id
                        if passer_id not in self.pass_stats:
                            self.pass_stats[passer_id] = {
                                "success": 0,
                                "fail": 0,
                            }
                        self.pass_stats[passer_id]["fail"] += 1
                self.ball_owner = p
                self.intended_recipient = None
                break

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
