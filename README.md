# Plant Monitoring System

Ein fortschrittliches System zur Überwachung und Steuerung von Cannabispflanzen basierend auf den Athena® Standards. Das System implementiert die bewährten Athena® Anbaumethoden und Präzisionsbewässerungsstrategien für optimale Ergebnisse.

## Athena® Standards Integration

Dieses System basiert auf den wissenschaftlich validierten Athena® Methoden:
- **Präzisionsbewässerung** mit P0, P1, P2, P3 Phasen
- **Crop Steering** für vegetative und generative Steuerung
- **VPD-gesteuerte Umweltkontrolle** (0.8-1.4 kPa je nach Wachstumsphase)
- **EC-Stacking** Strategien für Nährstoffmanagement
- **Dryback-Targets** für optimale Wurzelentwicklung

## Home Assistant Integration

### System-Architektur Diagramm
```
┌─────────────────────────────────────────────────────────┐
│                 HOME ASSISTANT CORE                     │
├─────────────────────┬───────────────────────────────────┤
│    MQTT BROKER      │         DASHBOARD UI              │
│   (Sensor Data)     │      (Lovelace Cards)             │
├─────────────────────┼───────────────────────────────────┤
│   AUTOMATIONS       │         DATABASE                  │
│ (Athena® Logic)     │    (InfluxDB/MariaDB)             │
└─────────────────────┴───────────────────────────────────┘
            │                           │
    ┌───────▼─────────┐         ┌───────▼─────────┐
    │   ESP32 Nodes   │         │  Actuator Hub   │
    │                 │         │                 │
    │ • VWC Sensors   │         │ • Water Pumps   │
    │ • EC Sensors    │         │ • Fans/Climate  │
    │ • pH Sensors    │         │ • LED Lights    │
    │ • Temp/Humidity │         │ • CO₂ Valves    │
    └─────────────────┘         └─────────────────┘
```

### MQTT Topic Structure (Athena® Standard)
```
athena/
├── environment/
│   ├── temp_air          # sensor.temp_001
│   ├── humidity_air      # sensor.humid_001
│   ├── vpd_calculated    # sensor.vpd_001
│   ├── co2_ppm          # sensor.co2_001
│   └── pressure_air     # sensor.pressure_001
├── substrate/
│   ├── vwc_percent      # sensor.vwc_001
│   ├── ec_substrate     # sensor.ec_sub_001
│   ├── ph_substrate     # sensor.ph_sub_001
│   ├── temp_substrate   # sensor.temp_sub_001
│   └── dryback_percent  # sensor.dryback_001
├── irrigation/
│   ├── flow_input       # sensor.flow_001
│   ├── flow_runoff      # sensor.flow_002
│   ├── ec_input         # sensor.ec_in_001
│   ├── ph_input         # sensor.ph_in_001
│   └── pump_status      # switch.pump_001
└── steering/
    ├── phase_current    # sensor.athena_phase
    ├── steering_mode    # input_select.crop_steering
    └── growth_phase     # input_select.growth_phase
```

Alle Sensoren und Aktoren sind als **Home Assistant Entitäten** konfiguriert und ermöglichen:
- Vollständige Integration in das Home Assistant Ökosystem
- Automatisierungen basierend auf Sensorwerten
- Dashboards und Visualisierungen
- Historische Datenauswertung
- Mobile App Benachrichtigungen

### Sensor-Entity Konfiguration
```yaml
# Beispiel: VWC Sensor Entity
sensor:
  - name: "Substrate Moisture VWC"
    unique_id: "athena_vwc_001"
    state_topic: "athena/substrate/vwc_percent"
    unit_of_measurement: "%"
    device_class: moisture
    state_class: measurement
    icon: mdi:water-percent
    
  - name: "Substrate EC"
    unique_id: "athena_ec_sub_001"  
    state_topic: "athena/substrate/ec_substrate"
    unit_of_measurement: "ppm"
    state_class: measurement
    icon: mdi:flash-outline
```

### Zukünftige Entwicklung
Das langfristige Ziel ist die Entwicklung einer **HACS (Home Assistant Community Store) Integration**, um:
- Eine einfache Installation über HACS zu ermöglichen
- Vorkonfigurierte Entitäten und Dashboards bereitzustellen
- Automatische Updates und Wartung zu gewährleisten
- Die Community-Integration zu fördern
## Sensoren

### Umweltmonitoring (Athena® Standards)

| Sensor ID | Kategorie | Typ | Beschreibung | Athena® Zielwerte |
|-----------|-----------|-----|--------------|-------------------|
| TEMP-001 | Temperatur | BME280| Lufttemperatur Innen | Veg: 22-28°C, Flower: 18-28°C |
| HUMID-001 | Feuchtigkeit | BME280 | Luftfeuchtigkeit Innen| Veg: 58-75%, Flower: 50-72% |
| PRESSURE-001 | Umwelt | BME280 | Luftdruck Innen| Standardluftdruck |
| VPD-001 | VPD | Calc | VPD Innen | Veg: 0.8-1.0 kPa, Flower: 1.0-1.4 kPa |
| TEMP-002 | Temperatur | DHT22| Lufttemperatur Außen | Referenzwert |
| HUMID-002 | Feuchtigkeit | DHT22 | Luftfeuchtigkeit Außen| Referenzwert |

### Substratmonitoring (Präzisionsbewässerung)

| Sensor ID | Kategorie | Typ | Beschreibung | Athena® Zielwerte |
|-----------|-----------|-----|--------------|-------------------|
| VWC-001 | Substratfeuchte | Kapazitiv | Volumetrischer Wassergehalt | Field Capacity bis Full Saturation |
| EC-SUB-001 | Elektrische Leitfähigkeit | EC-Sensor | Substrat EC (pwEC) | Veg: 3-5, Flower: 3-10 |
| TEMP-SUB-001 | Temperatur | DS18B20 | Substrattemperatur | 18-25°C |
| PH-SUB-001 | pH-Wert | pH-Sensor | Substrat pH | 5.8-6.2 (Coco/Rockwool) |

### Bewässerungssteuerung

| Sensor ID | Kategorie | Typ | Beschreibung | Funktionsweise |
|-----------|-----------|-----|--------------|-----------------|
| FLOW-001 | Durchfluss | Ultraschall | Input-Volumen Messung | Shot-Volumen Berechnung |
| FLOW-002 | Durchfluss | Ultraschall | Runoff-Volumen Messung | Runoff-Prozent Berechnung |
| EC-IN-001 | Elektrische Leitfähigkeit | EC-Sensor | Input EC Messung | Input EC Monitoring |
| PH-IN-001 | pH-Wert | pH-Sensor | Input pH Messung | Input pH Monitoring |

### Erweiterte Sensoren

| Sensor ID | Kategorie | Typ | Beschreibung |
|-----------|-----------|-----|--------------|
| LIGHT-001 | Licht | BH1750 | Umgebungslicht |
| UV-001 | Licht | VEML6070 | UV-Strahlung |
| TEMP-003 | Temperatur | CWT-Soil-THCPH-S | Bodentemperatur |
| PH-001 | pH-Wert | CWT-Soil-THCPH-S | Boden pH-Wert |
| EC-001 | EC-Wert | CWT-Soil-THCPH-S | Boden Ec-Wert |
| VWC-001 | Bodenfeuchtigkeit | CWT-Soil-THCPH-S | Bodenfeuchtigkeit |
| CO2-001 | Umwelt | SenseAir S8 | CO2-Konzentration |
| WATERTANK-001 | Füllstand |  | Drucksensor Tank Füllstand |
| LECKSENSE-001 | Auslauf Schutz | 2 pin contact | Leck-Schutz |
| LECKSENSE-002 | Auslauf Schutz | 2 pin contact | Leck-Schutz |
| DRYBACK-001 | Rücktrocknung | Calc| Soil Dryback |
| DRYBACKHOURLY-001 | Rücktrockung Stündlich | Calc| Soil Dryback Hourly|

## Aktoren

| Aktor ID | Kategorie | Typ | Beschreibung |
|----------|-----------|-----|--------------|
| PUMP-001 | Bewässerung | Wasserpumpe | Hauptbewässerungspumpe |
| VALVE-001 | Bewässerung | Magnetventil | Bewässerungsventil Zone 1 |
| VALVE-002 | Bewässerung | Magnetventil | Bewässerungsventil Zone 2 |
| FAN-001 | Belüftung | Lüfter | Abluftventilator |
| FAN-002 | Belüftung | Lüfter | Zuluftventilator |
| LED-001 | Beleuchtung | LED Panel | Pflanzenlicht |
| HUMIDIFIER-001 | Befeuchtung | Ultraschall | Luftbefeuchter |
| DEHUMIDIFIER-001 | Entfeuchtung | Peltier | Luftentfeuchter |
| CO2VALVE-001 | CO2 Ventil | Magnetventil | CO₂ Ventil |

## Athena® Bewässerungsphasen

Das System implementiert die vier Athena® Bewässerungsphasen für optimale Pflanzensteuerung:

### Visual Overview: 24-Stunden Bewässerungszyklus
```
VWC%  
100 ┤                                                                    
 95 ┤    ╭─────P2 MAINTENANCE─────╮                                     
 90 ┤   ╱                          ╲                                    
 85 ┤  ╱P1                          ╲                                   
 80 ┤ ╱ SAT                          ╲                                  
 75 ┤╱                               ╲                                 
 70 ┤                                 ╲                                
 65 ┤                                  ╲                               
 60 ┤                                   ╲                              
 55 ┤                                    ╲─P3 DRYBACK─                 
 50 ┤                                     ╲                            
 45 ┤                                      ╲                           
 40 ┤P0                                     ╲                          
    └┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬─── Zeit
     6h   8h   10h  12h  14h  16h  18h  20h  22h  0h   2h   4h   6h
     │    │                          │                          │
   LIGHTS │                      LIGHTS                     LIGHTS
    ON    │                       OFF                        ON
         P0→P1
```

### P0 - Vor-Bewässerungsphase (Additional Dryback)
- **Zeitraum**: 1-2 Stunden nach Lichtbeginn
- **Funktion**: "Transpiration vor Bewässerung" - Stomata öffnen sich
- **Dryback**: 1-5% zusätzlicher Dryback nach Lichtbeginn
- **Zweck**: Pflanzen aktivieren vor erster Bewässerung
- **Physiologie**: Wurzelaktivität anregen, osmotischen Druck aufbauen

### P1 - Sättigungsphase (Saturation)
- **Zeitraum**: Erste Bewässerungsphase bis Target VWC% erreicht
- **Shot-Größe**: 2-6% des Substratvolumens
- **Intervall**: 15-30 Minuten zwischen Shots
- **Ziel**: Substrate langsam bis zum Peak VWC% Target sättigen
- **Runoff**: 2-7% je nach Strategie (vegetativ vs. generativ)
- **Technik**: Vermeidung von Channeling durch stufenweise Sättigung

### P2 - Erhaltungsphase (Maintenance)
- **Zeitraum**: Während der gesamten Lichtzeit
- **Funktion**: Peak VWC% Target halten
- **Steuerung**: Dryback und Substrat-EC Kontrolle
- **Variabilität**: Shot-Größe anpassen für EC-Stacking
- **Frequenz**: Basierend auf Transpirationskurve und VPD

### P3 - Dryback-Phase (Overnight Dryback)
- **Zeitraum**: Licht aus bis nächster P1
- **Vegetativer Dryback**: 30-40% (weniger Stress, Bud Swell)
- **Generativer Dryback**: 40-50% (mehr Stress, kompakte Pflanzen)
- **Messung**: Relative Änderung des VWC%
- **Wichtigkeit**: Wurzelatmung, Nährstoffaufnahme-Optimierung

### Dryback-Kurven Visualisierung
```
Vegetative Steering (30-40% Dryback):
VWC%
100 ┤ ╭─────────────────╮
 90 ┤╱                   ╲
 80 ┤                     ╲
 70 ┤                      ╲
 60 ┤                       ╲─────── Sanfter Dryback
    └┬───────────────────────┬───── für Wachstum
     18h                     6h

Generative Steering (40-50% Dryback):
VWC%
100 ┤ ╭─────────────────╮
 90 ┤╱                   ╲
 80 ┤                     ╲
 70 ┤                      ╲
 60 ┤                       ╲
 50 ┤                        ╲──── Stärkerer Dryback
    └┬───────────────────────┬──── für Blüte/Kompaktheit
     18h                     6h
```


## System Monitoring & Troubleshooting

### Sensor-Status Dashboard
```
┌─ SYSTEM HEALTH ──────────────────────────────────────┐
│ ✅ VWC Sensor      │ 78.5%  │ Normal   │ 2min ago   │
│ ✅ EC Substrate    │ 4.2ppm │ Normal   │ 2min ago   │  
│ ⚠️  pH Substrate    │ 5.2    │ Low      │ 5min ago   │
│ ❌ Temp Substrate  │ --     │ Offline  │ 15min ago  │
│ ✅ VPD Calculated  │ 1.1kPa │ Normal   │ 1min ago   │
└──────────────────────────────────────────────────────┘

┌─ IRRIGATION STATUS ──────────────────────────────────┐
│ Current Phase: P2 - Maintenance                      │
│ Last Shot: 14:23 (45min ago) - 3.2% Shot            │
│ Daily Water: 2.4L / 3.1L Target                     │
│ Runoff Today: 12.3% (Target: 8-16%)                 │
│ Next Irrigation: Auto (VWC < 75%)                   │
└──────────────────────────────────────────────────────┘
```

### Alert-System Konfiguration
```yaml
# Kritische Alerts
- alias: "CRITICAL: VWC Sensor Offline"
  trigger:
    platform: state
    entity_id: sensor.vwc_001
    to: 'unavailable'
    for: '00:05:00'
  action:
    - service: notify.mobile_app
      data:
        title: "🚨 KRITISCH: VWC Sensor Offline"
        message: "Substratfeuchte-Sensor antwortet nicht. Wechsel zu Zeit-basierter Bewässerung."
        data:
          priority: "high"
          
- alias: "WARNING: Substrat zu trocken"
  trigger:
    platform: numeric_state
    entity_id: sensor.vwc_001
    below: 50
    for: '00:10:00'
  action:
    - service: switch.turn_on
      entity_id: switch.pump_001
      data:
        duration: 60  # Notfall-Bewässerung
    - service: notify.mobile_app
      data:
        title: "⚠️ WARNUNG: Substrat zu trocken"
        message: "VWC unter 50%. Notfall-Bewässerung aktiviert."
```

### Fehlerdiagnose-Tabelle
| Problem | Symptom | Ursache | Lösung |
|---------|---------|---------|---------|
| **Hohe Substrat-EC** | EC > 8.0 ppm | Zu wenig Runoff | Vegetative Shots (6% Volume) |
| **Niedrige Substrat-EC** | EC < 3.0 ppm | Zu viel Runoff | Generative Shots (2% Volume) |
| **VWC-Sensor schwankt** | +/- 5% Abweichung | Schlechte Kalibrierung | Rekalibrierung in nasser + trockener Erde |
| **Kein Runoff** | 0% Runoff bei Bewässerung | Zu kleine Shots oder zu trocken | Shot-Größe erhöhen auf 4-6% |
| **Übermäßiger Runoff** | >20% Runoff | Channeling oder Übersättigung | Kleinere, häufigere Shots |
| **pH-Drift** | pH steigt/fällt kontinuierlich | Pufferverlust oder Mikrobielle Aktivität | pH-Pufferung prüfen, Substrat erneuern |

### Preventive Maintenance Schedule
```
Täglich:
├── VWC-Kalibrierung Check
├── EC-Sensor Reinigung
├── pH-Sensor Wartung
└── Runoff-Messung Validation

Wöchentlich:
├── Sensor-Kalibrierung (EC & pH)
├── Durchfluss-Sensoren Check
├── Pump Performance Test
└── MQTT Connection Status

Monatlich:
├── Vollständige Sensor-Neukalibrierung
├── Substrat EC-Profile Audit
├── Historical Data Analysis
└── Backup Configuration Export
```

## Erweiterte Automatisierungslogik

### Adaptive Bewässerung basierend auf Pflanzenentwicklung
```yaml
# Dynamische Shot-Größe basierend auf Wachstum
- alias: "Adaptive Shot Size - Vegetative Growth"
  trigger:
    platform: time_pattern
    minutes: "/30"  # Alle 30 Minuten prüfen
  condition:
    - condition: state
      entity_id: input_select.growth_phase
      state: 'vegetative'
    - condition: numeric_state
      entity_id: sensor.dryback_001
      above: 15  # Bei 15% Dryback
  action:
    - service: switch.turn_on
      entity_id: switch.pump_001
      data:
        duration: >
          {% set substrate_size = states('sensor.substrate_size')|int %}
          {% set growth_week = states('sensor.growth_week')|int %}
          {% set base_shot = substrate_size * 0.03 %}  # 3% base
          {% set growth_multiplier = 1 + (growth_week * 0.1) %}  # +10% pro Woche
          {{ (base_shot * growth_multiplier)|round }}
```

### Intelligente EC-Stacking Automatisierung
```yaml
- alias: "Smart EC Stacking - Generative Phase"
  trigger:
    platform: state
    entity_id: sensor.runoff_ec_001
  condition:
    - condition: state
      entity_id: input_select.crop_steering
      state: 'generative'
  action:
    - choose:
        # Runoff-EC zu niedrig -> Shots reduzieren
        - conditions:
            condition: numeric_state
            entity_id: sensor.runoff_ec_001
            below: 6.0
          sequence:
            - service: input_number.set_value
              target:
                entity_id: input_number.shot_size_percent
              data:
                value: >
                  {{ max(1.5, states('input_number.shot_size_percent')|float - 0.5) }}
        
        # Runoff-EC zu hoch -> Shots erhöhen  
        - conditions:
            condition: numeric_state
            entity_id: sensor.runoff_ec_001
            above: 10.0
          sequence:
            - service: input_number.set_value
              target:
                entity_id: input_number.shot_size_percent
              data:
                value: >
                  {{ min(6.0, states('input_number.shot_size_percent')|float + 0.5) }}
```

### Precision Timing für P0-P3 Phasen
```yaml
# P0 Phase - Additional Dryback Calculator
- alias: "P0 Phase - Smart Dryback Timing"
  trigger:
    platform: state
    entity_id: light.led_001
    to: 'on'
  action:
    - service: input_datetime.set_datetime
      target:
        entity_id: input_datetime.p0_end_time
      data:
        datetime: >
          {% set current_vwc = states('sensor.vwc_001')|float %}
          {% set target_dryback = 3.0 %}  # 3% additional dryback
          {% set dryback_rate = 2.5 %}    # 2.5% per hour average
          {% set delay_hours = target_dryback / dryback_rate %}
          {{ (now() + timedelta(hours=delay_hours)).strftime('%Y-%m-%d %H:%M:%S') }}

# P1 Phase - Saturation with VPD Adjustment
- alias: "P1 Phase - VPD-Adjusted Saturation"
  trigger:
    platform: time
    at: input_datetime.p0_end_time
  action:
    - service: script.p1_saturation_sequence
      data:
        shot_count: >
          {% set vpd = states('sensor.vpd_001')|float %}
          {% if vpd > 1.2 %}
            4  # Hohe VPD = mehr Shots
          {% elif vpd < 0.8 %}
            2  # Niedrige VPD = weniger Shots
          {% else %}
            3  # Normale VPD = standard Shots
          {% endif %}
```

## Messwerte
Alle Sensoren und Aktoren werden über **Home Assistant** verwaltet und bieten:
- Echtzeit-Monitoring über Home Assistant Dashboards
- Historische Datenanalyse mit der integrierten Datenbank
- Benachrichtigungen bei kritischen Werten über die Mobile App
- Automatische Bewässerung und Klimasteuerung durch Automatisierungen

## Integration Details
- **Plattform**: Home Assistant
- **Protokoll**: MQTT/Zigbee/WiFi (je nach Sensor/Aktor)
- **Entitäten**: Jeder Sensor und Aktor ist eine eigene Home Assistant Entität
- **Updates**: Kontinuierliche Datenübertragung alle 30 Sekunden

## HACS Integration Roadmap

### Geplante Features für HACS Release
- **Custom Component**: `athena_plant_monitor`
- **Vorkonfigurierte Entitäten**: Alle Sensoren und Aktoren automatisch erkannt
- **Dashboard Templates**: Fertige Lovelace-Karten für Athena® Monitoring
- **Automatisierungs-Blueprints**: P0-P3 Phasen als wiederverwendbare Blueprints
- **Crop Steering Presets**: Vordefinierte Wachstumsphasen-Konfigurationen

### Installation via HACS (Zukunft)
```yaml
# configuration.yaml
athena_plant_monitor:
  mqtt_prefix: "athena"
  substrate_size: 10  # Liter
  growth_phase: "vegetative"
  irrigation_strategy: "precision"
  crop_steering: "vegetative"
```

### Blueprint Beispiele (in Entwicklung)
- **Athena P0-P3 Complete Cycle**: Vollständiger Tagesablauf
- **VPD-Based Climate Control**: VPD-gesteuerte Klimaregelung  
- **EC Stacking Automation**: Automatisches EC-Management
- **Emergency Protocols**: Notfallprotokolle bei Sensorausfall

## Hinweise
- Alle Entitäten sind in Home Assistant konfiguriert
- Sensoren werden alle 30 Sekunden ausgelesen
- Kalibrierung erfolgt monatlich über Home Assistant Automatisierungen
- Bei Sensorausfall wird automatisch eine Benachrichtigung über die Home Assistant App gesendet
- HACS Integration in Entwicklung für vereinfachte Installation und Updates

---
*Letzte Aktualisierung: August 2025*

## Crop Steering Strategien

### Crop Steering Konzept-Diagramm
```
                    VWC% Peak Target
                         ↓
Vegetative ──────────────●─────────── Field Capacity +
(Wachstum)               │            (Mehr Runoff)
                         │
                         │            
Field Capacity ──────────●─────────── Optimaler Bereich
                         │
                         │
Generative ──────────────●─────────── Field Capacity -
(Blüte)                  │            (Weniger Runoff)
                         ↑
                    Stress-Level
```

### Vegetative Steuerung (Längenwachstum fördern)
**Prinzip**: Weniger Stress = Mehr Wachstum
- **Größere Shots**: Mehr Runoff → niedrigere Substrat-EC
- **Kleinerer Dryback**: 30-40%
- **Peak VWC%**: Über Field Capacity
- **Anwendung**: Veg, Flower Bulk (Wochen 5-7)
- **Physiologie**: Optimale Wasserversorgung für Zellteilung

```
Vegetative Steering Kurve:
EC ppm
2500 ┤                             
2000 ┤ ╭─Runoff EC (gespült)       
1500 ┤╱                           
1000 ┤    Substrat EC ───────────── Niedrig für Wachstum
 500 ┤                            
     └┬────┬────┬────┬────┬────── Zeit
      8h   12h  16h  20h  24h
```

### Generative Steuerung (Blütenbildung fördern)
**Prinzip**: Mehr Stress = Mehr Blüte
- **Kleinere Shots**: Weniger Runoff → höhere Substrat-EC  
- **Größerer Dryback**: 40-50%
- **Peak VWC%**: Bei oder unter Field Capacity
- **Anwendung**: Flower Stretch (Wochen 1-4), Finish (Wochen 8-9)
- **Physiologie**: Kontrollierten Stress für reproduktive Entwicklung

```
Generative Steering Kurve:
EC ppm
3000 ┤                 ╭─Substrat EC (konzentriert)
2500 ┤               ╱             
2000 ┤             ╱               
1500 ┤───────────╱─Runoff EC       
1000 ┤                             
     └┬────┬────┬────┬────┬────── Zeit
      8h   12h  16h  20h  24h
```

### EC-Stacking Strategie Diagramm
```
Input EC: 3.0 (konstant)

Vegetativ (Mehr Runoff = EC Spülung):
├── Input EC: 3.0
├── Substrat EC: 3.5-5.0 ◄── Gespült durch hohen Runoff
└── Runoff EC: 4.0-5.0

Generativ (Weniger Runoff = EC Stacking):
├── Input EC: 3.0
├── Substrat EC: 6.0-10.0 ◄── Konzentriert durch wenig Runoff
└── Runoff EC: 7.0-11.0
```

### Kombinierte Strategien nach Wachstumsphase
```
Woche 1-4 (Veg):     [████████] Vegetativ (100%)
Woche 5-8 (Stretch): [██████░░] Generativ (75%)
Woche 9-12 (Bulk):   [████░░░░] Vegetativ (50%) 
Woche 13-16 (Finish):[██░░░░░░] Generativ (25%)

Legend: █ = Dominante Strategie, ░ = Sekundäre Strategie
```

## Substrat-Spezifikationen

### Empfohlene Substratgrößen (nach Veg-Zeit)
- **7-14 Tage Veg**: 4 Liter Töpfe
- **14-21 Tage Veg**: 7 Liter Töpfe  
- **18-28 Tage Veg**: 10 Liter Töpfe

### Shot-Volumen Referenz
| Substratgröße | 1% Shot-Volumen |
|---------------|-----------------|
| 4 Liter Topf | 40 mL |
| 7 Liter Topf | 70 mL |
| 10 Liter Topf | 100 mL |
| 15 cm Rockwool (Hugo) | 35 mL |

## VPD-Targets nach Wachstumsphase

### VPD-Kurve über Tagesverlauf
```
VPD kPa
1.6 ┤                    ╭─Finish (1.2-1.4)       
1.4 ┤                  ╱│                         
1.2 ┤               ╱───╯│ ╲─Bulk/Stretch (1.0-1.2)
1.0 ┤            ╱─      │   ╲                    
0.8 ┤         ╱──        │    ╲───╮               
0.6 ┤──────╱─Veg (0.8-1.0)        ╲──────────    
    └┬────┬────┬────┬────┬────┬────┬────┬────┬── Zeit
     6h   9h   12h  15h  18h  21h  0h   3h   6h
     │                   │                   │
   Lights              Lights              Lights
    ON                  OFF                 ON
```

### VPD-Berechnung und Automation
```
VPD = (SVP × (100 - RH)) / 100

Wo:
SVP = 0.6108 × e^(17.27×T/(T+237.3))  [Sättigungsdampfdruck]
T = Temperatur in °C
RH = Relative Luftfeuchtigkeit in %
```

| Wachstumsphase | Temperatur | Luftfeuchtigkeit | VPD Target | Transpiration |
|----------------|------------|------------------|------------|---------------|
| Veg | 22.2-27.7°C | 58-75% | 0.8-1.0 kPa | Moderat |
| Flower Stretch | 25.5-27.7°C | 60-72% | 1.0-1.2 kPa | Erhöht |
| Flower Bulk | 23.8-26.6°C | 60-70% | 1.0-1.2 kPa | Erhöht |
| Flower Finish | 18.3-22.2°C | 50-60% | 1.2-1.4 kPa | Maximal |

### VPD-basierte Bewässerungsanpassung
```
Hohe VPD (>1.2 kPa): ╭─ Mehr Transpiration
                     ├─ Häufigere kleine Shots
                     ├─ Kürzere Dryback-Zeiten
                     └─ Erhöhte Substratfeuchte

Niedrige VPD (<0.8 kPa): ╭─ Weniger Transpiration
                         ├─ Weniger häufige Shots
                         ├─ Längere Dryback-Zeiten
                         └─ Reduzierte Substratfeuchte
```

## Nährstoff-Targets (Athena® Pro Line)

### EC-Werte nach Wachstumsphase
| Phase | Input EC | Substrat EC | Runoff EC |
|-------|----------|-------------|-----------|
| Veg (W1-4) | 3.0 | 3-5 | 4.0-5.0 |
| Flower Stretch (W1-4) | 3.0 | 4-10 | 6.0-7.0 |
| Flower Bulk (W5-7) | 3.0 | 3.5-6 | 5.0-6.0 |
| Flower Finish (W8-9) | 3.0 | 3-4 | 3.0-3.5 |

### pH-Werte
- **Input pH**: 5.8-6.2 (Coco/Rockwool), 6.0-6.4 (Torf-basiert)
- **Runoff pH**: Sollte höher als Input sein (gesunde Pflanzen)

## Automatisierte Bewässerung & Crop Steering nach Athena® Standards

### Precision Irrigation Strategy (P0, P1, P2, P3 Phasen)

Das System implementiert die **Athena® Precision Irrigation Strategy** mit vier definierten Bewässerungsphasen:

#### P0 Phase - Additional Dryback (1-2 Stunden nach Licht an)
- **Beschreibung**: Bewusster Wasserentzug nach dem Einschalten der Beleuchtung
- **Dauer**: 30 Minuten - 2 Stunden nach Lights-On
- **Ziel**: "Transpiration vor Bewässerung" - Stoma öffnen sich vor Wasserzufuhr
- **VWC-Verlust**: 1-5% zusätzlicher Dryback
- **Automatisierung**: Verzögerung der ersten Bewässerung um 1-2h nach Lichtstart

#### P1 Phase - Saturationsphase (Erste Bewässerungen nach Lights-On)
- **Beschreibung**: Stufenweise Sättigung des Substrats auf Ziel-VWC
- **Methode**: 2-6% Shots alle 15-30 Minuten
- **Ziel**: Langsame Substratsättigung ohne Channeling
- **Runoff**: 2-7% je nach Crop Steering Strategie
- **Ende**: Wenn Peak VWC% Target erreicht ist
- **Automatisierung**: Mehrere kleine Bewässerungszyklen mit Pausen

#### P2 Phase - Erhaltungsphase (Tageslicht-Periode)
- **Beschreibung**: Aufrechterhaltung der optimalen VWC während der Lichtperiode
- **Funktion**: Feinabstimmung der Substrat-EC und Dryback-Kontrolle
- **Shot-Größe**: Variable je nach Strategie (Vegetativ vs. Generativ)
- **Intervalle**: Basierend auf Dryback-Rate und VPD
- **Runoff-Kontrolle**: 
  - Vegetativ: 8-16% Runoff (niedrigere Substrat-EC)
  - Generativ: 1-7% Runoff (höhere Substrat-EC)

#### P3 Phase - Dryback-Phase (Lights-Off bis nächster Tag)
- **Beschreibung**: Kontrollierte Rücktrocknung über Nacht
- **Dryback-Ziele**:
  - **Vegetativ**: 30-40% Dryback (weniger Stress)
  - **Generativ**: 40-50% Dryback (mehr Stress)
- **Funktion**: Wurzelatmung ermöglichen, Fäulnis verhindern
- **Monitoring**: Kontinuierliche VWC-Überwachung bis zum nächsten P0

### Wachstumsphasen mit Athena® Standards

#### Vegetative Phase (Veg)
- **Umwelt-Ziele**:
  - Temperatur: 22.2° - 27.7°C
  - Luftfeuchtigkeit: 58-75%
  - VPD: 0.8 - 1.0 kPa
  - PPFD: 300-600 μmol/m²/s
- **Bewässerung**:
  - Substrat-EC: 3.0-5.0
  - Dryback: 30-40%
  - Strategie: Vegetativ (mehr Runoff, niedrigere EC)
  - pH: 5.8-6.2 (Coco/Rockwool), 6.0-6.4 (Torf)

#### Blüte Stretch (Woche 1-4)
- **Umwelt-Ziele**:
  - Temperatur: 25.5° - 27.7°C
  - Luftfeuchtigkeit: 60-72%
  - VPD: 1.0 - 1.2 kPa
  - PPFD: 600-1000 μmol/m²/s
- **Bewässerung**:
  - Substrat-EC: 4.0-10.0
  - Dryback: 40-50%
  - Strategie: Generativ (weniger Runoff, höhere EC)
  - CO₂: 1200-1500 ppm

#### Blüte Bulk (Woche 5-7)
- **Umwelt-Ziele**:
  - Temperatur: 23.8° - 26.6°C
  - Luftfeuchtigkeit: 60-70%
  - VPD: 1.0 - 1.2 kPa
  - PPFD: 850-1200 μmol/m²/s
- **Bewässerung**:
  - Substrat-EC: 3.5-6.0
  - Dryback: 30-40%
  - Strategie: Vegetativ (Bud Swell fördern)
  - CO₂: 1200-1500 ppm

#### Blüte Finish (Woche 8-10)
- **Umwelt-Ziele**:
  - Temperatur: 18.3° - 22.2°C
  - Luftfeuchtigkeit: 50-60%
  - VPD: 1.2 - 1.4 kPa
  - PPFD: 600-900 μmol/m²/s
- **Bewässerung**:
  - Substrat-EC: 3.0-4.0
  - Dryback: 40-50%
  - Strategie: Gemischt (EC reduzieren + Generativ)
  - CO₂: 500-800 ppm

### Crop Steering Strategien

#### Vegetative Steering (Wachstum fördern)
**Ziel**: Größere Schüsse, mehr Runoff, niedrigere Substrat-EC, kleinere Drybacks
```
Wenn Peak VWC% > Field Capacity:
  → Mehr Runoff erzeugen
  → Substrat-EC senken
  → Shot-Größe erhöhen

Wenn Dryback < 30%:
  → Zusätzliche P2-Events entfernen
  → Dryback erhöhen
```

#### Generative Steering (Blüte fördern)
**Ziel**: Kleinere Schüsse, weniger Runoff, höhere Substrat-EC, größere Drybacks
```
Wenn Peak VWC% = Field Capacity:
  → Runoff reduzieren (EC Stacking)
  → Substrat-EC erhöhen
  → Shot-Größe verringern

Wenn Dryback > 50%:
  → P2-Events hinzufügen
  → Dryback reduzieren
```

### Shot-Volumen Tabelle (Athena® Standards)

| Substrat-Größe | 1% Shot-Volumen | Vegetativ Runoff | Generativ Runoff |
|----------------|-----------------|------------------|------------------|
| 4L Topf | 40 mL | 303-606 mL (8-16%) | 37-265 mL (1-7%) |
| 7L Topf | 70 mL | 606-1211 mL (8-16%) | 76-530 mL (1-7%) |
| 10L Topf | 100 mL | 908-1817 mL (8-16%) | 116-795 mL (1-7%) |
| 10cm Rockwool | 10 mL | 80-160 mL (8-16%) | 10-70 mL (1-7%) |
| 15cm Rockwool | 35 mL | 280-560 mL (8-16%) | 35-245 mL (1-7%) |

### Automatisierungslogik

#### Täglicher Bewässerungszyklus
```
06:00 - Lights ON
06:30-08:30 - P0 Phase (Additional Dryback)
08:30-10:00 - P1 Phase (Saturation)
10:00-18:00 - P2 Phase (Maintenance)
18:00-06:00 - P3 Phase (Dryback)
```

#### Sensor-Integration
- **VWC-Sensoren**: Kontinuierliche Substratfeuchte-Messung
- **EC-Sensoren**: Substrat-EC Monitoring für Precision Steering
- **Runoff-Sammlung**: Automatische EC/pH-Messung des Abflusses
- **VPD-Berechnung**: Umwelt-basierte Bewässerungsanpassung

#### Notfall-Protokolle (Athena® konform)
- **Runoff-EC zu hoch**: Vegetative Shots (mehr Runoff)
- **Runoff-EC zu niedrig**: Generative Shots (weniger Runoff)
- **VWC-Sensor Ausfall**: Fallback auf Zeit-basierte Bewässerung
- **Überwässerung**: Sofortiger Stopp + verlängerte P3-Phase

## Home Assistant Automatisierungs-Beispiele

### P0 Phase Automation (Additional Dryback)
```yaml
- alias: "Athena P0 - Additional Dryback nach Lights On"
  trigger:
    - platform: state
      entity_id: light.led_001
      to: 'on'
  action:
    - delay: '01:00:00'  # 1 Stunde warten
    - condition: numeric_state
      entity_id: sensor.vwc_001
      below: 85  # Nur wenn VWC unter 85%
    - service: switch.turn_off
      entity_id: switch.pump_001  # Bewässerung blockieren
```

### P1 Phase Automation (Saturation)
```yaml
- alias: "Athena P1 - Saturation Phase"
  trigger:
    - platform: time
      at: '08:30:00'
  condition:
    - condition: state
      entity_id: light.led_001
      state: 'on'
  action:
    - repeat:
        count: 4  # Bis zu 4 Shots
        sequence:
          - service: switch.turn_on
            entity_id: switch.pump_001
            data:
              duration: 30  # 30 Sekunden = ~2% Shot
          - delay: '00:15:00'  # 15 Minuten Pause
          - condition: numeric_state
            entity_id: sensor.vwc_001
            above: 90  # Stopp bei 90% VWC
```

### VPD-basierte Bewässerungssteuerung
```yaml
- alias: "VPD-gesteuerte P2 Bewässerung"
  trigger:
    - platform: numeric_state
      entity_id: sensor.dryback_001
      above: 15  # Bei 15% Dryback
  condition:
    - condition: state
      entity_id: light.led_001
      state: 'on'
    - condition: numeric_state
      entity_id: sensor.vpd_001
      above: 1.0  # Nur bei VPD > 1.0 kPa
  action:
    - service: switch.turn_on
      entity_id: switch.pump_001
      data:
        duration: "{{ (states('sensor.substrate_size')|int * 0.03)|round }}"  # 3% Shot
```

### Crop Steering Automation
```yaml
- alias: "Vegetative Steering - Hoher Runoff"
  trigger:
    - platform: numeric_state
      entity_id: sensor.ec_sub_001
      above: 6.0  # Substrat-EC zu hoch
  condition:
    - condition: state
      entity_id: input_select.growth_phase
      state: 'vegetative'
  action:
    - service: switch.turn_on
      entity_id: switch.pump_001
      data:
        duration: "{{ (states('sensor.substrate_size')|int * 0.06)|round }}"  # 6% Shot für mehr Runoff

- alias: "Generative Steering - Niedriger Runoff"
  trigger:
    - platform: numeric_state
      entity_id: sensor.ec_sub_001
      below: 4.0  # Substrat-EC zu niedrig
  condition:
    - condition: state
      entity_id: input_select.growth_phase
      state: 'flowering'
  action:
    - service: switch.turn_on
      entity_id: switch.pump_001
      data:
        duration: "{{ (states('sensor.substrate_size')|int * 0.02)|round }}"  # 2% Shot für weniger Runoff
```


