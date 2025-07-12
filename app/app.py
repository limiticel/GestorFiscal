from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = "12345678"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return render_template("index.html")



@socketio.on("mensagem_cliente")
def handle_message(data):
  print(f"mensagem recebida: {data}")
  emit("mensagem_servidor",f"servidor recebeu: {data}", broadcast=True)


@socketio.on("disconnect")
def on_disconnect():
    print("Cliente desconectado")
    

if __name__ == "__main__":
    socketio.run(app, debug=True)