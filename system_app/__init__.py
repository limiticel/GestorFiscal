from flask import Flask
from flask_socketio import SocketIO

socketio= SocketIO(cors_allowed_origins="*") #instancia um servidor da classe socketio (Websocket)

def create_app():  #função inicial(cria a aplicação geral)
    app = Flask(__name__)  #instancia a classe Flask 
    app.config["SECRET_KEY"]  =  '12345678'
    socketio.init_app(app)

    from .routes import set_routes
    set_routes(app)


    return app, socketio