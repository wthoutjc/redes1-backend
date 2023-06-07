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
full_message = ""
numero_secuencia = None

@socketio.on('message')
def on_message(*args):
    response = [json.loads(data) for data in args][0]
    global numero_secuencia

    # Crear trama
    inicio = int(str(response["indicator"]), 2)
    numero_secuencia = response["sequence"]

    flags = {
        "solicitar_confirmacion":response["requestConfirmation"],	
        "es_inicio_mensaje":response["startMessage"],
        "es_fin_mensaje":response["endMessage"],
        "enviar_confirmacion":response["sendConfirmation"],
    }

    datos = response["message"]
    trama = Trama(inicio, numero_secuencia, flags, datos)

    # Reglas    
    success, response_trama = rules.verificar_trama(trama)

    secuencia_tramas = rules.get_secuencia_tramas()
    socketio.emit('f-frame_sequence', secuencia_tramas)

    if success:
        socketio.emit('f-message', {
            "indicator":trama.inicio,
            "sequence":trama.numero_secuencia,
            "startMessage":trama.flags["es_inicio_mensaje"],                # SM
            "endMessage":trama.flags["es_fin_mensaje"],                     # EM
            "requestConfirmation":trama.flags["solicitar_confirmacion"],    # RC
            "sendConfirmation":trama.flags["enviar_confirmacion"],          # SC
            "message":trama.datos,
        })

        socketio.emit('f-response', {
            "indicator":response_trama.inicio,
            "sequence":response_trama.numero_secuencia,
            "startMessage":response_trama.flags["es_inicio_mensaje"],                # SM
            "endMessage":response_trama.flags["es_fin_mensaje"],                     # EM
            "requestConfirmation":response_trama.flags["solicitar_confirmacion"],    # RC
            "sendConfirmation":response_trama.flags["enviar_confirmacion"],          # SC
            "message":response_trama.datos,
        })

@socketio.on('b-response')
def on_response(*args):
    global full_message
    global numero_secuencia

    if numero_secuencia == 0:
        rules.add_secuencia_tramas({
            "message": f"Trama {len(rules.get_secuencia_tramas())} (Rx) Control, listo para recibir",
        })
        secuencia_tramas = rules.get_secuencia_tramas()
        socketio.emit('f-frame_sequence', secuencia_tramas)
    else:
        full_message += f"{args[0]} "
        socketio.emit('f-full_message', full_message)
    
    numero_secuencia = numero_secuencia + 1
    socketio.emit('f-current_plot', numero_secuencia)
    

@socketio.on('disconnect')
def on_disconnect():
    rules.clean_tramas()
    rules.secuencia_tramas.clear()
    print("Cliente desconectado satisfactoriamente")

if __name__ == '__main__':
    socketio.run(app, port=5000, host="0.0.0.0", debug=True)
    eventlet.monkey_patch(socket=True, select=True)        