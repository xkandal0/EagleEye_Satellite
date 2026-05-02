# src/core/main.py

import time
import math
from src.subsystems.eps import EPS
from src.subsystems.tcs import TCS
from src.subsystems.adcs import ADCS
from src.hal.sensor_hub import SensorHub
from src.core.fdir_manager import FDIRManager

class OrdenadorABordo:
    def __init__(self):
        # Subsistemas
        self.eps = EPS()
        self.tcs = TCS()
        self.adcs = ADCS()
        self.sensores = SensorHub()
        self.fdir = FDIRManager()
        
        # Estado operativo
        self.consumo_base = 15.0
        self.consumo_operativo = 25.0
        self.consumo_actual = self.consumo_base

    def ejecutar_ciclo(self):
        print("Iniciando FSW EagleEye-1 con Gestor FDIR independiente...")
        ciclo = 0
        
        while True:
            ciclo += 1
            
            # --- FÍSICA EXTERNA ---
            fase_orbita = math.sin(ciclo * 0.2)
            en_eclipse = fase_orbita < 0
            
            # --- SUBSISTEMAS (Verdad fundamental) ---
            angulo_error = self.adcs.actualizar_orientacion(en_eclipse)
            eficiencia_angulo = math.cos(math.radians(angulo_error))
            
            generacion_maxima = 40.0 * fase_orbita if not en_eclipse else 0.0
            generacion_real = generacion_maxima * eficiencia_angulo
            
            bat_real = self.eps.actualizar_bateria(generacion_real, self.consumo_actual)
            temp_real = self.tcs.actualizar_temperatura(en_eclipse, self.consumo_actual)
            
            # --- SENSORES (Con ruido) ---
            bat_medida = self.sensores.leer_bateria(bat_real)
            temp_medida = self.sensores.leer_temperatura(temp_real)
            
            # --- GESTOR DE EMERGENCIAS (FDIR) ---
            en_peligro = self.fdir.evaluar_estado(bat_medida, temp_medida)
            
            if en_peligro:
                self.consumo_actual = self.consumo_base
                estado_fdir = "MODO SEGURO ACTIVO"
            else:
                self.consumo_actual = self.consumo_operativo
                estado_fdir = "NOMINAL"

            # --- TELEMETRÍA ---
            estado_adcs = "OK" if self.adcs.alineado else "DESVIADO"
            print(f"[{ciclo:03d}] BAT: {bat_medida}% | TEMP: {temp_medida}ºC | SOL: {generacion_real:.1f}W | ADCS: {estado_adcs} | FDIR: {estado_fdir}")
            
            time.sleep(0.5)

if __name__ == "__main__":
    satelite = OrdenadorABordo()
    satelite.ejecutar_ciclo()