# src/gs/ground_station.py

import socket
import json
import threading
import tkinter as tk
from tkinter import ttk

class GroundStation:
    def __init__(self, root):
        self.root = root
        self.root.title("Estación de Tierra - Madrid (AOS/LOS)")
        self.root.geometry("350x400")
        self.root.configure(padx=20, pady=20)

        # Configuración de Red (Simulación de Radiofrecuencia)
        self.udp_ip = "127.0.0.1"
        self.rx_port = 5005  # Puerto donde la GS escucha la telemetría
        self.tx_port = 5006  # Puerto para enviar telecomandos al satélite
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.rx_port))

        self.crear_interfaz()

        # Iniciar hilo de escucha en segundo plano para no bloquear la interfaz
        self.hilo_rx = threading.Thread(target=self.recibir_telemetria, daemon=True)
        self.hilo_rx.start()

    def crear_interfaz(self):
        ttk.Label(self.root, text="TELEMETRÍA EAGLEEYE-1", font=("Arial", 14, "bold")).pack(pady=10)

        # Panel de datos
        frame_datos = ttk.Frame(self.root)
        frame_datos.pack(fill="x", pady=10)

        ttk.Label(frame_datos, text="Modo Operativo:").grid(row=0, column=0, sticky="w", pady=5)
        self.lbl_modo = ttk.Label(frame_datos, text="ESPERANDO...", font=("Arial", 10, "bold"))
        self.lbl_modo.grid(row=0, column=1, sticky="e")

        ttk.Label(frame_datos, text="Batería:").grid(row=1, column=0, sticky="w", pady=5)
        self.lbl_bat = ttk.Label(frame_datos, text="-- %")
        self.lbl_bat.grid(row=1, column=1, sticky="e")

        ttk.Label(frame_datos, text="Temperatura:").grid(row=2, column=0, sticky="w", pady=5)
        self.lbl_temp = ttk.Label(frame_datos, text="-- ºC")
        self.lbl_temp.grid(row=2, column=1, sticky="e")

        ttk.Label(frame_datos, text="Consumo PWR:").grid(row=3, column=0, sticky="w", pady=5)
        self.lbl_pwr = ttk.Label(frame_datos, text="-- W")
        self.lbl_pwr.grid(row=3, column=1, sticky="e")
        
        ttk.Label(frame_datos, text="Último Ciclo RX:").grid(row=4, column=0, sticky="w", pady=5)
        self.lbl_ciclo = ttk.Label(frame_datos, text="--")
        self.lbl_ciclo.grid(row=4, column=1, sticky="e")

        # Separador
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=15)

        # Panel de Telecomandos
        ttk.Label(self.root, text="UPLINK (TELECOMANDOS)", font=("Arial", 12, "bold")).pack()
        self.btn_payload = ttk.Button(self.root, text="Encender Carga Útil (+10W)", command=self.enviar_comando)
        self.btn_payload.pack(pady=10)

    def recibir_telemetria(self):
        while True:
            try:
                datos, _ = self.sock.recvfrom(1024)
                paquete = json.loads(datos.decode('utf-8'))
                # Actualizar la interfaz desde el hilo principal
                self.root.after(0, self.actualizar_pantalla, paquete)
            except Exception as e:
                pass

    def actualizar_pantalla(self, paquete):
        self.lbl_modo.config(text=paquete.get("mod", "ERROR"))
        self.lbl_bat.config(text=f"{paquete.get('bat', 0):.1f} %")
        self.lbl_temp.config(text=f"{paquete.get('tmp', 0):.1f} ºC")
        self.lbl_pwr.config(text=f"{paquete.get('pwr', 0):.1f} W")
        self.lbl_ciclo.config(text=str(paquete.get("seq", 0)))

        # Cambiar color según estado
        if paquete.get("mod") == "SEGURO":
            self.lbl_modo.config(foreground="red")
        else:
            self.lbl_modo.config(foreground="green")

    def enviar_comando(self):
        # Generar un comando JSON y enviarlo por UDP
        comando = {"id": 999, "cmd": "PAYLOAD_ON", "val": 10}
        datos_tx = json.dumps(comando).encode('utf-8')
        self.sock.sendto(datos_tx, (self.udp_ip, self.tx_port))

if __name__ == "__main__":
    ventana = tk.Tk()
    app = GroundStation(ventana)
    ventana.mainloop()