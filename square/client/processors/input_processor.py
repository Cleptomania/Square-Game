from typing import List

from square.client.components import InputComponent
from square.common import esper
from square.common.components import PhysicsComponent


class InputProcessor(esper.Processor):
    def process(self, delta_time: float, excludes: List[int] = []):
        for ent, (phys, inp) in self.world.get_components(
            PhysicsComponent, InputComponent
        ):
            phys.velocity[0] = 0
            phys.velocity[1] = 0
            if inp.up and not inp.down:
                phys.velocity[1] = 3
            elif inp.down and not inp.up:
                phys.velocity[1] = -3
            if inp.left and not inp.right:
                phys.velocity[0] = -3
            elif inp.right and not inp.left:
                phys.velocity[0] = 3
