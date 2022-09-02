from typing import Dict

import arcade

from square.common import esper
from square.common.components import PhysicsComponent, SpriteComponent
from square.common.processors import PhysicsProcessor


class Application:
    """
    Main game class

    The server uses this to run the headless version of the game.
    """

    def __init__(self):
        self.world = esper.World()
        self.players: Dict[str, int] = {}
        self.player_spritelist = arcade.SpriteList()
        self.world.add_processor(PhysicsProcessor())

    def add_player(self, new_id: str, x: float, y: float):
        if new_id in self.players:
            raise RuntimeError("Duplicate Player ID")
        sprite = arcade.SpriteSolidColor(40, 40, arcade.csscolor.RED)
        sprite.center_x = x
        sprite.center_y = y
        if self.player_spritelist is not None:
            self.player_spritelist.append(sprite)
        player = self.world.create_entity(SpriteComponent(sprite), PhysicsComponent())
        self.players[new_id] = player
        return player

    def remove_player(self, id: str):
        self.world.delete_entity(self.players[id])
        del self.players[id]

    def on_update(self, delta_time):
        pass
