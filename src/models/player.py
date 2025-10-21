import numpy as np

from src.models.enums import PlayerRole


class Player:
    def __init__(
        self,
        player_id: int,
        team_id: int,
        role: PlayerRole,
        position: np.ndarray,
    ):
        self.player_id = player_id
        self.team_id = team_id
        self.role = role
        self.position = position
        self.velocity = np.zeros(2)

    def move(self):
        self.position += self.velocity
