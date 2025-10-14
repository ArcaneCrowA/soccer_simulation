import numpy as np
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

# 1. Player Roles and Skills
PLAYER_ROLES = {
    "Goalkeeper": {"skill_range": (0.5, 0.8)},
    "Defender": {"skill_range": (0.6, 0.85)},
    "Midfielder": {"skill_range": (0.7, 0.95)},
    "Forwards": {"skill_range": (0.75, 0.98)},
}


def assign_player_skill(role):
    """Assigns a skill level to a player based on their role."""
    min_skill, max_skill = PLAYER_ROLES[role]["skill_range"]
    return np.random.uniform(min_skill, max_skill)


# 2. Bayesian Network for Pass Prediction
def create_pass_network():
    """Creates and returns the Bayesian Network for pass success."""
    network = DiscreteBayesianNetwork(
        [
            ("PasserRole", "PassSuccess"),
            ("TargetRole", "PassSuccess"),
            ("DistanceToTarget", "PassSuccess"),
            ("AngleToTarget", "PassSuccess"),
            ("DefenderProximity", "PassSuccess"),
            ("PasserSpeed", "PassSuccess"),
            ("TargetSpeed", "PassSuccess"),
            ("PassType", "PassSuccess"),
            ("Pressure", "PassSuccess"),
            ("PlayerSkill", "PassSuccess"),
            ("PasserRole", "PasserSpeed"),
            ("TargetRole", "TargetSpeed"),
        ]
    )

    # --- CPDs (Conditional Probability Distributions) ---
    # These probabilities are illustrative. They should be learned from data.

    # Player Roles (Categorical)
    cpd_passer_role = TabularCPD(
        "PasserRole",
        4,
        [[0.1], [0.4], [0.3], [0.2]],
        state_names={
            "PasserRole": ["Goalkeeper", "Defender", "Midfielder", "Forwards"]
        },
    )
    cpd_target_role = TabularCPD(
        "TargetRole",
        4,
        [[0.1], [0.4], [0.3], [0.2]],
        state_names={
            "TargetRole": ["Goalkeeper", "Defender", "Midfielder", "Forwards"]
        },
    )

    # Physical Factors (Discretized into bins)
    cpd_distance = TabularCPD(
        "DistanceToTarget",
        3,
        [[0.6], [0.3], [0.1]],
        state_names={"DistanceToTarget": ["Short", "Medium", "Long"]},
    )
    cpd_angle = TabularCPD(
        "AngleToTarget",
        3,
        [[0.7], [0.2], [0.1]],
        state_names={"AngleToTarget": ["Easy", "Moderate", "Hard"]},
    )
    cpd_defender_prox = TabularCPD(
        "DefenderProximity",
        3,
        [[0.2], [0.5], [0.3]],
        state_names={"DefenderProximity": ["Close", "Medium", "Far"]},
    )
    cpd_pressure = TabularCPD(
        "Pressure", 2, [[0.7], [0.3]], state_names={"Pressure": ["Low", "High"]}
    )
    cpd_pass_type = TabularCPD(
        "PassType",
        2,
        [[0.6], [0.4]],
        state_names={"PassType": ["Ground", "Air"]},
    )

    # Player-dependent factors
    cpd_passer_speed = TabularCPD(
        "PasserSpeed",
        3,
        [[0.8, 0.5, 0.3, 0.2], [0.15, 0.3, 0.4, 0.5], [0.05, 0.2, 0.3, 0.3]],
        evidence=["PasserRole"],
        evidence_card=[4],
        state_names={
            "PasserSpeed": ["Low", "Medium", "High"],
            "PasserRole": ["Goalkeeper", "Defender", "Midfielder", "Forwards"],
        },
    )
    cpd_target_speed = TabularCPD(
        "TargetSpeed",
        3,
        [[0.7, 0.4, 0.2, 0.1], [0.2, 0.4, 0.5, 0.6], [0.1, 0.2, 0.3, 0.3]],
        evidence=["TargetRole"],
        evidence_card=[4],
        state_names={
            "TargetSpeed": ["Low", "Medium", "High"],
            "TargetRole": ["Goalkeeper", "Defender", "Midfielder", "Forwards"],
        },
    )
    cpd_player_skill = TabularCPD(
        "PlayerSkill",
        3,
        [[0.2], [0.6], [0.2]],
        state_names={"PlayerSkill": ["Low", "Medium", "High"]},
    )

    # Pass Success (dependent on all others)
    # This CPD is complex due to many parents. A simplified version is shown.
    # In a real scenario, this would be learned from a large dataset.
    num_evidence_states = 4 * 4 * 3 * 3 * 3 * 3 * 3 * 2 * 2 * 3
    values = np.random.rand(2, num_evidence_states)
    values /= values.sum(axis=0)
    cpd_pass_success = TabularCPD(
        "PassSuccess",
        2,
        values,
        evidence=[
            "PasserRole",
            "TargetRole",
            "DistanceToTarget",
            "AngleToTarget",
            "DefenderProximity",
            "PasserSpeed",
            "TargetSpeed",
            "PassType",
            "Pressure",
            "PlayerSkill",
        ],
        evidence_card=[4, 4, 3, 3, 3, 3, 3, 2, 2, 3],
        state_names={
            "PassSuccess": ["Fail", "Success"],
            "PasserRole": ["Goalkeeper", "Defender", "Midfielder", "Forwards"],
            "TargetRole": ["Goalkeeper", "Defender", "Midfielder", "Forwards"],
            "DistanceToTarget": ["Short", "Medium", "Long"],
            "AngleToTarget": ["Easy", "Moderate", "Hard"],
            "DefenderProximity": ["Close", "Medium", "Far"],
            "PasserSpeed": ["Low", "Medium", "High"],
            "TargetSpeed": ["Low", "Medium", "High"],
            "PassType": ["Ground", "Air"],
            "Pressure": ["Low", "High"],
            "PlayerSkill": ["Low", "Medium", "High"],
        },
    )

    network.add_cpds(
        cpd_passer_role,
        cpd_target_role,
        cpd_distance,
        cpd_angle,
        cpd_defender_prox,
        cpd_pressure,
        cpd_pass_type,
        cpd_passer_speed,
        cpd_target_speed,
        cpd_player_skill,
        cpd_pass_success,
    )
    network.check_model()
    return network


# 3. Prediction and Confidence
def predict_pass_success(network, evidence):
    """
    Predicts pass success and provides a confidence score.

    Args:
        network: The trained Bayesian Network.
        evidence: A dictionary of observed variables, e.g.,
                  {"PasserRole": "Midfielder", "DistanceToTarget": "Short"}

    Returns:
        A tuple of (prediction, confidence_score).
    """
    inference = VariableElimination(network)
    result = inference.query(variables=["PassSuccess"], evidence=evidence)

    success_prob = result.values[1]  # Probability of "Success"

    # Confidence score calculation (example)
    # Factors: player skill, data availability (assumed), network calibration
    player_skill_level = evidence.get("PlayerSkill", "Medium")
    skill_confidence = {"Low": 0.7, "Medium": 0.85, "High": 0.95}.get(
        player_skill_level, 0.8
    )

    # A more complex model could factor in the number of data points for the given evidence
    confidence = success_prob * skill_confidence

    prediction = "Success" if success_prob > 0.5 else "Fail"

    return prediction, confidence, success_prob


if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Create players and assign skills
    players = {
        "Player1": {
            "role": "Midfielder",
            "skill": assign_player_skill("Midfielder"),
        },
        "Player2": {
            "role": "Forwards",
            "skill": assign_player_skill("Forwards"),
        },
    }
    print(f"Players: {players}\n")

    # 2. Create the network
    pass_network = create_pass_network()

    # 3. Simulate a pass and predict
    pass_evidence = {
        "PasserRole": "Midfielder",
        "TargetRole": "Forwards",
        "DistanceToTarget": "Medium",
        "AngleToTarget": "Easy",
        "DefenderProximity": "Far",
        "PasserSpeed": "Medium",
        "TargetSpeed": "High",
        "PassType": "Ground",
        "Pressure": "Low",
        "PlayerSkill": "High",  # Assuming the passer is highly skilled
    }

    prediction, confidence, probability = predict_pass_success(
        pass_network, pass_evidence
    )

    print(f"Pass Scenario: {pass_evidence}")
    print(f"-> Prediction: {prediction}")
    print(f"-> Probability of Success: {probability:.2f}")
    print(f"-> Confidence Score: {confidence:.2f}")
