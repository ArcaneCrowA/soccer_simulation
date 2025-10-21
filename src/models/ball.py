import numpy as np


class Ball:
    def __init__(self, position: np.ndarray):
        self.position = position
        self.velocity = np.zeros(2)
        self.drag = 0.95

    def move(self):
        self.position += self.velocity
        self.velocity *= self.drag
