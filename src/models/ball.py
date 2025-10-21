import numpy as np


class Ball:
    def __init__(self, position: np.ndarray):
        self.position = position
        self.velocity = np.zeros(2)

    def move(self):
        self.position += self.velocity
