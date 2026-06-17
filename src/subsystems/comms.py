# src/subsystems/comms.py

import json

class COMMS:
    def __init__(self):
        self.enlace_activo = True

    def generar_paquete_telemetria(self, ciclo, modo, bateria, temperatura, consumo, latitud, longitud):
        paquete = {
            "seq": ciclo,
            "mod": modo,
            "bat": bateria,
            "tmp": temperatura,
            "pwr": consumo,
            "lat": latitud,
            "lon": longitud
        }
        return json.dumps(paquete)

    def procesar_telecomando(self, comando_raw):
        try:
            comando = json.loads(comando_raw)
            return comando
        except json.JSONDecodeError:
            print("ERROR COMMS: Paquete de telecomando corrupto.")
            return None