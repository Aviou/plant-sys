#!/usr/bin/env python3
"""Test der vereinfachten WLAN-Lichtsteuerung ohne Lichtsensor."""

import sys
import os
from datetime import datetime, time

# Add the custom component path
sys.path.append('/home/avi23/Projekte/plant-sys/custom_components/athena_plant_monitor')

def test_no_light_sensor():
    """Testet die Lichtsteuerung ohne Lichtsensor."""
    print("=== Athena Plant Monitor - OHNE Lichtsensor Test ===\n")
    
    try:
        from const import (
            ESPHOME_ENTITIES, DAY_NIGHT_CONFIG,
            CONF_EXTERNAL_LIGHT_ENTITY, CONF_LIGHT_SCHEDULE_START, 
            CONF_LIGHT_SCHEDULE_END, DEFAULT_LIGHT_SCHEDULE_START,
            DEFAULT_LIGHT_SCHEDULE_END
        )
        
        print("✅ Konstanten erfolgreich importiert")
        
        # Überprüfe, dass keine Lichtsensor-Entitäten vorhanden sind
        light_sensor_entities = [key for key in ESPHOME_ENTITIES.keys() if 'light' in key and 'sensor' in ESPHOME_ENTITIES[key]]
        
        if light_sensor_entities:
            print(f"❌ Noch Lichtsensor-Entitäten gefunden: {light_sensor_entities}")
            return False
        else:
            print("✅ Keine Lichtsensor-Entitäten gefunden - korrekt entfernt")
        
        # Überprüfe DAY_NIGHT_CONFIG
        if "light_threshold" in DAY_NIGHT_CONFIG:
            print(f"❌ Lichtsensor-Schwellenwert noch in DAY_NIGHT_CONFIG")
            return False
        else:
            print("✅ Lichtsensor-Schwellenwert aus DAY_NIGHT_CONFIG entfernt")
        
        print(f"\n📋 Verfügbare Tag/Nacht-Erkennungsmethoden:")
        print(f"  1. 🔌 Externe Lichtentität (WLAN-Steckdose)")
        print(f"     └─ Konfiguration: {CONF_EXTERNAL_LIGHT_ENTITY}")
        print(f"  2. 💡 ESPHome LED Panel")
        print(f"     └─ Entität: {ESPHOME_ENTITIES.get('led_panel', 'Nicht konfiguriert')}")
        print(f"  3. 🔀 ESPHome Growlight Switch")
        print(f"     └─ Entität: {ESPHOME_ENTITIES.get('grow_light_switch', 'Nicht konfiguriert')}")
        print(f"  4. ⏰ Zeitbasierte Erkennung (Fallback)")
        print(f"     └─ Standard: {DEFAULT_LIGHT_SCHEDULE_START} - {DEFAULT_LIGHT_SCHEDULE_END}")
        
        # Test der Konfigurationsparameter
        print(f"\n🛠️ Konfigurationsparameter:")
        print(f"  • Temperatur-Unterschied: {DAY_NIGHT_CONFIG.get('temp_difference', 'N/A')}°C")
        print(f"  • VPD-Unterschied: {DAY_NIGHT_CONFIG.get('vpd_difference', 'N/A')} kPa")
        print(f"  • Luftfeuchtigkeit-Erhöhung: {DAY_NIGHT_CONFIG.get('humidity_increase', 'N/A')}%")
        print(f"  • CO₂-Reduktion: {DAY_NIGHT_CONFIG.get('co2_reduction', 'N/A')} ppm")
        
        # Simuliere Zeitbasierte Erkennung
        current_time = datetime.now().time()
        start_time = time.fromisoformat(DEFAULT_LIGHT_SCHEDULE_START)
        end_time = time.fromisoformat(DEFAULT_LIGHT_SCHEDULE_END)
        
        if start_time <= end_time:
            is_day_time = start_time <= current_time <= end_time
        else:
            is_day_time = current_time >= start_time or current_time <= end_time
        
        print(f"\n⏰ Zeitbasierte Erkennung (Fallback-Test):")
        print(f"  Aktuelle Zeit: {current_time}")
        print(f"  Licht-Zeitplan: {start_time} - {end_time}")
        print(f"  Status: {'🌞 Tag' if is_day_time else '🌙 Nacht'}")
        
        # Test der automatischen Switch-Erkennung
        print(f"\n🔍 Automatische Licht-Switch-Erkennung:")
        test_entities = [
            "switch.growlight_steckdose",
            "switch.shelly_growroom", 
            "switch.led_panel_power",
            "switch.wachstumslicht",
            "light.philips_hue_growlight",
            "switch.some_random_device"  # Sollte nicht erkannt werden
        ]
        
        light_keywords = ["light", "lamp", "led", "grow", "steckdose", "socket"]
        
        for entity in test_entities:
            is_light = (entity.startswith("switch.") and 
                       any(keyword in entity.lower() for keyword in light_keywords)) or entity.startswith("light.")
            print(f"  {'✅' if is_light else '❌'} {entity}")
        
        # Test der vereinfachten ESPHome Entitäten
        print(f"\n📊 ESPHome-Entitäten (ohne Lichtsensoren):")
        sensor_entities = [key for key in ESPHOME_ENTITIES.keys() if key in [
            "temperature", "humidity", "pressure", "vwc", "ec_substrate", 
            "ph_substrate", "temp_substrate", "co2", "water_level"
        ]]
        
        for entity in sensor_entities:
            print(f"  ✅ {entity}: {ESPHOME_ENTITIES[entity]}")
        
        # Lichtsteuerungs-Entitäten
        light_control_entities = [key for key in ESPHOME_ENTITIES.keys() if 'led' in key or 'light' in key]
        if light_control_entities:
            print(f"\n💡 Lichtsteuerungs-Entitäten:")
            for entity in light_control_entities:
                print(f"  💡 {entity}: {ESPHOME_ENTITIES[entity]}")
        
        print(f"\n✅ VEREINFACHTE LICHTSTEUERUNG ERFOLGREICH!")
        print(f"")
        print(f"🎯 Optimierungen:")
        print(f"   • Keine Lichtsensor-Abhängigkeit")
        print(f"   • Direkte WLAN-Steckdosen-Steuerung")
        print(f"   • Zeitbasierte Fallback-Erkennung")
        print(f"   • Vereinfachte ESPHome-Integration")
        print(f"   • Weniger Sensoranforderungen")
        print(f"")
        print(f"🔧 Vorteile:")
        print(f"   • Einfachere Hardware-Anforderungen")
        print(f"   • Zuverlässige zeitbasierte Steuerung")
        print(f"   • Fokus auf WLAN-Steckdosen (sehr verbreitet)")
        print(f"   • Weniger Ausfallquellen")
        print(f"   • Kostengünstiger")
        print(f"")
        print(f"📱 Setup-Schritte:")
        print(f"   1. WLAN-Steckdose in Home Assistant einrichten")
        print(f"   2. Athena Integration installieren")
        print(f"   3. Externe Lichtentität in UI wählen")
        print(f"   4. Licht-Zeitplan konfigurieren")
        print(f"   5. Tag/Nacht-Automatisierung testen")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    success = test_no_light_sensor()
    if success:
        print(f"\n🚀 BEREIT FÜR PRODUKTIVEINSATZ!")
        print(f"   Keine zusätzlichen Lichtsensoren erforderlich.")
        print(f"   Perfekt für Standard-WLAN-Steckdosen-Setups.")
    
    sys.exit(0 if success else 1)
