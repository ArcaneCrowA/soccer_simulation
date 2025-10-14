1. What is a Bayesian Network?

Think of a Bayesian network as a smart web of cause and effect for uncertain events. It's a graph where:
*   **Nodes** are variables that can be in different states (e.g., the variable `DistanceToTarget` can be in the state `Short`, `Medium`, or `Long`).
*   **Arrows (Edges)** between nodes show probabilistic relationships. An arrow from `A` to `B` means that `A` has a direct influence on the probability of `B`.

Our goal is to use this network to calculate the probability of a pass being successful, given a set of circumstances.

### 2. The "Pass Success" Network Structure

In our simulation, I've created a Bayesian network where `PassSuccess` is the central variable we want to predict. Many factors influence the success of a pass, and I've modeled these as nodes with arrows pointing to `PassSuccess`:

*   **Player Roles:** `PasserRole` and `TargetRole` (e.g., Midfielder, Defender). A pass from a Midfielder to a Forward is different from a pass between two Defenders.
*   **Physical Factors:** `DistanceToTarget`, `AngleToTarget`, `PasserSpeed`, `TargetSpeed`.
*   **Game Situation:** `DefenderProximity` (how close is an opponent?), `Pressure` (is the passer under pressure?).
*   **Player Skill:** A `PlayerSkill` node represents the passer's intrinsic ability.

I also modeled that a player's role can influence their speed, so there are arrows from `PasserRole` to `PasserSpeed` and `TargetRole` to `TargetSpeed`.

### 3. How Predictions are Made

The process of predicting a pass is as follows:

1.  **Gathering Evidence:** When a player is about to kick the ball, we collect information about the current state of the game. This becomes our "evidence." For example:
    *   `PasserRole` is "Midfielder".
    *   `TargetRole` is "Forwards".
    *   `DistanceToTarget` is "Long".
    *   `DefenderProximity` is "Close".
    *   `PlayerSkill` is "High".

2.  **Inference:** We feed this evidence into the Bayesian network. The network then uses an algorithm called **Variable Elimination** to perform inference. This process propagates the evidence through the network, updating the probabilities of all other nodes based on the given information.

3.  **Calculating the Result:** The result of the inference is the updated probability distribution for the `PassSuccess` node. For instance, the network might calculate:
    *   P(PassSuccess = "Success" | evidence) = 0.75
    *   P(PassSuccess = "Fail" | evidence) = 0.25

    Based on these probabilities, we can make a prediction. Since the probability of success (75%) is higher than failure (25%), the prediction would be "Success".

### 4. Confidence Score

The confidence score is an additional layer on top of the raw probability. It's a measure of how much we should trust the prediction. In our case, it's calculated based on:

*   **The prediction probability:** A very high or very low probability (e.g., 95% or 5%) leads to higher confidence than a probability close to 50%.
*   **The player's skill:** We have more confidence in the predictions for highly skilled players.

This entire logic is encapsulated in the `create_pass_network` and `predict_pass_success` functions in the `src/statistics.py` file. The probabilities I've set are illustrative; for a real-world application, they would be learned from analyzing thousands of real game passes.
