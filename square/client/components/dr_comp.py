from dataclasses import dataclass as component
from typing import Tuple


@component
class DRComponent:
    previous_position: Tuple[float, float] = (0, 0)
    position: Tuple[float, float] = (0, 0)
    previous_velocity: Tuple[float, float] = (0, 0)
    velocity: Tuple[float, float] = (0, 0)
    previous_time: float = 0
    time: float = 0
    acceleration: Tuple[float, float] = (0, 0)
