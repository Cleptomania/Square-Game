from typing import List

from square.common import esper
from square.common.components import PhysicsComponent, SpriteComponent


class PhysicsProcessor(esper.Processor):
    def process(self, delta_time: float, excludes: List[int] = []):
        for ent, (phys, sprite) in self.world.get_components(
            PhysicsComponent, SpriteComponent
        ):
            sprite.sprite.center_x += phys.velocity[0]
            sprite.sprite.center_y += phys.velocity[1]
