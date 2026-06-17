# src/hal/orbital.py

from skyfield.api import load, EarthSatellite, wgs84

class SimuladorOrbital:
    def __init__(self):
        self.ts = load.timescale()
        self.efemerides = load('de421.bsp')
        
        linea1 = '1 25544U 98067A   24168.12345678  .00016717  00000-0  30268-3 0  9002'
        linea2 = '2 25544  51.6402 181.2055 0005251 319.4629 173.4764 15.49221687563539'
        self.satelite = EarthSatellite(linea1, linea2, 'EagleEye-1', self.ts)
        
        # Coordenadas de la Estación de Tierra (Madrid)
        self.estacion_control = wgs84.latlon(40.4168, -3.7038)

    def evaluar_entorno(self, tiempo_actual):
        t = self.ts.from_datetime(tiempo_actual)
        geocentrica = self.satelite.at(t)
        
        # 1. Cálculo de Eclipse
        en_eclipse = not geocentrica.is_sunlit(self.efemerides)
        
        # 2. Cálculo de Visibilidad (AOS/LOS)
        diferencia = self.satelite - self.estacion_control
        topocentrica = diferencia.at(t)
        alt, az, distance = topocentrica.altaz()
        en_cobertura = alt.degrees > 10.0
        
        # 3. NUEVO: Cálculo Geográfico (Nadir)
        subpunto = wgs84.subpoint_of(geocentrica)
        latitud = subpunto.latitude.degrees
        longitud = subpunto.longitude.degrees
        
        return en_eclipse, en_cobertura, latitud, longitud