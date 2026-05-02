# src/core/fdir_manager.py

class FDIRManager:
    def __init__(self):
        self.modo_seguro = False

    def evaluar_estado(self, bateria, temperatura):
        # 1. DETECCIÓN (Fault Detection)
        fallo_energia = bateria < 80.0
        fallo_termico = temperatura > 40.0 or temperatura < 0.0
        
        if fallo_energia or fallo_termico:
            # 2. AISLAMIENTO (Isolation)
            self.modo_seguro = True
        else:
            # 3. RECUPERACIÓN (Recovery)
            # Solo volvemos a la normalidad si los parámetros son muy seguros
            recuperacion_energia = bateria > 90.0
            recuperacion_termica = 5.0 < temperatura < 35.0
            
            if recuperacion_energia and recuperacion_termica:
                self.modo_seguro = False

        return self.modo_seguro