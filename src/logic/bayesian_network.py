from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork

from src.models import PlayerRole
from src.models.pass_type import PassType


class PassSuccessPredictor:
    def __init__(self):
        self.model = BayesianNetwork(
            [
                ("PlayerSkill", "PassSuccess"),
                ("DistanceToTarget", "PassSuccess"),
                ("PasserRole", "PassSuccess"),
                ("TargetRole", "PassSuccess"),
                ("AngleToTarget", "PassSuccess"),
                ("PasserSpeed", "PassSuccess"),
                ("DefenderProximity", "PassSuccess"),
                ("TargetSpeed", "PassSuccess"),
                ("PassType", "PassSuccess"),
                ("Pressure", "PassSuccess"),
            ]
        )

        # Define Conditional Probability Distributions (CPDs)
        cpd_skill = TabularCPD(
            variable="PlayerSkill",
            variable_card=2,
            values=[[0.5], [0.5]],
            state_names={"PlayerSkill": ["Low", "High"]},
        )

        cpd_distance = TabularCPD(
            variable="DistanceToTarget",
            variable_card=2,
            values=[[0.5], [0.5]],
            state_names={"DistanceToTarget": ["Short", "Long"]},
        )

        cpd_passer_role = TabularCPD(
            variable="PasserRole",
            variable_card=4,
            values=[[0.25], [0.25], [0.25], [0.25]],
            state_names={
                "PasserRole": [
                    "goalkeeper",
                    "defender",
                    "midfielder",
                    "attacker",
                ]
            },
        )

        cpd_target_role = TabularCPD(
            variable="TargetRole",
            variable_card=4,
            values=[[0.25], [0.25], [0.25], [0.25]],
            state_names={
                "TargetRole": [
                    "goalkeeper",
                    "defender",
                    "midfielder",
                    "attacker",
                ]
            },
        )

        cpd_angle = TabularCPD(
            variable="AngleToTarget",
            variable_card=2,
            values=[[0.5], [0.5]],
            state_names={"AngleToTarget": ["Narrow", "Wide"]},
        )

        cpd_passer_speed = TabularCPD(
            variable="PasserSpeed",
            variable_card=2,
            values=[[0.5], [0.5]],
            state_names={"PasserSpeed": ["Slow", "Fast"]},
        )

        cpd_defender_proximity = TabularCPD(
            variable="DefenderProximity",
            variable_card=2,
            values=[[0.5], [0.5]],
            state_names={"DefenderProximity": ["Close", "Far"]},
        )

        cpd_target_speed = TabularCPD(
            variable="TargetSpeed",
            variable_card=2,
            values=[[0.5], [0.5]],
            state_names={"TargetSpeed": ["Slow", "Fast"]},
        )

        cpd_pass_type = TabularCPD(
            variable="PassType",
            variable_card=3,
            values=[[0.33], [0.33], [0.34]],
            state_names={"PassType": ["short", "long", "through_ball"]},
        )

        cpd_pressure = TabularCPD(
            variable="Pressure",
            variable_card=2,
            values=[[0.5], [0.5]],
            state_names={"Pressure": ["Low", "High"]},
        )

        cpd_pass_success = TabularCPD(
            variable="PassSuccess",
            variable_card=2,
            values=[
                # Probabilities of PassSuccess=False
                # These values are just placeholders and should be learned from data
                [0.1] * 1536,  # High Skill, Short Dist, etc.
                [0.9] * 1536,  # Low Skill, Long Dist, etc.
            ],
            evidence=[
                "PlayerSkill",
                "DistanceToTarget",
                "PasserRole",
                "TargetRole",
                "AngleToTarget",
                "PasserSpeed",
                "DefenderProximity",
                "TargetSpeed",
                "PassType",
                "Pressure",
            ],
            evidence_card=[2, 2, 4, 4, 2, 2, 2, 2, 3, 2],
            state_names={
                "PassSuccess": ["False", "True"],
                "PlayerSkill": ["Low", "High"],
                "DistanceToTarget": ["Short", "Long"],
                "PasserRole": [
                    "goalkeeper",
                    "defender",
                    "midfielder",
                    "attacker",
                ],
                "TargetRole": [
                    "goalkeeper",
                    "defender",
                    "midfielder",
                    "attacker",
                ],
                "AngleToTarget": ["Narrow", "Wide"],
                "PasserSpeed": ["Slow", "Fast"],
                "DefenderProximity": ["Close", "Far"],
                "TargetSpeed": ["Slow", "Fast"],
                "PassType": ["short", "long", "through_ball"],
                "Pressure": ["Low", "High"],
            },
        )

        self.model.add_cpds(
            cpd_skill,
            cpd_distance,
            cpd_passer_role,
            cpd_target_role,
            cpd_angle,
            cpd_passer_speed,
            cpd_defender_proximity,
            cpd_target_speed,
            cpd_pass_type,
            cpd_pressure,
            cpd_pass_success,
        )
        self.model.check_model()

        self.inference = VariableElimination(self.model)

    def get_confidence(self, total_passes: int) -> str:
        if total_passes < 10:
            return "Low"
        elif total_passes < 50:
            return "Medium"
        else:
            return "High"

    def predict(
        self,
        skill: float,
        distance: float,
        passer_role: PlayerRole,
        target_role: PlayerRole,
        angle: float,
        passer_speed: float,
        defender_proximity: float,
        target_speed: float,
        pass_type: PassType,
        pressure: float,
        total_passes: int,
    ) -> tuple[float, str]:
        skill_state = "High" if skill > 0.5 else "Low"
        distance_state = (
            "Long" if distance > 30 else "Short"
        )  # 30 is a threshold
        angle_state = "Wide" if angle > 0.5 else "Narrow"  # 0.5 is a threshold
        passer_speed_state = (
            "Fast" if passer_speed > 0.5 else "Slow"
        )  # 0.5 is a threshold
        defender_proximity_state = (
            "Close" if defender_proximity < 10 else "Far"
        )  # 10 is a threshold
        target_speed_state = (
            "Fast" if target_speed > 0.5 else "Slow"
        )  # 0.5 is a threshold
        pressure_state = (
            "High" if pressure > 0.5 else "Low"
        )  # 0.5 is a threshold

        result = self.inference.query(
            variables=["PassSuccess"],
            evidence={
                "PlayerSkill": skill_state,
                "DistanceToTarget": distance_state,
                "PasserRole": passer_role.value,
                "TargetRole": target_role.value,
                "AngleToTarget": angle_state,
                "PasserSpeed": passer_speed_state,
                "DefenderProximity": defender_proximity_state,
                "TargetSpeed": target_speed_state,
                "PassType": pass_type.value,
                "Pressure": pressure_state,
            },
        )

        confidence = self.get_confidence(total_passes)
        return (
            result.values[1],
            confidence,
        )  # Return the probability of PassSuccess=True and confidence
