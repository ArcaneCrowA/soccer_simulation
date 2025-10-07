# soccer_simulation

## Installation
```
uv sync
```

## How to run

```
uv run src/main.py --load
```

## How to train
```
uv run src/main.py --train [n]
```
n is number of tries

## Pseudo-code for players
```
CLASS DQN
    INIT(state_size, action_size)
        layer1 = Linear(state_size → 64)
        layer2 = Linear(64 → 64)
        layer3 = Linear(64 → action_size)

    FUNCTION forward(x)
        x = ReLU(layer1(x))
        x = ReLU(layer2(x))
        RETURN layer3(x)
END CLASS


CLASS Player
    INIT(name, accuracy, defence, position, radius, color, team)
        store basic attributes
        set velocity = (0, 0)
        set last_action = None

    FUNCTION load_model(path)
        load weights from file
        if not training → set epsilon = small value

    FUNCTION remember(state, action, reward, next_state, done)
        add (state, action, reward, next_state, done) to memory

    FUNCTION replay()
        IF memory < batch_size → RETURN
        sample random experiences
        compute predicted Q-values
        compute target Q-values using Bellman equation
        update model weights via gradient descent
        reduce epsilon

    FUNCTION choose_action(state)
        if random() < epsilon → pick random action
        else → pick action with max Q-value
        store as last_action
        RETURN action

    FUNCTION move_towards(target, speed)
        direction = normalize(target - position)
        position += direction * speed

    FUNCTION distance_to(pos)
        RETURN Euclidean distance between position and pos

    FUNCTION can_reach_ball(ball, range)
        RETURN distance_to(ball) ≤ radius + ball.radius + range

    FUNCTION kick_ball(ball, target, power)
        direction = normalize(target - ball.position)
        add random deviation based on accuracy
        ball.velocity = direction * power

    FUNCTION separate_from_others(teammates)
        FOR each mate in teammates
            IF too close → push both apart slightly

    FUNCTION stay_in_zone(screen_width, screen_height)
        restrict player position to role-specific field region
END CLASS


### Specialized Roles

CLASS Goalkeeper EXTENDS Player
    INIT(...)
        setup DQN(state=8, actions=3)
        setup memory, gamma, epsilon, optimizer

    FUNCTION get_state(ball, screen_width, screen_height, teammates)
        RETURN normalized vector of:
            self position, ball position & velocity, goal-relative distances

    FUNCTION choose_action(state)
        IF random() < epsilon → random action
        ELSE → argmax(Q(state))

    FUNCTION update(action, ball, screen_width, screen_height, teammates)
        CASE action:
            0: move to intercept ball
            1: block/dive if near ball
            2: pass or kick ball to teammate or center
END CLASS


CLASS Defender EXTENDS Player
    INIT(...)
        setup DQN(state=10, actions=4)

    FUNCTION get_state(ball, screen_width, screen_height, opponents)
        RETURN normalized vector of positions, velocities, distances

    FUNCTION update(action, ball, ...)
        CASE action:
            0: tackle → kick ball away
            1: intercept → move toward ball
            2: chase → move to ball
            3: return to defensive position
END CLASS


CLASS Midfielder EXTENDS Player
    INIT(...)
        setup DQN(state=9, actions=10)

    FUNCTION get_state(ball, teammates, screen_width, screen_height)
        RETURN normalized vector of positions, ball, teammate dist, goal dist

    FUNCTION update(action, ball, teammates, screen_width, screen_height, speed)
        CASE 0–7: move in 8 directions
        CASE 8: if can kick → shoot at goal
        CASE 9: stay still
END CLASS


CLASS Forwards EXTENDS Player
    INIT(...)
        setup DQN(state=9, actions=10)

    FUNCTION get_state(ball, teammates, screen_width, screen_height)
        same as Midfielder

    FUNCTION update(action, ball, teammates, screen_width, screen_height, speed)
        CASE 0–7: move directions
        CASE 8: kick toward goal
        CASE 9: stay still
END CLASS
```
## Pseudocode for main

```
FUNCTION run_simulation(load_models):
    init pygame screen and clock
    create teams, players, ball
    if load_models: load each player’s saved model

    WHILE running:
        handle quit events
        handle round timing and countdowns

        FOR each player:
            get state
            compute reward from last action
            store transition and replay
            choose action and update

        update positions, move ball, detect goals

        if goal scored:
            reset positions and show "GOAL" message

        draw field, players, ball, scores, and timer
        update display and control FPS

    quit pygame

    FUNCTION get_player_state(player, ball, team, opponent):
        return player-specific observation (position, ball, teammates/opponents)

    FUNCTION calculate_reward(player, ball, teammates, goal_team, team_name):
        reward = base value
        penalize out-of-bounds or crowding
        reward being near or reaching ball
        reward goal scored (positive if team scored, negative otherwise)
        return reward
  ```
