# src/subsystems/obdh.py

class OBDH:
    def __init__(self):
        self.memoria_masiva = []
        self.limite_memoria = 5000  # Máximo de paquetes almacenables

    def almacenar_paquete(self, paquete_json):
        if len(self.memoria_masiva) < self.limite_memoria:
            self.memoria_masiva.append(paquete_json)
        else:
            # Comportamiento circular: sobrescribe los datos más antiguos si se llena
            self.memoria_masiva.pop(0)
            self.memoria_masiva.append(paquete_json)

    def volcar_memoria(self):
        paquetes_a_enviar = self.memoria_masiva.copy()
        self.memoria_masiva.clear()
        return paquetes_a_enviar