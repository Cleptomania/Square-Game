from typing import List

from square.client.components import DRComponent
from square.common import esper
from square.common.components import PhysicsComponent, SpriteComponent


class DRProcessor(esper.Processor):
    def process(self, delta_time: float, excludes: List[int] = []):
        dt2 = delta_time * delta_time
        for ent, (dr_comp, physics_comp, sprite_comp) in self.world.get_components(
            DRComponent, PhysicsComponent, SpriteComponent
        ):
            if ent in excludes:
                continue

            time_cap = delta_time / 0.0666
            time_cap = max(min(time_cap, 1.0), 0.0)
            vb = (
                (
                    physics_comp.velocity[0]
                    + ((dr_comp.velocity[0] - physics_comp.velocity[0]) * time_cap)
                ),
                (
                    physics_comp.velocity[1]
                    + ((dr_comp.velocity[1] - physics_comp.velocity[1]) * time_cap)
                ),
            )
            pos_t0 = (
                (
                    sprite_comp.sprite.center_x
                    + (vb[0] * delta_time)
                    + (0.5 * dr_comp.acceleration[0] * dt2)
                ),
                (
                    sprite_comp.sprite.center_y
                    + (vb[1] * delta_time)
                    + (0.5 * dr_comp.acceleration[1] * dt2)
                ),
            )
            pos_t1 = (
                (
                    dr_comp.position[0]
                    + (dr_comp.velocity[0] * delta_time)
                    + (0.5 * dr_comp.acceleration[0] * dt2)
                ),
                (
                    dr_comp.position[1]
                    + (dr_comp.velocity[1] * delta_time)
                    + (0.5 * dr_comp.acceleration[1] * dt2)
                ),
            )

            pos_qx = pos_t0[0] + ((pos_t1[0] - pos_t0[0]) * time_cap)
            pos_qy = pos_t0[1] + ((pos_t1[1] - pos_t0[1]) * time_cap)

            if abs(pos_qx - dr_comp.position[0]) >= 20:
                pos_qx = dr_comp.position[0]

            if abs(pos_qy - dr_comp.position[1]) >= 20:
                pos_qy = dr_comp.position[1]

            sprite_comp.sprite.center_x = pos_qx
            sprite_comp.sprite.center_y = pos_qy
