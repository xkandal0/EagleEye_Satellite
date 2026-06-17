# src/subsystems/tcs.py

class TCS:
    def __init__(self):
        self.temperatura_actual = 20.0
        self.limite_max = 40.0
        self.limite_min = 0.0
        self.alerta_termica = False
        
        # Parámetros termodinámicos físicos
        self.temp_equilibrio_sol = 60.0    # Temperatura máxima del chasis al sol
        self.temp_equilibrio_eclipse = -30.0 # Temperatura mínima en el vacío
        self.inercia_termica = 0.05        # Velocidad de transferencia de calor (k)

    def actualizar_temperatura(self, en_eclipse, calor_equipos):
        # 1. Determinar el entorno exterior
        temp_ambiente = self.temp_equilibrio_eclipse if en_eclipse else self.temp_equilibrio_sol
        
        # 2. Ley de Enfriamiento de Newton
        # La velocidad de cambio depende de la diferencia térmica con el exterior
        delta_ambiente = (temp_ambiente - self.temperatura_actual) * self.inercia_termica
        
        # 3. Calor disipado internamente por la electrónica (Efecto Joule)
        calor_interno = calor_equipos * 0.05
        
        # 4. Calcular nueva temperatura neta
        self.temperatura_actual += (delta_ambiente + calor_interno)
        
        # 5. Comprobación FDIR
        if self.temperatura_actual > self.limite_max or self.temperatura_actual < self.limite_min:
            self.alerta_termica = True
        else:
            self.alerta_termica = False
            
        return self.temperatura_actual