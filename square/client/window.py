from typing import Optional

import arcade
import arcade.gui

from square.client.views.view_main_menu import MainMenuView

_window: Optional["Window"] = None


def get_window() -> "Window":
    if _window is None:
        raise RuntimeError(
            "No window is active. Use set_window() to set an active window"
        )

    return _window


def set_window(window: "Window") -> None:
    global _window
    _window = window


class Window(arcade.Window):
    def __init__(self):
        super().__init__(
            width=800,
            height=600,
            resizable=False,
        )

        # setup views
        self.views = {}
        self.views["main_menu"] = MainMenuView()

        set_window(self)

    def register_application(self, application):
        self.push_handlers(
            **{
                et: getattr(application, et, None)
                for et in self.event_types
                if hasattr(application, et)
            }
        )
