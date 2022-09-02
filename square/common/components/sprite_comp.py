from dataclasses import dataclass as component

from arcade import Sprite


@component
class SpriteComponent:
    sprite: Sprite
