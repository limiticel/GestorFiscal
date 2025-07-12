from flask import Flask
from system_app import *

app,socket = create_app()


if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", debug = True)