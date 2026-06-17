# src/subsystems/adcs.py

class ADCS:
    def __init__(self):
        self.angulo_error = 0.0
        self.alineado = True
        
        # Parámetros de control ajustados
        self.tasa_deriva = 2.0       # El satélite pierde orientación lentamente (º/min)
        self.tasa_correccion = 6.0   # Los actuadores corrigen el error rápidamente al ver el Sol (º/min)

    def actualizar_orientacion(self, en_eclipse):
        if en_eclipse:
            # En la sombra no hay referencia solar; el satélite deriva de forma acumulativa
            self.angulo_error += self.tasa_deriva
            
            # Límite físico: 180 grados significa estar completamente al revés
            if self.angulo_error > 180.0:
                self.angulo_error = 180.0
        else:
            # Al salir al sol, los sensores guían la maniobra de re-apuntamiento
            if self.angulo_error > 0:
                self.angulo_error -= self.tasa_correccion
            
            if self.angulo_error < 0:
                self.angulo_error = 0.0

        # El estándar UNP-12 considera el satélite "alineado" si el error es menor a 5 grados
        self.alineado = self.angulo_error < 5.0
        
        return self.angulo_error