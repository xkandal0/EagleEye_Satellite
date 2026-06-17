# src/core/main.py

import time
import math
import socket
from datetime import datetime, timedelta, timezone
from enum import Enum

from src.subsystems.eps import EPS
from src.subsystems.tcs import TCS
from src.subsystems.adcs import ADCS
from src.subsystems.comms import COMMS
from src.subsystems.obdh import OBDH
from src.hal.sensor_hub import SensorHub
from src.hal.orbital import SimuladorOrbital
from src.core.fdir_manager import FDIRManager

class ModoSatelite(Enum):
    INICIO = 1
    NOMINAL = 2
    SEGURO = 3

class OrdenadorABordo:
    def __init__(self):
        self.eps = EPS()
        self.tcs = TCS()
        self.adcs = ADCS()
        self.comms = COMMS()
        self.obdh = OBDH()
        self.sensores = SensorHub()
        self.fdir = FDIRManager()
        self.orbital = SimuladorOrbital()
        
        self.modo_actual = ModoSatelite.INICIO
        self.consumo_actual = 15.0
        
        self.bat_medida = 100.0
        self.temp_medida = 20.0
        self.en_cobertura = False
        
        self.tiempo_simulacion = datetime(2026, 6, 17, 12, 0, 0, tzinfo=timezone.utc)

        # Configuración de la Radio (Sockets UDP)
        self.udp_ip = "127.0.0.1"
        self.tx_port = 5005  # Enviar telemetría a la GS
        self.rx_port = 5006  # Recibir comandos de la GS
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.rx_port))
        self.sock.setblocking(False)  # Evita que el programa se congele esperando comandos

    def tarea_fisica_sensores(self):
        en_eclipse, self.en_cobertura = self.orbital.evaluar_entorno(self.tiempo_simulacion)
        angulo_error = self.adcs.actualizar_orientacion(en_eclipse)
        eficiencia_angulo = math.cos(math.radians(angulo_error))
        generacion_maxima = 40.0 if not en_eclipse else 0.0
        generacion_real = max(0.0, generacion_maxima * eficiencia_angulo)
        
        bat_real = self.eps.actualizar_bateria(generacion_real, self.consumo_actual)
        temp_real = self.tcs.actualizar_temperatura(en_eclipse, self.consumo_actual)
        
        self.bat_medida = self.sensores.leer_bateria(bat_real)
        self.temp_medida = self.sensores.leer_temperatura(temp_real)

    def tarea_fdir_modos(self, ciclo):
        en_peligro = self.fdir.evaluar_estado(self.bat_medida, self.temp_medida)
        
        if en_peligro and self.modo_actual != ModoSatelite.SEGURO:
            print(f"[{self.tiempo_simulacion.strftime('%H:%M:%S')}] >> TRANSICIÓN: Entrando en MODO SEGURO")
            self.modo_actual = ModoSatelite.SEGURO
        elif not en_peligro and self.modo_actual == ModoSatelite.SEGURO:
            print(f"[{self.tiempo_simulacion.strftime('%H:%M:%S')}] >> TRANSICIÓN: Recuperación a NOMINAL")
            self.modo_actual = ModoSatelite.NOMINAL
        elif not en_peligro and self.modo_actual == ModoSatelite.INICIO:
            if ciclo > 20: 
                print(f"[{self.tiempo_simulacion.strftime('%H:%M:%S')}] >> TRANSICIÓN: Arranque completado, entrando a NOMINAL")
                self.modo_actual = ModoSatelite.NOMINAL

        if self.modo_actual == ModoSatelite.INICIO or self.modo_actual == ModoSatelite.SEGURO:
            self.consumo_actual = 15.0
        elif self.modo_actual == ModoSatelite.NOMINAL and self.consumo_actual < 25.0:
            self.consumo_actual = 25.0

    def tarea_recepcion_comandos(self, ciclo):
        if not self.en_cobertura:
            return  # No puede recibir nada si no hay línea de visión

        try:
            datos, _ = self.sock.recvfrom(1024)
            comando_entrante = datos.decode('utf-8')
            print(f"[{self.tiempo_simulacion.strftime('%H:%M:%S')}] RX << Señal interceptada: {comando_entrante}")
            
            comando_procesado = self.comms.procesar_telecomando(comando_entrante)
            if comando_procesado:
                self.ejecutar_comando(comando_procesado)
        except BlockingIOError:
            pass  # No hay comandos en la cola en este momento

    def ejecutar_comando(self, comando):
        accion = comando.get("cmd")
        if accion == "PAYLOAD_ON" and self.modo_actual == ModoSatelite.NOMINAL:
            carga_w = comando.get("val", 0)
            self.consumo_actual += carga_w
            print(f"EJECUTANDO TC: Carga útil encendida (+{carga_w}W). Consumo total: {self.consumo_actual}W")
        elif accion == "PAYLOAD_ON":
            print("RECHAZADO: No se puede encender la carga útil fuera del modo NOMINAL.")

    def tarea_comunicaciones(self, ciclo):
        paquete_tx = self.comms.generar_paquete_telemetria(
            ciclo, self.modo_actual.name, self.bat_medida, self.temp_medida, self.consumo_actual
        )
        self.obdh.almacenar_paquete(paquete_tx)
        
        if self.en_cobertura:
            datos_volcados = self.obdh.volcar_memoria()
            if datos_volcados:
                print(f"[{self.tiempo_simulacion.strftime('%H:%M:%S')}] ====== TRANSMITIENDO {len(datos_volcados)} PAQUETES A GS ======")
                for paquete in datos_volcados:
                    # Envío real a través del socket UDP
                    self.sock.sendto(paquete.encode('utf-8'), (self.udp_ip, self.tx_port))

    def ejecutar_planificador(self):
        print("Iniciando FSW EagleEye-1 (Radio UDP Activada)...")
        ciclo = 0
        while True:
            ciclo += 1
            self.tiempo_simulacion += timedelta(minutes=1)
            
            self.tarea_fisica_sensores()
            self.tarea_fdir_modos(ciclo)
            self.tarea_recepcion_comandos(ciclo)
            
            if ciclo % 10 == 0:
                self.tarea_comunicaciones(ciclo)
            
            time.sleep(0.01)

if __name__ == "__main__":
    satelite = OrdenadorABordo()
    satelite.ejecutar_planificador()