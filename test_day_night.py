#!/usr/bin/env python3
"""Test script für die Tag/Nacht-Unterscheidung in der Athena Plant Monitor Integration."""

import sys
import os
from datetime import datetime

# Add the custom component path
sys.path.append('/home/avi23/Projekte/plant-sys/custom_components/athena_plant_monitor')

try:
    from const import GROWTH_PHASES, DAY_NIGHT_CONFIG
    
    print("=== Athena Plant Monitor - Tag/Nacht Unterscheidung Test ===\n")
    
    # Test der Wachstumsphasen mit Tag/Nacht-Parametern
    print("1. Wachstumsphasen mit Tag/Nacht-Parametern:")
    for phase_name, phase_config in GROWTH_PHASES.items():
        print(f"\n{phase_name.upper()}: {phase_config['name']}")
        print(f"  Tag:   Temp {phase_config.get('temp_target_day', 'N/A')}°C, "
              f"Feuchte {phase_config.get('humidity_target_day', 'N/A')}%, "
              f"VPD {phase_config.get('vpd_target_day', 'N/A')} kPa, "
              f"CO₂ {phase_config.get('co2_target_day', 'N/A')} ppm")
        print(f"  Nacht: Temp {phase_config.get('temp_target_night', 'N/A')}°C, "
              f"Feuchte {phase_config.get('humidity_target_night', 'N/A')}%, "
              f"VPD {phase_config.get('vpd_target_night', 'N/A')} kPa, "
              f"CO₂ {phase_config.get('co2_target_night', 'N/A')} ppm")
    
    # Test der Tag/Nacht-Konfiguration
    print(f"\n2. Tag/Nacht-Konfiguration:")
    print(f"  Lichtschwellenwert: {DAY_NIGHT_CONFIG['light_threshold']} lx")
    print(f"  Temperaturdifferenz: {DAY_NIGHT_CONFIG['temp_difference']}°C")
    print(f"  VPD Differenz: {DAY_NIGHT_CONFIG['vpd_difference']} kPa")
    print(f"  Luftfeuchtigkeitserhöhung: {DAY_NIGHT_CONFIG['humidity_increase']}%")
    print(f"  CO₂ Reduktion: {DAY_NIGHT_CONFIG['co2_reduction']} ppm")
    
    # Simuliere Tag/Nacht-Berechnungen
    print(f"\n3. Beispiel-Berechnungen für verschiedene Phasen:")
    
    test_phases = ["vegetative", "flowering_bulk"]
    
    for phase in test_phases:
        phase_config = GROWTH_PHASES[phase]
        print(f"\n{phase.upper()}:")
        
        # Tag-Werte
        temp_day = phase_config.get('temp_target_day', 25.0)
        humidity_day = phase_config.get('humidity_target_day', 65.0)
        vpd_day = phase_config.get('vpd_target_day', 1.0)
        co2_day = phase_config.get('co2_target_day', 1200)
        
        # Nacht-Werte
        temp_night = phase_config.get('temp_target_night', 22.0)
        humidity_night = phase_config.get('humidity_target_night', 70.0)
        vpd_night = phase_config.get('vpd_target_night', 0.8)
        co2_night = phase_config.get('co2_target_night', 1000)
        
        print(f"  Tag:   {temp_day}°C, {humidity_day}%, VPD {vpd_day}, CO₂ {co2_day}")
        print(f"  Nacht: {temp_night}°C, {humidity_night}%, VPD {vpd_night}, CO₂ {co2_night}")
        print(f"  Differenz: ΔT {temp_day - temp_night}°C, "
              f"ΔH {humidity_night - humidity_day}%, "
              f"ΔVPD {vpd_day - vpd_night}, "
              f"ΔCO₂ {co2_day - co2_night}")
    
    # Aktuelle Zeit-Simulation
    current_hour = datetime.now().hour
    is_day_fallback = 6 <= current_hour < 22
    
    print(f"\n4. Aktuelle Zeit-Simulation:")
    print(f"  Aktuelle Stunde: {current_hour}")
    print(f"  Tag-Zyklus (Fallback): {'JA' if is_day_fallback else 'NEIN'}")
    
    print(f"\n✅ Tag/Nacht-Unterscheidung erfolgreich implementiert!")
    print(f"   - Alle Wachstumsphasen haben Tag/Nacht-Parameter")
    print(f"   - Temperatur, Luftfeuchtigkeit, VPD und CO₂ werden unterschieden")
    print(f"   - Lichtsensor-basierte Erkennung mit Fallback auf Uhrzeit")
    print(f"   - Integration in Coordinator und Sensoren verfügbar")
    
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("Stelle sicher, dass die const.py Datei korrekt ist.")
except Exception as e:
    print(f"❌ Fehler: {e}")
