"""
Orbit Calculator Module
Calculates fundamental orbital parameters based on the Mission Requirements Document (MRD).
"""

import numpy as np

def calculate_orbit_parameters(altitude_km):
    """
    Calculates orbital period and worst-case eclipse time for a circular Low Earth Orbit.
    
    Parameters:
        altitude_km (float): Orbit altitude in kilometers.
        
    Returns:
        tuple: (period_minutes, eclipse_minutes)
    """
    # Earth constants
    R_EARTH_KM = 6371.0
    MU_EARTH_KM3_S2 = 398600.4418
    
    # 1. Calculate orbital radius
    r_orbit_km = R_EARTH_KM + altitude_km
    
    # 2. Calculate orbital period (Kepler's Third Law)
    # T = 2 * pi * sqrt(r^3 / mu)
    period_sec = 2 * np.pi * np.sqrt((r_orbit_km**3) / MU_EARTH_KM3_S2)
    period_min = period_sec / 60.0
    
    # 3. Calculate eclipse time (Cylindrical shadow model, Beta angle = 0)
    # The half-angle of the shadow cylinder
    theta_rad = np.arcsin(R_EARTH_KM / r_orbit_km)
    
    # Total shadow angle is 2 * theta
    fraction_in_shadow = (2 * theta_rad) / (2 * np.pi)
    eclipse_min = period_min * fraction_in_shadow
    
    return period_min, eclipse_min

if __name__ == "__main__":
    # Test the function using [REQ-ORB-020]
    target_altitude = 500.0 # km
    
    period, eclipse = calculate_orbit_parameters(target_altitude)
    
    print("=========================================")
    print(f" MISSION ORBIT ANALYSIS (Altitude: {target_altitude} km)")
    print("=========================================")
    print(f" Orbital Period:  {period:.2f} minutes")
    print(f" Eclipse Time:    {eclipse:.2f} minutes")
    print(f" Sunlight Time:   {(period - eclipse):.2f} minutes")
    print("=========================================")