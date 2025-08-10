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

**Zukünftige HACS UI-Konfiguration:**
Alle ESPHome-Entitäten werden über eine benutzerfreundliche HACS-Integration konfigurierbar sein (keine YAML-Bearbeitung erforderlich)

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

### MQTT Topic Structure (ESPHome Integration)
```
# ESPHome Auto-Discovery Topics
homeassistant/
├── sensor/
│   ├── esphome_node_1_temperature     # sensor.esphome_node_1_temperature
│   ├── esphome_node_1_humidity        # sensor.esphome_node_1_humidity
│   ├── esphome_node_1_pressure        # sensor.esphome_node_1_pressure
│   ├── esphome_node_1_vwc             # sensor.esphome_node_1_vwc
│   ├── esphome_node_1_ec_substrate    # sensor.esphome_node_1_ec_substrate
│   ├── esphome_node_1_ph_substrate    # sensor.esphome_node_1_ph_substrate
│   ├── esphome_node_1_temp_substrate  # sensor.esphome_node_1_temp_substrate
│   └── esphome_node_1_co2             # sensor.esphome_node_1_co2
├── switch/
│   ├── esphome_node_1_pump            # switch.esphome_node_1_pump
│   ├── esphome_node_1_fan_intake      # switch.esphome_node_1_fan_intake
│   ├── esphome_node_1_fan_exhaust     # switch.esphome_node_1_fan_exhaust
│   ├── esphome_node_1_humidifier      # switch.esphome_node_1_humidifier
│   └── esphome_node_1_dehumidifier    # switch.esphome_node_1_dehumidifier
└── light/
    └── esphome_node_1_led_panel       # light.esphome_node_1_led_panel
```

**Vereinfachtes System ohne Runoff-Messung:**
- Bewässerungssteuerung basiert auf VWC-Sensor und Zeitsteuerung
- Single-Zone Setup (eine Bewässerungszone)
- Alle Entitäten automatisch über ESPHome discovert

Alle Sensoren und Aktoren sind als **Home Assistant Entitäten** konfiguriert und ermöglichen:
- Vollständige Integration in das Home Assistant Ökosystem
- Automatisierungen basierend auf Sensorwerten
- Dashboards und Visualisierungen
- Historische Datenauswertung
- Mobile App Benachrichtigungen

**Zukünftige HACS UI-Konfiguration**: Alle ESPHome-Entitäten werden über eine benutzerfreundliche HACS-Integration konfigurierbar sein, sodass keine manuelle YAML-Bearbeitung erforderlich ist.

### Sensor-Entity Konfiguration (ESPHome)
```yaml
# ESPHome Gerät - Automatische Discovery
# Alle Sensoren werden automatisch in Home Assistant registriert

# Beispiel Template Sensoren für erweiterte Funktionen:
sensor:
  - platform: template
    sensors:
      vpd_calculated:
        friendly_name: "VPD Calculated"
        unit_of_measurement: "kPa"
        value_template: >
          {% set temp = states('sensor.esphome_node_1_temperature')|float %}
          {% set humidity = states('sensor.esphome_node_1_humidity')|float %}
          {% set svp = 0.6108 * (2.71828 ** (17.27 * temp / (temp + 237.3))) %}
          {{ ((svp * (100 - humidity)) / 100)|round(2) }}
          
      dryback_percent:
        friendly_name: "Dryback Percentage"
        unit_of_measurement: "%"
        value_template: >
          {% set current_vwc = states('sensor.esphome_node_1_vwc')|float %}
          {% set max_vwc = states('input_number.max_vwc_today')|float %}
          {% if max_vwc > 0 %}
            {{ (((max_vwc - current_vwc) / max_vwc) * 100)|round(1) }}
          {% else %}
            0
          {% endif %}

# Helper für Max VWC Tracking
input_number:
  max_vwc_today:
    name: "Max VWC Today"
    min: 0
    max: 100
    step: 0.1
    unit_of_measurement: "%"
    
  substrate_size:
    name: "Substrate Size"
    min: 1
    max: 20
    step: 0.5
    initial: 10
    unit_of_measurement: "L"

# Growth Phase Selection
input_select:
  growth_phase:
    name: "Growth Phase"
    options:
      - "vegetative"
      - "flowering_stretch"
      - "flowering_bulk" 
      - "flowering_finish"
    initial: "vegetative"
    
  crop_steering:
    name: "Crop Steering Strategy"
    options:
      - "vegetative"
      - "generative"
      - "balanced"
    initial: "vegetative"
```

### Zukünftige Entwicklung
Das langfristige Ziel ist die Entwicklung einer **HACS (Home Assistant Community Store) Integration**, um:
- Eine einfache Installation über HACS zu ermöglichen
- Vorkonfigurierte Entitäten und Dashboards bereitzustellen
- **Vollständige UI-basierte Konfiguration** aller ESPHome-Entitäten
- **Entity-Mapping Interface** für einfache Sensor/Aktor-Zuordnung
- **Drag-and-Drop Dashboard-Konfiguration** für Athena® Monitoring-Karten
- Automatische Updates und Wartung zu gewährleisten
- Die Community-Integration zu fördern
## Sensoren (ESPHome Integration)

### Umweltmonitoring

| Sensor | ESPHome Entity | Beschreibung | Athena® Zielwerte |
|--------|----------------|--------------|-------------------|
| BME280 | `sensor.esphome_node_1_temperature` | Lufttemperatur | Veg: 22-28°C, Flower: 18-28°C |
| BME280 | `sensor.esphome_node_1_humidity` | Luftfeuchtigkeit | Veg: 58-75%, Flower: 50-72% |
| BME280 | `sensor.esphome_node_1_pressure` | Luftdruck | Standardluftdruck |
| Template | `sensor.vpd_calculated` | VPD (berechnet) | Veg: 0.8-1.0 kPa, Flower: 1.0-1.4 kPa |
| SenseAir S8 | `sensor.esphome_node_1_co2` | CO₂ Konzentration | 400-1500 ppm |

### Substratmonitoring (vereinfacht ohne Runoff)

| Sensor | ESPHome Entity | Beschreibung | Athena® Zielwerte |
|--------|----------------|--------------|-------------------|
| Kapazitiv | `sensor.esphome_node_1_vwc` | Substratfeuchte VWC | 60-90% je nach Phase |
| EC-Sensor | `sensor.esphome_node_1_ec_substrate` | Substrat EC | Veg: 3-5, Flower: 3-10 |
| DS18B20 | `sensor.esphome_node_1_temp_substrate` | Substrattemperatur | 18-25°C |
| pH-Sensor | `sensor.esphome_node_1_ph_substrate` | Substrat pH | 5.8-6.2 (Coco/Rockwool) |
| Template | `sensor.dryback_percent` | Dryback % (berechnet) | Veg: 30-40%, Flower: 40-50% |

### Zusätzliche Sensoren

| Sensor | ESPHome Entity | Beschreibung |
|--------|----------------|--------------|
| Wassertank | `sensor.esphome_node_1_water_level` | Tank-Füllstand |
| Leak Sensor | `binary_sensor.esphome_node_1_leak_sensor` | Leckage-Erkennung |
|-----------|-----------|-----|--------------|
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

## Aktoren (ESPHome Integration)

| Aktor | ESPHome Entity | Beschreibung |
|-------|----------------|--------------|
| Wasserpumpe | `switch.esphome_node_1_pump` | Hauptbewässerungspumpe (Single Zone) |
| Abluftventilator | `switch.esphome_node_1_fan_exhaust` | Abluftventilator |
| Zuluftventilator | `switch.esphome_node_1_fan_intake` | Zuluftventilator |
| LED Panel | `light.esphome_node_1_led_panel` | Pflanzenlicht |
| Luftbefeuchter | `switch.esphome_node_1_humidifier` | Ultraschall Luftbefeuchter |
| Luftentfeuchter | `switch.esphome_node_1_dehumidifier` | Peltier Luftentfeuchter |
| CO₂ Ventil | `switch.esphome_node_1_co2_valve` | CO₂ Magnetventil |

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

### Fehlerdiagnose-Tabelle (ohne Runoff-Messung)
| Problem | Symptom | Ursache | Lösung |
|---------|---------|---------|---------|
| **Hohe Substrat-EC** | EC > 8.0 ppm | Zu seltene Bewässerung | Häufigere, kürzere Shots (vegetative Strategie) |
| **Niedrige Substrat-EC** | EC < 3.0 ppm | Zu häufige Bewässerung | Längere Pausen zwischen Shots (generative Strategie) |
| **VWC-Sensor schwankt** | +/- 5% Abweichung | Schlechte Kalibrierung | ESPHome Sensor rekalibrieren |
| **VWC steigt nicht** | Keine Reaktion bei Bewässerung | Sensor defekt oder Channel | Sensor-Position prüfen, ESPHome Logs checken |
| **Übermäßige VWC** | VWC > 95% konstant | Staunässe oder Sensor-Drift | Drainage prüfen, Sensor kalibrieren |
| **pH-Drift** | pH steigt/fällt kontinuierlich | Pufferverlust | Nährlösung pH-Puffer erhöhen |
| **ESPHome offline** | Sensor unavailable | WLAN-Probleme | ESPHome Gerät neu starten |

### Preventive Maintenance Schedule (ESPHome System)
```
Täglich:
├── VWC-Sensor Status Check (ESPHome Dashboard)
├── EC-Sensor Kalibrierung Check
├── Wassertank-Füllstand prüfen
└── WLAN-Verbindung ESPHome Node

Wöchentlich:
├── Sensor-Kalibrierung (EC & pH in ESPHome)
├── Pump Performance Test
├── ESPHome Logs Review
└── Home Assistant Entity Status

Monatlich:
├── Vollständige ESPHome Sensor-Neukalibrierung
├── Substrat EC-Profile Analysis
├── Historical Data Backup
└── ESPHome Firmware Update Check
```

## Erweiterte Automatisierungslogik (ESPHome angepasst)

### Adaptive Bewässerung für Single-Zone System
```yaml
- alias: "Adaptive Watering - Growth Based"
  trigger:
    platform: time_pattern
    minutes: "/30"  # Alle 30 Minuten prüfen
  condition:
    - condition: state
      entity_id: light.esphome_node_1_led_panel
      state: 'on'
    - condition: numeric_state
      entity_id: sensor.dryback_percent
      above: >
        {% if is_state('input_select.crop_steering', 'vegetative') %}
          15
        {% else %}
          20
        {% endif %}
  action:
    - service: switch.turn_on
      entity_id: switch.esphome_node_1_pump
    - delay: >
        {% set substrate_size = states('input_number.substrate_size')|float %}
        {% set steering = states('input_select.crop_steering') %}
        {% set base_time = 30 %}  # 30 seconds base
        {% if steering == 'vegetative' %}
          {% set multiplier = 1.5 %}
        {% elif steering == 'generative' %}
          {% set multiplier = 0.8 %}
        {% else %}
          {% set multiplier = 1.0 %}
        {% endif %}
        {{ "00:00:%02d"|format((base_time * multiplier * (substrate_size / 10))|int) }}
    - service: switch.turn_off
      entity_id: switch.esphome_node_1_pump
```

### Intelligente EC-Regulation ohne Runoff
```yaml
- alias: "Smart EC Management - No Runoff"
  trigger:
    platform: state
    entity_id: sensor.esphome_node_1_ec_substrate
  condition:
    - condition: template
      value_template: "{{ trigger.to_state.state != 'unavailable' }}"
  action:
    - choose:
        # EC zu hoch -> Frequent watering (flush effect)
        - conditions:
            - condition: numeric_state
              entity_id: sensor.esphome_node_1_ec_substrate
              above: 7.0
          sequence:
            - service: input_select.select_option
              target:
                entity_id: input_select.crop_steering
              data:
                option: "vegetative"  # Temporary vegetative for flushing
            - delay: '06:00:00'  # 6 hours of vegetative watering
            - service: input_select.select_option
              target:
                entity_id: input_select.crop_steering
              data:
                option: "{{ states('input_select.growth_phase') }}"  # Back to phase-appropriate steering
        
        # EC zu niedrig -> Reduce watering frequency
        - conditions:
            - condition: numeric_state
              entity_id: sensor.esphome_node_1_ec_substrate
              below: 3.0
          sequence:
            - service: input_select.select_option
              target:
                entity_id: input_select.crop_steering
              data:
                option: "generative"  # Temporary generative for concentration
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

### 🎯 Hauptziel: Vollständige UI-Konfiguration
**Alle ESPHome-Entitäten werden über eine benutzerfreundliche HACS-Integration konfigurierbar sein - keine manuelle YAML-Bearbeitung erforderlich!**

### Geplante Features für HACS Release
- **Custom Component**: `athena_plant_monitor`
- **UI-Konfiguration**: Alle Sensoren, Aktoren und Parameter über Web-Interface
- **Vorkonfigurierte Entitäten**: Alle Sensoren und Aktoren automatisch erkannt
- **Dashboard Templates**: Fertige Lovelace-Karten für Athena® Monitoring
- **Automatisierungs-Blueprints**: P0-P3 Phasen als wiederverwendbare Blueprints
- **Crop Steering Presets**: Vordefinierte Wachstumsphasen-Konfigurationen
- **Grafische Konfiguration**: Drag & Drop Interface für Sensorwerte und Schwellwerte

### Installation via HACS (Zukunft)
```yaml
# configuration.yaml - Minimale Konfiguration
athena_plant_monitor:
  # Alle weiteren Einstellungen über HACS UI konfigurierbar
  auto_discovery: true
```

**HACS UI Features:**
- Sensor-Mapping über Dropdown-Menüs
- Schwellwert-Einstellungen mit Schiebereglern
- Phase-Parameter mit Vorschau-Diagrammen
- Crop Steering Wizard mit Wachstumsphasen
- Echtzeit-Systemstatus und Diagnose

### Blueprint Beispiele (in Entwicklung)
- **Athena P0-P3 Complete Cycle**: Vollständiger Tagesablauf
- **VPD-Based Climate Control**: VPD-gesteuerte Klimaregelung  
- **EC Stacking Automation**: Automatisches EC-Management
- **Emergency Protocols**: Notfallprotokolle bei Sensorausfall

---

## 🎯 Zusammenfassung und Ausblick

### Aktueller Stand
Dieses Athena® Handbook basierte Bewässerungssystem ist vollständig auf **Home Assistant mit ESPHome** ausgelegt und implementiert alle vier Irrigationsphasen (P0-P3) sowie Crop Steering Strategien für eine Ein-Zonen-Anlage ohne Runoff-Messung.

### 🔮 Zukünftige HACS Integration
**Das Hauptziel ist die vollständige UI-Konfiguration**: Alle derzeit in YAML konfigurierten ESPHome-Entitäten werden über eine benutzerfreundliche HACS-Integration konfigurierbar sein. Nutzer werden in der Lage sein:

- **Sensoren zuweisen** über Dropdown-Menüs statt YAML-Bearbeitung
- **Schwellwerte einstellen** mit grafischen Schiebereglern
- **Irrigationsphasen konfigurieren** mit visuellen Diagrammen
- **Crop Steering** über einen Wizard mit Wachstumsphasen-Presets
- **Dashboard erstellen** mit Drag & Drop Lovelace-Karten

### Technische Vorteile
- ✅ **ESPHome Integration**: Alle Sensoren als native Home Assistant Entitäten
- ✅ **Einzel-Zonen Setup**: Optimiert für einfache Anlagen ohne Runoff
- ✅ **Athena® Kompatibilität**: Vollständige Umsetzung aller Irrigationsphasen
- ✅ **Erweiterbar**: Vorbereitet für zukünftige HACS UI-Features
- ✅ **Wartungsfreundlich**: Template-Sensoren für VPD und Dryback-Berechnung

**Für Entwickler**: Die aktuelle YAML-Konfiguration dient als Referenz-Implementation für die kommende HACS-Integration und kann bereits produktiv eingesetzt werden.


