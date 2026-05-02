# src/hal/sensor_hub.py

import random

class SensorHub:
    def __init__(self):
        # 5% de probabilidad de que un sensor falle por un pico de radiación
        self.probabilidad_fallo = 0.05 

    def leer_bateria(self, valor_real):
        # El sensor de voltaje tiene un pequeño margen de error (ruido gaussiano)
        ruido = random.gauss(0, 0.3)
        valor_medido = valor_real + ruido
        return round(valor_medido, 2)

    def leer_temperatura(self, valor_real):
        # Ruido térmico normal
        ruido = random.gauss(0, 0.5)
        valor_medido = valor_real + ruido
        
        # Simulación de Single Event Upset (SEU): un impacto de radiación ciega el sensor un instante
        if random.random() < self.probabilidad_fallo:
            # Añade un pico de calor o frío irreal
            valor_medido += random.choice([-15.0, 20.0]) 
            
        return round(valor_medido, 2)