from typing import List


class PhysicsComponent:
    def __init__(self, x=0.0, y=0.0):
        self.velocity: List[float] = [x, y]
