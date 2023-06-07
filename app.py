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
    global numero_secuencia
    response = [json.loads(data) for data in args][0]

    # Crear trama
    inicio = int(str(response["indicator"]), 2)
    numero_secuencia = response["sequence"]
    rules.set_num_frames(response["frames"])

    flags = {
        "solicitar_confirmacion":response["requestConfirmation"],	
        "es_inicio_mensaje":response["startMessage"],
        "es_fin_mensaje":response["endMessage"],
        "enviar_confirmacion":response["sendConfirmation"],
    }

    datos = response.get("message") or ''
    trama = Trama(inicio, numero_secuencia, flags, datos)

    if not trama.es_valida():
        rules.add_secuencia_tramas({
            "error": f"Trama (Tx), la trama no cumple con las reglas",
        })

        secuencia_tramas = rules.get_secuencia_tramas()
        socketio.emit('f-frame_sequence', secuencia_tramas)
        return

    # Reglas
    success, response_trama = rules.verificar_trama(trama)

    secuencia_tramas = rules.get_secuencia_tramas()
    socketio.emit('f-frame_sequence', secuencia_tramas)

    if success:
        # Transmisor
        socketio.emit('f-message', {
            "indicator":trama.inicio,
            "sequence":trama.numero_secuencia,
            "startMessage":trama.flags["es_inicio_mensaje"],                # SM
            "endMessage":trama.flags["es_fin_mensaje"],                     # EM
            "requestConfirmation":trama.flags["solicitar_confirmacion"],    # RC
            "sendConfirmation":trama.flags["enviar_confirmacion"],          # SC
            "message":trama.datos,
        })

        # Respuesta
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

    if rules.rc == 0:
        rules.rc = 1
        rules.sc = 1
        numero_secuencia = 1
        rules.add_secuencia_tramas({
            "message": f"Trama (Rx) Control, listo para recibir",
        })
    else:
        rules.sc = 1
        full_message += f"{args[0]}"
        socketio.emit('f-full_message', full_message)
        rules.add_secuencia_tramas({
            "message": f"Trama (Rx) Datos, trama recibida",
        })

        if int(numero_secuencia) == int(rules.frames):
            rules.rc = 0
            numero_secuencia = 0
            # TODO: Llamar un evento para que borre el mensaje y el número de frames.
        else:
            numero_secuencia += 1

    secuencia_tramas = rules.get_secuencia_tramas()
    socketio.emit('f-frame_sequence', secuencia_tramas)
    socketio.emit('f-current_plot', numero_secuencia)
    

@socketio.on('disconnect')
def on_disconnect():
    rules.rc = 0
    rules.sc = 0
    rules.frames = 0
    rules.clean_tramas()
    rules.secuencia_tramas.clear()
    print("Cliente desconectado satisfactoriamente")

if __name__ == '__main__':
    socketio.run(app, port=5000, host="0.0.0.0", debug=True)
    eventlet.monkey_patch(socket=True, select=True)        