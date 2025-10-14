import math
import random
from collections import deque

import pygame
import torch
import torch.nn as nn
import torch.optim as optim
from pygame.math import Vector2


# DQN Model
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


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
        self.last_action = None

    def load_model(self, path, for_training=False):
        self.dqn.load_state_dict(torch.load(path))
        if not for_training:
            self.epsilon = 0.05  # Set epsilon low for inference/simulation
        print(f"Model loaded for {self.name}")

    def save_model(self, path):
        torch.save(self.dqn.state_dict(), path)

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory."""
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        """Train the DQN using experience replay."""
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.stack(states)
        next_states = torch.stack(next_states)
        actions = torch.tensor(actions)
        rewards = torch.tensor(rewards)
        dones = torch.tensor(dones, dtype=torch.float32)

        # Compute Q values
        q_values = self.dqn(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        next_q_values = self.dqn(next_states).max(1)[0]
        targets = rewards + self.gamma * next_q_values * (1 - dones)

        # Update network
        loss = nn.MSELoss()(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def choose_action(self, state):
        action = self.choose_action(state)
        self.last_action = action
        return action

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
        direction = target_position - ball.position

        # Prevent zero-length vector
        if direction.length() == 0:
            return  # Skip kick if ball is exactly under player

        direction = direction.normalize()

        angle_dev = (1 - self.accuracy) * 90
        deviation = random.uniform(-angle_dev, angle_dev)
        actual_direction = direction.rotate(math.degrees(deviation))
        ball.velocity = actual_direction * kick_power

    def separate_from_others(
        self, teammates, min_distance=20, push_strength=0.5
    ):
        """Push players apart if they are too close to each other."""
        for mate in teammates:
            if mate is self:
                continue
            diff = self.position - mate.position
            dist = diff.length()
            if dist < min_distance and dist > 0:
                # Compute how much to push
                overlap = (min_distance - dist) / 2
                direction = diff.normalize()
                self.position += direction * overlap * push_strength
                mate.position -= direction * overlap * push_strength

    def stay_in_zone(self, field_width, field_height):
        """Keep player within their tactical zone depending on role."""
        role = self.__class__.__name__
        margin = self.radius
        third = field_width / 3

        if self.team_name == "Real Madrid":
            if role == "Goalkeeper":
                min_x, max_x = margin, third * 0.5
            elif role == "Defender":
                min_x, max_x = margin, third
            elif role == "Midfielder":
                min_x, max_x = third * 0.5, third * 2
            elif role == "Forwards":
                min_x, max_x = third * 1.5, field_width - third * 0.2
        else:  # Kairat (right side)
            if role == "Goalkeeper":
                min_x, max_x = field_width - third * 0.5, field_width - margin
            elif role == "Defender":
                min_x, max_x = field_width - third, field_width - margin
            elif role == "Midfielder":
                min_x, max_x = third, field_width - third * 0.5
            elif role == "Forwards":
                min_x, max_x = third * 0.2, field_width - third * 1.5

        # Clamp Y to field bounds
        min_y, max_y = margin, field_height - margin

        if role != "Goalkeeper":
            # Apply clamping
            self.position.x = max(
                margin, min(self.position.x, field_width - margin)
            )
            self.position.y = max(min_y, min(self.position.y, max_y))
        else:
            self.position.x = max(min_x, min(self.position.x, max_x))
            self.position.y = max(min_y, min(self.position.y, max_y))


class Goalkeeper(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_position = self.position.copy()
        self.state_size = 8  # e.g., ball_x,y,vel_x,y, own_x,y, goal_dist_x,y
        self.action_size = 3  # move, dive, stay
        self.dqn = DQN(self.state_size, self.action_size)
        self.optimizer = optim.Adam(self.dqn.parameters(), lr=0.001)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32

    def get_state(self, ball, field_width, field_height, teammates):
        state = [
            self.position.x / field_width,
            self.position.y / field_height,
            ball.position.x / field_width,
            ball.position.y / field_height,
            ball.velocity.x / 25,
            ball.velocity.y / 25,
            (
                field_height
                if self.team_name == "Kairat"
                else 0 - self.position.x
            )
            / field_height,
            (field_height / 2 - self.position.y) / field_height,
        ]
        return torch.tensor(state, dtype=torch.float32)

    def choose_action(self, state):
        if random.random() <= self.epsilon:
            return random.randint(0, self.action_size - 1)
        with torch.no_grad():
            return self.dqn(state.unsqueeze(0)).argmax().item()

    def update(self, action, ball, field_width, field_height, teammates):
        penalty_area_width = 150
        min_x = (
            self.radius
            if self.team_name == "Real Madrid"
            else field_width - penalty_area_width // 2
        )
        max_x = (
            penalty_area_width // 2
            if self.team_name == "Real Madrid"
            else field_width - self.radius
        )
        target_y = max(
            (field_height - 150) // 2,
            min((field_height + 150) // 2, ball.position.y),
        )

        if action == 0:  # Move to intercept
            target_x = max(min_x, min(max_x, ball.position.x))
            self.move_towards(Vector2(target_x, target_y), speed=3)
        elif action == 1 and self.can_reach_ball(ball):  # Dive/Block
            ball.velocity *= 0.1  # Stop the ball
        elif action == 2 and self.can_reach_ball(ball):  # Kick
            # Find a teammate in the midfield to pass to
            best_mate = None
            for mate in teammates:
                if isinstance(mate, Midfielder):
                    best_mate = mate
                    break  # Found one, that's good enough

            if best_mate:
                self.kick_ball(ball, best_mate.position, kick_power=20)
            else:  # Fallback: kick forward to center
                kick_target = Vector2(field_width / 2, self.position.y)
                self.kick_ball(ball, kick_target, kick_power=20)


class Defender(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_position = self.position.copy()
        self.state_size = 10  # ball_x,y,vel_x,y, own_x,y, opponent_dist, goal_dist_x,y, zone_dist
        self.action_size = 4  # tackle, intercept, move_to_ball, return_to_pos
        self.dqn = DQN(self.state_size, self.action_size)
        self.optimizer = optim.Adam(self.dqn.parameters(), lr=0.001)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32

    def get_state(self, ball, field_width, field_height, opponents):
        def_x = (
            field_width // 4
            if self.team_name == "Real Madrid"
            else field_width - field_width // 4
        )
        state = [
            self.position.x / field_width,
            self.position.y / field_height,
            ball.position.x / field_width,
            ball.position.y / field_height,
            ball.velocity.x / 25,
            ball.velocity.y / 25,
            min([self.distance_to(p.position) for p in opponents])
            / field_width,
            abs(
                (field_width if self.team_name == "Kairat" else 0)
                - self.position.x
            )
            / field_width,
            abs(self.position.y - ball.position.y) / field_height,
            abs(self.position.x - def_x) / field_width,
        ]
        return torch.tensor(state, dtype=torch.float32)

    def choose_action(self, state):
        if random.random() <= self.epsilon:
            return random.randint(0, self.action_size - 1)
        with torch.no_grad():
            return self.dqn(state.unsqueeze(0)).argmax().item()

    def update(self, action, ball, field_width, field_height, opponents):
        def_x = (
            field_width // 4
            if self.team_name == "Real Madrid"
            else field_width - field_width // 4
        )
        in_half = (
            self.team_name == "Real Madrid"
            and ball.position.x < field_width / 2
        ) or (self.team_name == "Kairat" and ball.position.x > field_width / 2)

        if action == 0 and self.can_reach_ball(ball):  # Tackle
            target_x = field_width * (
                0.6 if self.team_name == "Real Madrid" else 0.4
            )
            self.kick_ball(
                ball, Vector2(target_x, random.uniform(0, field_height)), 10
            )
        elif (
            action == 1 and in_half and self.distance_to(ball.position) < 200
        ):  # Intercept
            self.move_towards(ball.position, 2.5)
        elif action == 2:  # Move to ball
            self.move_towards(ball.position, 2.5)
        else:  # Return to position
            self.move_towards(Vector2(def_x, ball.position.y), 1.8)


class Midfielder(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_position = self.position.copy()
        self.state_size = (
            9  # pos_x,y, ball_x,y,vel_x,y, teammate_dist, goal_dist, can_kick
        )
        self.action_size = 10  # 8 directions, kick, stay
        self.dqn = DQN(self.state_size, self.action_size)
        self.optimizer = optim.Adam(self.dqn.parameters(), lr=0.001)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32

    def get_state(self, ball, teammates, field_width, field_height):
        # Flatten state vector (example)
        state = [
            self.position.x / field_width,
            self.position.y / field_height,
            ball.position.x / field_width,
            ball.position.y / field_height,
            ball.velocity.x / 25,
            ball.velocity.y / 25,  # normalized
            # Add teammate dists, opponent dists (simplify to closest)
            min([self.distance_to(p.position) for p in teammates if p != self])
            / field_width,
            # Goal dist
            abs(
                field_width
                if self.team_name == "Real Madrid"
                else 0 - self.position.x
            )
            / field_width,
            1.0 if self.can_reach_ball(ball) else 0.0,
        ]
        return torch.tensor(state, dtype=torch.float32)

    def choose_action(self, state):
        if random.random() <= self.epsilon:
            return random.randint(0, self.action_size - 1)
        with torch.no_grad():
            return self.dqn(state.unsqueeze(0)).argmax().item()

    def update(self, action, ball, teammates, field_width, field_height, speed):
        # --- Movement Actions ---
        if action == 0:  # Move North
            self.position.y -= speed
        elif action == 1:  # Move North-East
            self.position.y -= speed / 1.414
            self.position.x += speed / 1.414
        elif action == 2:  # Move East
            self.position.x += speed
        elif action == 3:  # Move South-East
            self.position.y += speed / 1.414
            self.position.x += speed / 1.414
        elif action == 4:  # Move South
            self.position.y += speed
        elif action == 5:  # Move South-West
            self.position.y += speed / 1.414
            self.position.x -= speed / 1.414
        elif action == 6:  # Move West
            self.position.x -= speed
        elif action == 7:  # Move North-West
            self.position.y -= speed / 1.414
            self.position.x -= speed / 1.414

        # --- Other Actions ---
        elif action == 8:  # Kick
            if self.can_reach_ball(ball):
                # Simple rule: shoot at goal
                goal_x = field_width if self.team_name == "Real Madrid" else 0
                goal_center = Vector2(goal_x, field_height / 2)
                self.kick_ball(ball, goal_center, kick_power=20)

        # action == 9 is "Stay Still", so we do nothing.


class Forwards(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_position = self.position.copy()
        self.state_size = (
            9  # pos_x,y, ball_x,y,vel_x,y, teammate_dist, goal_dist, can_kick
        )
        self.action_size = 10  # 8 directions, kick, stay
        self.dqn = DQN(self.state_size, self.action_size)
        self.optimizer = optim.Adam(self.dqn.parameters(), lr=0.001)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32

    def get_state(self, ball, teammates, field_width, field_height):
        # Flatten state vector (example)
        state = [
            self.position.x / field_width,
            self.position.y / field_height,
            ball.position.x / field_width,
            ball.position.y / field_height,
            ball.velocity.x / 25,
            ball.velocity.y / 25,  # normalized
            # Add teammate dists, opponent dists (simplify to closest)
            min([self.distance_to(p.position) for p in teammates if p != self])
            / field_width,
            abs(
                field_width
                if self.team_name == "Real Madrid"
                else 0 - self.position.x
            )
            / field_width,
            1.0 if self.can_reach_ball(ball) else 0.0,
        ]
        return torch.tensor(state, dtype=torch.float32)

    def choose_action(self, state):
        if random.random() <= self.epsilon:
            return random.randint(0, self.action_size - 1)
        with torch.no_grad():
            return self.dqn(state.unsqueeze(0)).argmax().item()

    def update(self, action, ball, teammates, field_width, field_height, speed):
        # --- Movement Actions ---
        if action == 0:  # Move North
            self.position.y -= speed
        elif action == 1:  # Move North-East
            self.position.y -= speed / 1.414
            self.position.x += speed / 1.414
        elif action == 2:  # Move East
            self.position.x += speed
        elif action == 3:  # Move South-East
            self.position.y += speed / 1.414
            self.position.x += speed / 1.414
        elif action == 4:  # Move South
            self.position.y += speed
        elif action == 5:  # Move South-West
            self.position.y += speed / 1.414
            self.position.x -= speed / 1.414
        elif action == 6:  # Move West
            self.position.x -= speed
        elif action == 7:  # Move North-West
            self.position.y -= speed / 1.414
            self.position.x -= speed / 1.414

        # --- Other Actions ---
        elif action == 8:  # Kick
            if self.can_reach_ball(ball):
                # Simple rule: shoot at goal
                goal_x = field_width if self.team_name == "Real Madrid" else 0
                goal_center = Vector2(goal_x, field_height / 2)
                self.kick_ball(ball, goal_center, kick_power=20)

        # action == 9 is "Stay Still", so we do nothing.
