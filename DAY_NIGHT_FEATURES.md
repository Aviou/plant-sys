# Tag/Nacht-Unterscheidung - Übersicht

## ✅ Implementierte Features

### 🌓 Automatische Tag/Nacht-Erkennung
- **Primär**: Lichtsensor-basierte Erkennung über konfigurierbaren Schwellenwert (10.000 lx)
- **Sekundär**: Wachstumslampen-Status (wenn Lichtsensor nicht verfügbar)
- **Fallback**: Zeitbasierte Erkennung (6:00-22:00 = Tag)

### 📊 Dynamische Zielwerte pro Wachstumsphase

#### Vegetative Phase
| Parameter | Tag | Nacht | Unterschied |
|-----------|-----|-------|-------------|
| Temperatur | 25.0°C | 22.0°C | -3.0°C |
| Luftfeuchtigkeit | 65.0% | 70.0% | +5.0% |
| VPD | 0.9 kPa | 0.7 kPa | -0.2 kPa |
| CO₂ | 1200 ppm | 1000 ppm | -200 ppm |

#### Flowering Stretch
| Parameter | Tag | Nacht | Unterschied |
|-----------|-----|-------|-------------|
| Temperatur | 24.0°C | 21.0°C | -3.0°C |
| Luftfeuchtigkeit | 60.0% | 65.0% | +5.0% |
| VPD | 1.0 kPa | 0.8 kPa | -0.2 kPa |
| CO₂ | 1400 ppm | 1200 ppm | -200 ppm |

#### Flowering Bulk
| Parameter | Tag | Nacht | Unterschied |
|-----------|-----|-------|-------------|
| Temperatur | 22.0°C | 19.0°C | -3.0°C |
| Luftfeuchtigkeit | 55.0% | 60.0% | +5.0% |
| VPD | 1.2 kPa | 1.0 kPa | -0.2 kPa |
| CO₂ | 1500 ppm | 1300 ppm | -200 ppm |

#### Flowering Finish
| Parameter | Tag | Nacht | Unterschied |
|-----------|-----|-------|-------------|
| Temperatur | 20.0°C | 17.0°C | -3.0°C |
| Luftfeuchtigkeit | 50.0% | 55.0% | +5.0% |
| VPD | 1.4 kPa | 1.2 kPa | -0.2 kPa |
| CO₂ | 1200 ppm | 1000 ppm | -200 ppm |

### 🎛️ Home Assistant Integration

#### Neue Sensoren
- **`sensor.athena_temperature_target`**: Dynamisches Temperaturziel (Tag/Nacht)
- **`sensor.athena_humidity_target`**: Dynamisches Luftfeuchtigkeitsziel (Tag/Nacht)
- **`sensor.athena_co2_target`**: Dynamisches CO₂-Ziel (Tag/Nacht)
- **`sensor.athena_vpd_target`**: Dynamisches VPD-Ziel (Tag/Nacht)
- **`sensor.athena_is_day_cycle`**: Zeigt "Tag" oder "Nacht" an

#### Erweiterte Klimasteuerung
- **Automatische Anpassung**: Alle Klimastrategien berücksichtigen jetzt Tag/Nacht-Ziele
- **VPD-Optimierung**: Passt sich automatisch an Tag/Nacht-VPD-Ziele an
- **Smarte Ventilation**: Lüftungsempfehlungen basierend auf aktuellen Zielen

### 🔧 Konfiguration

#### Anpassbare Parameter in `const.py`
```python
DAY_NIGHT_CONFIG = {
    "light_threshold": 10000,  # lx - Schwellenwert für Tag/Nacht
    "temp_difference": 3.0,    # °C - Standard Nachtabsenkung
    "vpd_difference": 0.2,     # kPa - Standard VPD Reduktion nachts
    "humidity_increase": 5.0,  # % - Standard Luftfeuchtigkeitserhöhung nachts
    "co2_reduction": 200,      # ppm - Standard CO₂ Reduktion nachts
}
```

### 🚀 Automatisierungsbeispiele

#### Automatische Tag/Nacht-Umschaltung
```yaml
automation:
  - alias: "Athena Tag/Nacht Zielwerte"
    trigger:
      - platform: state
        entity_id: sensor.athena_is_day_cycle
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.grow_room
        data:
          temperature: "{{ states('sensor.athena_temperature_target') | float }}"
      - service: climate.set_humidity
        target:
          entity_id: climate.grow_room
        data:
          humidity: "{{ states('sensor.athena_humidity_target') | float }}"
```

#### VPD-optimierte Klimasteuerung
```yaml
automation:
  - alias: "VPD Optimierung Tag/Nacht"
    trigger:
      - platform: time_pattern
        minutes: "/15"  # Alle 15 Minuten prüfen
    condition:
      - condition: state
        entity_id: switch.athena_vpd_optimization
        state: "on"
    action:
      - service: athena_plant_monitor.optimize_vpd
```

### 📱 Dashboard Integration

#### Lovelace Card Beispiel
```yaml
type: entities
title: Athena Tag/Nacht Status
entities:
  - entity: sensor.athena_is_day_cycle
    name: Aktueller Zyklus
  - entity: sensor.athena_temperature_target
    name: Temperatur Ziel
  - entity: sensor.athena_humidity_target
    name: Luftfeuchtigkeit Ziel
  - entity: sensor.athena_vpd_target
    name: VPD Ziel
  - entity: sensor.athena_co2_target
    name: CO₂ Ziel
  - type: divider
  - entity: sensor.athena_temperature
    name: Ist-Temperatur
  - entity: sensor.athena_humidity
    name: Ist-Luftfeuchtigkeit
  - entity: sensor.athena_vpd_calculated
    name: Ist-VPD
  - entity: sensor.athena_co2
    name: Ist-CO₂
```

## 🧪 Testing

Der Test-Script `test_day_night.py` validiert:
- ✅ Korrekte Implementierung aller Tag/Nacht-Parameter
- ✅ Konsistente Unterschiede zwischen Tag- und Nachtzielen
- ✅ Funktionsfähigkeit der Zeit-basierten Fallback-Logik
- ✅ Korrekte Integration in alle Wachstumsphasen

## 🎯 Nutzen

### Für Grower
- **Präzisere Klimasteuerung**: Pflanzen erhalten nachts optimale Ruhebedingungen
- **Energieeffizienz**: Reduzierte Heiz-/Kühlkosten durch angepasste Nachttemperaturen
- **Bessere Erträge**: Tag/Nacht-Zyklen fördern natürliche Pflanzenprozesse

### Für Home Assistant Nutzer
- **Automatisierung**: Keine manuellen Einstellungsänderungen mehr nötig
- **Transparenz**: Klare Anzeige der aktuellen Ziele und Zyklen
- **Flexibilität**: Vollständig anpassbare Parameter für verschiedene Setups

Die Tag/Nacht-Unterscheidung macht das Athena Plant Monitor System zu einer vollständig professionellen Lösung für die präzise Pflanzensteuerung!
