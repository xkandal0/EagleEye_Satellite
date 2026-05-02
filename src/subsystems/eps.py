# src/subsystems/eps.py

class EPS:
    def __init__(self):
        self.bateria_nivel = 100.0
        self.limite_seguro = 80.0
        self.modo_seguro_activo = False

    def actualizar_bateria(self, generacion_solar, consumo_total):
        balance = generacion_solar - consumo_total
        self.bateria_nivel += balance * 0.2
        
        if self.bateria_nivel > 100.0:
            self.bateria_nivel = 100.0
            
        if self.bateria_nivel < self.limite_seguro:
            self.modo_seguro_activo = True
        else:
            self.modo_seguro_activo = False
            
        return self.bateria_nivel