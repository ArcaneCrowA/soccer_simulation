import csv
import os

from . import constants
from .models.players import Defender, Goalkeeper, Midfielder


def get_last_episode(filename="scores.csv"):
    """Return the last recorded episode number from file (or 0 if none)."""
    if not os.path.exists(filename):
        return 0
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            if len(lines) <= 1:  # only header
                return 0
            last_line = lines[-1].strip().split(",")
            return int(last_line[0])
    except Exception:
        return 0


def append_score(episode, real_madrid, kairat, filename="scores.csv"):
    """Append one episode's score to file."""
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writerow(["Episode", "Real Madrid", "Kairat"])
        writer.writerow([episode, real_madrid.score, kairat.score])


def get_player_state(player, ball, team, opponent_team):
    """Gets the state for a player based on their type."""
    if isinstance(player, Goalkeeper):
        return player.get_state(
            ball,
            constants.FIELD_WIDTH,
            constants.FIELD_HEIGHT,
            team.team_members,
        )
    elif isinstance(player, Defender):
        return player.get_state(
            ball,
            constants.FIELD_WIDTH,
            constants.FIELD_HEIGHT,
            opponent_team.team_members,
        )
    else:  # Midfielder and Forwards
        return player.get_state(
            ball,
            team.team_members,
            constants.FIELD_WIDTH,
            constants.FIELD_HEIGHT,
        )


def calculate_reward(
    player, ball, team_members, goal_scored_team_name, team_name
):
    """Calculates the reward for a player's last action."""
    reward = 0
    # Penalty for being out of bounds
    if not (
        5 < player.position.x < constants.FIELD_WIDTH - 5
        and 5 < player.position.y < constants.FIELD_HEIGHT - 5
    ):
        reward -= 0.09

    # Reward for distance from other midfielders
    if isinstance(player, Midfielder):
        min_dist = float("inf")
        for mate in team_members:
            if mate is not player and isinstance(mate, Midfielder):
                min_dist = min(min_dist, player.distance_to(mate.position))
        if min_dist < 75:
            reward -= 0.2
        else:
            reward += 0.05

    # Main game objective rewards
    if goal_scored_team_name:
        reward += 5 if goal_scored_team_name == team_name.lower() else -5
    elif player.can_reach_ball(ball):
        reward += 0.3
    elif player.distance_to(ball.position) < 150:
        reward += 0.2
    else:
        reward -= 0.02

    return reward
