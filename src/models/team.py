from pygame import Vector2

from src.models.players import (
    Defender,
    Forwards,
    Goalkeeper,
    Midfielder,
    Player,
)


class Team:
    def __init__(self, name, color, accuracy, saves):
        self.score = 0
        self.name = name
        self.color = color
        self.accuracy = accuracy
        self.saves = saves
        self.team_members: list[Player] = []

    def reset_positions(self):
        for player in self.team_members:
            player.position = Vector2(
                player.start_position
            )  # store this on init
            player.velocity = Vector2(0, 0)

    def create_players(self, screen_width, screen_height):
        r = 10
        gk_y = screen_height // 2
        y4 = [screen_height * (i + 1) // 5 for i in range(4)]
        y2 = [screen_height * (i + 1) // 3 for i in range(2)]
        if self.name == "Real Madrid":
            self.team_members.append(
                Goalkeeper(
                    f"{self.name} GK",
                    self.accuracy,
                    self.saves,
                    (screen_width // 10, gk_y),
                    r,
                    self.color,
                    self.name,
                )
            )
            for i, y in enumerate(y4):
                self.team_members.append(
                    Defender(
                        f"{self.name} D{i + 1}",
                        self.accuracy,
                        self.saves,
                        (screen_width // 5, y),
                        r,
                        self.color,
                        self.name,
                    )
                )
                self.team_members.append(
                    Midfielder(
                        f"{self.name} M{i + 1}",
                        self.accuracy,
                        self.saves,
                        (screen_width // 2 - screen_width // 8, y),
                        r,
                        self.color,
                        self.name,
                    )
                )
            for i, y in enumerate(y2):
                self.team_members.append(
                    Forwards(
                        f"{self.name} F{i + 1}",
                        self.accuracy,
                        self.saves,
                        (screen_width // 2 - screen_width // 6, y),
                        r,
                        self.color,
                        self.name,
                    )
                )
        else:
            self.team_members.append(
                Goalkeeper(
                    f"{self.name} GK",
                    self.accuracy,
                    self.saves,
                    (screen_width - screen_width // 10, gk_y),
                    r,
                    self.color,
                    self.name,
                )
            )
            for i, y in enumerate(y4):
                self.team_members.append(
                    Defender(
                        f"{self.name} D{i + 1}",
                        self.accuracy,
                        self.saves,
                        (screen_width - screen_width // 5, y),
                        r,
                        self.color,
                        self.name,
                    )
                )
                self.team_members.append(
                    Midfielder(
                        f"{self.name} M{i + 1}",
                        self.accuracy,
                        self.saves,
                        (screen_width // 2 + screen_width // 8, y),
                        r,
                        self.color,
                        self.name,
                    )
                )
            for i, y in enumerate(y2):
                self.team_members.append(
                    Forwards(
                        f"{self.name} F{i + 1}",
                        self.accuracy,
                        self.saves,
                        (screen_width // 2 + screen_width // 6, y),
                        r,
                        self.color,
                        self.name,
                    )
                )
