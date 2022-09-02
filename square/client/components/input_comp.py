from dataclasses import dataclass as component


@component
class InputComponent:
    left: int = 0
    right: int = 0
    up: int = 0
    down: int = 0
