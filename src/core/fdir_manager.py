# src/core/fdir_manager.py

class FDIRManager:
    def __init__(self):
        self.modo_seguro = False
        
        # Contadores de persistencia
        self.ciclos_fallo_energia = 0
        self.ciclos_fallo_termico = 0
        
        # Umbral de confirmación (requisito UNP-12)
        self.limite_persistencia = 3 

    def evaluar_estado(self, bateria, temperatura):
        # 1. DETECCIÓN INSTANTÁNEA
        anomalia_energia = bateria < 80.0
        anomalia_termica = temperatura > 40.0 or temperatura < 0.0
        
        # 2. FILTRADO DE PERSISTENCIA
        if anomalia_energia:
            self.ciclos_fallo_energia += 1
        else:
            self.ciclos_fallo_energia = 0  # Auto-recuperación si el ruido desaparece

        if anomalia_termica:
            self.ciclos_fallo_termico += 1
        else:
            self.ciclos_fallo_termico = 0

        # 3. AISLAMIENTO (Confirmación del fallo)
        fallo_confirmado = (self.ciclos_fallo_energia >= self.limite_persistencia or 
                            self.ciclos_fallo_termico >= self.limite_persistencia)

        if fallo_confirmado:
            self.modo_seguro = True
        
        # 4. RECUPERACIÓN (Histéresis estricta para salir del modo seguro)
        elif self.modo_seguro:
            recuperacion_energia = bateria > 90.0
            recuperacion_termica = 5.0 < temperatura < 35.0
            
            if recuperacion_energia and recuperacion_termica:
                self.modo_seguro = False
                self.ciclos_fallo_energia = 0
                self.ciclos_fallo_termico = 0

        return self.modo_seguro