import pygame
from pygame.math import Vector2


class Player:
    def __init__(
        self,
        name: str,
        accuracy: float,
        defence: float,
        position: tuple,
        radius: int,
        color: tuple,
        team_name: str,
    ):
        self.name = name
        self.accuracy = accuracy
        self.defence = defence
        self.position = Vector2(position)
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

    def move_towards(self, target: Vector2, speed: float):
        """Move toward a target (like ball or goal)."""
        direction = target - self.position
        if direction.length() > 0:
            direction = direction.normalize()
        self.position += direction * speed


class Goalkeeper(Player):
    def __init__(
        self,
        name: str,
        accuracy: float,
        defence: float,
        position: tuple,
        radius: int,
        color: tuple,
        team_name: str,
    ):
        super().__init__(
            name, accuracy, defence, position, radius, color, team_name
        )


class Midfielder(Player):
    def __init__(
        self,
        name: str,
        accuracy: float,
        defence: float,
        position: tuple,
        radius: int,
        color: tuple,
        team_name: str,
    ):
        super().__init__(
            name, accuracy, defence, position, radius, color, team_name
        )


class Defender(Player):
    def __init__(
        self,
        name: str,
        accuracy: float,
        defence: float,
        position: tuple,
        radius: int,
        color: tuple,
        team_name: str,
    ):
        super().__init__(
            name, accuracy, defence, position, radius, color, team_name
        )


class Forwards(Player):
    def __init__(
        self,
        name: str,
        accuracy: float,
        defence: float,
        position: tuple,
        radius: int,
        color: tuple,
        team_name: str,
    ):
        super().__init__(
            name, accuracy, defence, position, radius, color, team_name
        )


class Team:
    def __init__(self, name: str, color: tuple, accuracy: float, saves: float):
        self.score = 0
        self.name = name
        self.color = color
        self.accuracy = accuracy
        self.saves = saves
        self.team_members = []

    def create_players(self, screen_width: int, screen_height: int):
        player_radius = 10
        team_name = self.name
        team_color = self.color

        # Define general vertical spacing for players
        # Adjust these multipliers to spread players more or less
        goalkeeper_y = screen_height // 2
        defender_y_positions = [screen_height * (i + 1) // 5 for i in range(4)]
        midfielder_y_positions = [
            screen_height * (i + 1) // 5 for i in range(4)
        ]
        forward_y_positions = [screen_height * (i + 1) // 3 for i in range(2)]

        if team_name == "Real Madrid":  # Real Madrid starts on the left half
            # Goalkeeper
            self.team_members.append(
                Goalkeeper(
                    name=f"{team_name} GK",
                    accuracy=self.accuracy,
                    defence=self.saves,
                    position=(screen_width // 10, goalkeeper_y),
                    radius=player_radius,
                    color=team_color,
                    team_name=team_name,
                )
            )
            # Defenders (4 players)
            for i, y_pos in enumerate(defender_y_positions):
                self.team_members.append(
                    Defender(
                        name=f"{team_name} D{i + 1}",
                        accuracy=self.accuracy,
                        defence=self.saves,
                        position=(screen_width // 5, y_pos),
                        radius=player_radius,
                        color=team_color,
                        team_name=team_name,
                    )
                )
            # Midfielders (4 players)
            for i, y_pos in enumerate(midfielder_y_positions):
                self.team_members.append(
                    Midfielder(
                        name=f"{team_name} M{i + 1}",
                        accuracy=self.accuracy,
                        defence=self.saves,
                        position=(screen_width // 2 - screen_width // 8, y_pos),
                        radius=player_radius,
                        color=team_color,
                        team_name=team_name,
                    )
                )
            # Forwards (2 players)
            for i, y_pos in enumerate(forward_y_positions):
                self.team_members.append(
                    Forwards(
                        name=f"{team_name} F{i + 1}",
                        accuracy=self.accuracy,
                        defence=self.saves,
                        position=(
                            screen_width // 2
                            - screen_width
                            // 6,  # Move forwards closer to center for Real Madrid
                            y_pos,
                        ),
                        radius=player_radius,
                        color=team_color,
                        team_name=team_name,
                    )
                )
        else:  # Kairat starts on the right half, mirrored positions
            # Goalkeeper
            self.team_members.append(
                Goalkeeper(
                    name=f"{team_name} GK",
                    accuracy=self.accuracy,
                    defence=self.saves,
                    position=(screen_width - screen_width // 10, goalkeeper_y),
                    radius=player_radius,
                    color=team_color,
                    team_name=team_name,
                )
            )
            # Defenders (4 players)
            for i, y_pos in enumerate(defender_y_positions):
                self.team_members.append(
                    Defender(
                        name=f"{team_name} D{i + 1}",
                        accuracy=self.accuracy,
                        defence=self.saves,
                        position=(screen_width - screen_width // 5, y_pos),
                        radius=player_radius,
                        color=team_color,
                        team_name=team_name,
                    )
                )
            # Midfielders (4 players)
            for i, y_pos in enumerate(midfielder_y_positions):
                self.team_members.append(
                    Midfielder(
                        name=f"{team_name} M{i + 1}",
                        accuracy=self.accuracy,
                        defence=self.saves,
                        position=(screen_width // 2 + screen_width // 8, y_pos),
                        radius=player_radius,
                        color=team_color,
                        team_name=team_name,
                    )
                )
            # Forwards (2 players)
            for i, y_pos in enumerate(forward_y_positions):
                self.team_members.append(
                    Forwards(
                        name=f"{team_name} F{i + 1}",
                        accuracy=self.accuracy,
                        defence=self.saves,
                        position=(
                            screen_width // 2
                            + screen_width
                            // 6,  # Move forwards closer to center for Kairat
                            y_pos,
                        ),
                        radius=player_radius,
                        color=team_color,
                        team_name=team_name,
                    )
                )


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
