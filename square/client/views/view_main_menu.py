"""
Main Menu
"""
from typing import Tuple

import arcade
import arcade.gui

import square.client
from square.client.views import GameView, PauseView, SettingsView, View


class MultiplayerConnectDialog(
    arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorWidget
):
    """
    :param width: Width of the dialog box
    :param height: Height of the dialog box
    :param message_text:
    :param callback: Callback function, will receive the text of the clicked button
    """

    def __init__(self, *, width: float, height: float, callback=None):
        space = 10

        self._text_area = arcade.gui.UITextArea(
            text="Server connection string",
            width=width - space,
            height=height - space,
            text_color=arcade.color.BLACK,
        )
        self.input_field = arcade.gui.UIInputText(
            width=int(width * 0.8), height=30, text="127.0.0.1:9000"
        )
        input_field_box = arcade.gui.UIBorder(self.input_field)

        connect_button = arcade.gui.UIFlatButton(text="Connect")
        connect_button.on_click = self.on_connect  # type: ignore

        self._bg_tex = arcade.load_texture(
            ":resources:gui_basic_assets/window/grey_panel.png"
        )

        self._callback = callback  # type: ignore
        group = arcade.gui.UILayout(
            width=width,
            height=height,
            children=[
                arcade.gui.UIAnchorWidget(
                    child=self._text_area,
                    anchor_x="left",
                    anchor_y="top",
                    align_x=10,
                    align_y=-10,
                ),
                arcade.gui.UIAnchorWidget(
                    child=input_field_box,
                    anchor_x="center",
                    anchor_y="center",
                ),
                arcade.gui.UIAnchorWidget(
                    child=connect_button,
                    anchor_x="right",
                    anchor_y="bottom",
                    align_x=-20,
                    align_y=10,
                ),
            ],
        ).with_background(self._bg_tex)

        super().__init__(child=group)

    def on_connect(self, event):
        self.parent.remove(self)
        if self._callback is not None:
            address, _, port = self.input_field.text.partition(":")
            self._callback((address, int(port)))


class MainMenuView(View):
    def __init__(self):
        super().__init__()

        # A Vertical BoxGroup to align Buttons
        self.v_box = None

    def setup(self):
        super().setup()
        self.ui_manager = arcade.gui.UIManager()

        self.setup_buttons()

        self.ui_manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
            )
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.NAVY_BLUE)

    def setup_buttons(self):
        self.v_box = arcade.gui.UIBoxLayout()

        singleplayer_button = arcade.gui.UIFlatButton(text="Singleplayer", width=200)

        @singleplayer_button.event("on_click")
        def on_click_singleplayer(event):
            pass

        self.v_box.add(singleplayer_button.with_space_around(bottom=20))

        self.multiplayer_button = arcade.gui.UIFlatButton(text="Multiplayer", width=200)

        @self.multiplayer_button.event("on_click")
        def on_click_multiplayer(event):
            dialog = MultiplayerConnectDialog(
                width=450, height=200, callback=self.switch_to_multiplayer
            )
            self.ui_manager.add(dialog)

        self.v_box.add(self.multiplayer_button.with_space_around(bottom=20))

        self.settings_button = arcade.gui.UIFlatButton(text="Settings", width=200)

        @self.settings_button.event("on_click")
        def on_click_settings(event):
            if "settings" not in self.window.views:
                self.window.views["settings"] = SettingsView()
            self.window.show_view(self.window.views["settings"])

        self.v_box.add(self.settings_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)

        @quit_button.event("on_click")
        def on_click_quit(event):
            arcade.exit()

        self.v_box.add(quit_button)

    def switch_to_multiplayer(self, address: Tuple[str, int] = None):
        square.client.set_application(square.client.ClientApplication(address))
        if "game" not in self.window.views:
            self.window.views["game"] = GameView()
            self.window.views["pause"] = PauseView()
        self.window.show_view(self.window.views["game"])

    def on_draw(self):
        arcade.start_render()

        arcade.draw_text(
            "Square Game",
            self.window.width / 2,
            self.window.height - 125,
            arcade.color.ALLOY_ORANGE,
            font_size=44,
            anchor_x="center",
            anchor_y="center",
        )

        self.ui_manager.draw()
