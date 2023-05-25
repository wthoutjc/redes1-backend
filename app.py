from flask import Flask #, jsonify, make_response, request, Response
from flask_socketio import SocketIO
from flask_cors import CORS

import eventlet

# Tools
from decouple import config
import os

time_zone = config('TZ')
os.environ['TZ'] = time_zone

app = Flask(__name__)
SECRET_KEY = config('SECRET_KEY')
CORS(app)

app.config['SECRET_KEY'] = SECRET_KEY

socketio = SocketIO(app, cors_allowed_origins='*', async_mode="threading", websocket=True, max_http_buffer_size=1024*1024*1024)

@socketio.on('connect')
def on_connect():
    print(f'Cliente ff conectado satisfactoriamente')

@socketio.on('disconnect')
def on_disconnect():
    print(f'Cliente ff desconectado satisfactoriamente.')

if __name__ == '__main__':
    socketio.run(app, port=5000, host="0.0.0.0", debug=True)
    eventlet.monkey_patch(socket=True, select=True)        