from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

import eventlet

# Tools
from decouple import config
import os
import json

time_zone = config('TZ')
os.environ['TZ'] = time_zone

app = Flask(__name__)
SECRET_KEY = config('SECRET_KEY')
CORS(app)

app.config['SECRET_KEY'] = SECRET_KEY

socketio = SocketIO(app, cors_allowed_origins='*', async_mode="threading", websocket=True, max_http_buffer_size=1024*1024*1024)

from src.trama.trama import Trama
from src.rules.rules import Rules

rules = Rules(socketio)
secuencia_tramas = []

@socketio.on('message')
def on_message(*args):
    response = [json.loads(data) for data in args][0]

    print(response["indicator"])
    # Crear trama
    inicio = int(str(response["indicator"]), 2)
    numero_secuencia = response["sequence"]
    es_inicio_mensaje = response["startMessage"]
    es_fin_mensaje = response["endMessage"]
    solicitar_confirmacion = response["requestConfirmation"]
    datos = response["message"]

    trama = Trama(inicio, numero_secuencia, es_inicio_mensaje, es_fin_mensaje, solicitar_confirmacion, datos)
    rules.add_trama(trama)

    numero_secuencia = trama.numero_secuencia + 1
    socketio.emit('f-message', {
        "indicator":trama.inicio,
        "sequence":trama.numero_secuencia,
        "startMessage":trama.es_inicio_mensaje,
        "endMessage":trama.es_fin_mensaje,
        "requestConfirmation":trama.solicitar_confirmacion,
        "message":trama.datos,
    })
    socketio.emit('f-current_plot', numero_secuencia)

@socketio.on('disconnect')
def on_disconnect():
    rules.clean_tramas()
    secuencia_tramas.clear()
    print("Cliente desconectado satisfactoriamente")

if __name__ == '__main__':
    socketio.run(app, port=5000, host="0.0.0.0", debug=True)
    eventlet.monkey_patch(socket=True, select=True)        