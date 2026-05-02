# src/subsystems/adcs.py

class ADCS:
    def __init__(self):
        # Ángulo respecto al sol. 0 grados es alineación perfecta.
        self.angulo_error = 0.0
        self.alineado = True

    def actualizar_orientacion(self, en_eclipse):
        if en_eclipse:
            # En la sombra, perdemos la referencia del sol y el satélite deriva lentamente
            self.angulo_error += 5.0
            self.alineado = False
        else:
            # Al salir al sol, los motores corrigen la posición reduciendo el error
            if self.angulo_error > 0:
                self.angulo_error -= 3.0
            
            # Se considera alineado si el error es menor a 10 grados
            self.alineado = self.angulo_error < 10.0

        if self.angulo_error < 0:
            self.angulo_error = 0.0
            
        return self.angulo_error