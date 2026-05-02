# src/subsystems/tcs.py

class TCS:
    def __init__(self):
        self.temperatura_actual = 20.0  # Empezamos a 20ºC
        self.limite_max = 40.0
        self.limite_min = 0.0
        self.alerta_termica = False

    def actualizar_temperatura(self, en_eclipse, calor_equipos):
        # El calor de los equipos afecta a la temperatura interna
        factor_calor = calor_equipos * 0.05
        
        if en_eclipse:
            # En la sombra de la Tierra, el satélite se enfría
            self.temperatura_actual -= (0.8 - factor_calor)
        else:
            # Al sol, el satélite se calienta
            self.temperatura_actual += (1.2 + factor_calor)
            
        # Comprobación de seguridad térmica
        if self.temperatura_actual > self.limite_max or self.temperatura_actual < self.limite_min:
            self.alerta_termica = True
        else:
            self.alerta_termica = False
            
        return self.temperatura_actual