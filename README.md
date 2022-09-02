# Square Game

This is an example of a multiplayer game built with Python using the [Arcade](https://github.com/pythonarcade/arcade) library. In addition, it utilizes a slightly modified version of [Esper](https://github.com/benmoran56/esper)

# Installing

Simply run the following command:

```
python -m pip install .
```

# Running the Game

The game has two separate components, the client and the server. 

## Running the Server

You can run the server with the command:

```
python -m square -s
```

You can also provide the following options to the server command:

- `-a`, `--address` - the address to bind to, defaults to 127.0.0.1
- `-p`, `--port` - the port number to use, defaults to 9000

## Running the Client

Simply run:

```
python -m square
```