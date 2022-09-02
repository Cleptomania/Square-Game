import argparse


def launch_client():
    import arcade

    import square.client

    window = square.client.Window()

    square.client.set_window(window)
    window.show_view(window.views["main_menu"])
    arcade.run()


def launch_server(
    port: int,
    address: str = "127.0.0.1",
):
    from square.server import ServerApplication

    server = ServerApplication(
        address=address,
        port=port,
    )
    server.start()


def launcher():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", action="store_true")
    parser.add_argument("-a", "--address", default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=9000)

    args = parser.parse_args()

    if args.server:
        launch_server(
            address=args.address,
            port=args.port,
        )
    else:
        launch_client()


if __name__ == "__main__":
    launcher()
