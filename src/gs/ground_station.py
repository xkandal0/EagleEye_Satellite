# src/gs/ground_station.py

import socket
import threading
import json
from flask import Flask, render_template
from flask_socketio import SocketIO

import logging

# Silenciar los warnings de desarrollo y logs HTTP de Flask/Werkzeug
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Configuración de la aplicación web Flask
app = Flask(__name__, static_folder='web', template_folder='web')
app.config['SECRET_KEY'] = 'fsw_eagleeye_secret'

# Inicialización de SocketIO usando el modo nativo de hilos de Python
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# Parámetros de red locales
UDP_IP = "127.0.0.1"
GS_RX_PORT = 5005   # Puerto donde la GS escucha la telemetría del satélite
SAT_RX_PORT = 5006  # Puerto donde el satélite escucha los comandos de la GS

# Inicialización del socket UDP de radiofrecuencia
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, GS_RX_PORT))

def hilo_escucha_udp():
    """
    Rutina en segundo plano. Escucha los volcados de memoria masiva (UDP)
    del satélite y los emite por WebSocket hacia la interfaz web.
    """
    print(f"[*] Puente de radio activo. Escuchando telemetría en puerto {GS_RX_PORT}...")
    while True:
        try:
            datos, _ = udp_sock.recvfrom(8192)
            paquete_str = datos.decode('utf-8')
            paquete_json = json.loads(paquete_str)
            
            # Difusión inmediata a todos los navegadores web conectados
            socketio.emit('telemetria_satelite', paquete_json)
        except Exception as e:
            print(f"[ERROR UDP] Fallo al procesar paquete de telemetría: {e}")

@app.route('/')
def index():
    """Sirve la interfaz gráfica principalizada en el navegador"""
    return render_template('index.html')

@socketio.on('enviar_telecomando')
def handle_telecomando(data):
    """
    Recibe un comando desde la interfaz web (WebSocket) y lo 
    inyecta al canal de subida (UDP) hacia el ordenador de a bordo.
    """
    print(f"[*] Solicitud de Uplink recibida desde la web: {data}")
    try:
        datos_tx = json.dumps(data).encode('utf-8')
        udp_sock.sendto(datos_tx, (UDP_IP, SAT_RX_PORT))
        print(f"[UPLINK] Comando enviado al satélite en el puerto {SAT_RX_PORT}")
    except Exception as e:
        print(f"[ERROR UPLINK] No se pudo transmitir el comando: {e}")

if __name__ == '__main__':
    # Arrancar el hilo de escucha de radio antes de levantar el servidor web
    hilo_radio = threading.Thread(target=hilo_escucha_udp, daemon=True)
    hilo_radio.start()
    
    print("[*] Levantando el centro de control en http://127.0.0.1:5000")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)