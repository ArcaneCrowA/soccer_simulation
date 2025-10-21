import numpy as np

from src.logic.constants import FIELD_HEIGHT, FIELD_WIDTH, MAX_PLAYER_SPEED
from src.models import Action, Ball, Player, Team


class Game:
    def __init__(self, team1: Team, team2: Team):
        self.team1 = team1
        self.team2 = team2
        self.ball = Ball(np.array([FIELD_WIDTH / 2, FIELD_HEIGHT / 2]))
        self.ticks = 0

    def get_state(self):
        # Simplified state: ball position and first player's position
        player_pos = self.team1.players[0].position
        return np.concatenate([self.ball.position, player_pos])

    def step(self, player: Player, action: Action):
        # Update player velocity based on action
        if action == Action.MOVE_UP:
            player.velocity = np.array([0, -MAX_PLAYER_SPEED])
        elif action == Action.MOVE_DOWN:
            player.velocity = np.array([0, MAX_PLAYER_SPEED])
        elif action == Action.MOVE_LEFT:
            player.velocity = np.array([-MAX_PLAYER_SPEED, 0])
        elif action == Action.MOVE_RIGHT:
            player.velocity = np.array([MAX_PLAYER_SPEED, 0])
        elif action == Action.SHOOT:
            # TODO: Implement shooting logic
            pass

        # Move players
        for p in self.team1.players + self.team2.players:
            p.move()

        # Move ball
        self.ball.move()

        # TODO: Implement collision detection and other game logic

        self.ticks += 1
