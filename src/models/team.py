from src.models.player import Player


class Team:
    def __init__(self, team_id: int, players: list[Player]):
        self.team_id = team_id
        self.players = players
        self.score = 0
