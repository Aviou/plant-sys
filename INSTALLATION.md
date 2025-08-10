# Athena Plant Monitor Installation Guide

## Schnellstart

### 1. Voraussetzungen prüfen
- ✅ Home Assistant 2023.1+ installiert
- ✅ HACS (Home Assistant Community Store) installiert  
- ✅ ESPHome-Gerät mit Pflanzensensoren verfügbar

### 2. Installation über HACS

#### Option A: Über HACS Repository (empfohlen)
1. HACS öffnen: **Einstellungen** → **HACS**
2. **Integrationen** auswählen
3. **Benutzerdefinierte Repositories** (⋮ Menü oben rechts)
4. Repository hinzufügen:
   - URL: `https://github.com/avi23/athena-plant-monitor`
   - Kategorie: **Integration**
   - **Hinzufügen** klicken
5. **Athena Plant Monitor** in der Liste finden
6. **Herunterladen** klicken
7. Home Assistant **neu starten**

#### Option B: Manuelle Installation
1. Repository als ZIP herunterladen
2. Entpacken und `custom_components/athena_plant_monitor/` kopieren nach:
   ```
   homeassistant/
   └── custom_components/
       └── athena_plant_monitor/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           └── ...
   ```
3. Home Assistant neu starten

### 3. ESPHome Gerät vorbereiten

#### Minimum-Konfiguration für ESPHome:
```yaml
# esphome/athena-node-1.yaml
esphome:
  name: athena-node-1
  platform: ESP32
  board: esp32dev

wifi:
  ssid: "IhrWiFi"
  password: "IhrPasswort"

api:
  encryption:
    key: "your-api-key"

ota:
  password: "your-ota-password"

logger:

# MINIMUM ERFORDERLICH für Athena Integration:
sensor:
  # VWC Sensor (erforderlich)
  - platform: adc
    pin: A0
    name: "VWC"
    id: vwc_sensor
    update_interval: 30s
    unit_of_measurement: "%"
    accuracy_decimals: 1
    filters:
      - calibrate_linear:
          - 0.0 -> 0.0
          - 1.0 -> 100.0

switch:
  # Pumpe (erforderlich)  
  - platform: gpio
    pin: GPIO2
    name: "Pump"
    id: pump_switch
```

#### Vollständige ESPHome-Konfiguration:
```yaml
# Erweiterte Konfiguration mit allen Sensoren
sensor:
  # Umweltsensoren
  - platform: bme280
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    pressure:
      name: "Pressure"
    address: 0x76
    update_interval: 60s

  # VWC Sensor
  - platform: adc
    pin: A0
    name: "VWC"
    update_interval: 30s
    unit_of_measurement: "%"
    accuracy_decimals: 1

  # EC Sensor
  - platform: adc
    pin: A1
    name: "EC Substrate"
    update_interval: 30s
    unit_of_measurement: "ppm"
    accuracy_decimals: 1
    
  # pH Sensor
  - platform: adc
    pin: A2
    name: "pH Substrate"
    update_interval: 30s
    accuracy_decimals: 1
    
  # Substrattemperatur
  - platform: dallas
    address: 0x123456789ABCDEF0
    name: "Temp Substrate"
    
  # CO2 Sensor
  - platform: senseair
    co2:
      name: "CO2"
      
binary_sensor:
  # Leckage-Sensor
  - platform: gpio
    pin: GPIO4
    name: "Leak Sensor"
    device_class: moisture

switch:
  # Bewässerung
  - platform: gpio
    pin: GPIO2
    name: "Pump"
    
  # Ventilatoren
  - platform: gpio
    pin: GPIO5
    name: "Fan Intake"
  - platform: gpio
    pin: GPIO18
    name: "Fan Exhaust"
    
  # Be-/Entfeuchter
  - platform: gpio
    pin: GPIO19
    name: "Humidifier"
  - platform: gpio
    pin: GPIO21
    name: "Dehumidifier"
    
  # CO2 Ventil
  - platform: gpio
    pin: GPIO22
    name: "CO2 Valve"

light:
  # LED Panel
  - platform: neopixelbus
    type: GRB
    variant: WS2812
    pin: GPIO23
    num_leds: 30
    name: "LED Panel"
```

### 4. Integration einrichten

1. **Einstellungen** → **Geräte & Services**
2. **Integration hinzufügen** → "Athena Plant Monitor" suchen
3. **ESPHome-Gerät auswählen** aus der automatisch erkannten Liste
4. **Grundkonfiguration** vornehmen:
   - Update-Intervall: 30 Sekunden (empfohlen)
   - Wachstumsphase: "Vegetativ" (für neue Pflanzen)
   - Crop Steering: "Vegetativ" (Standard)
   - Substratgröße: Ihr tatsächliches Substratvolumen in Litern

5. **Erweiterte Einstellungen** (optional):
   - Manuelle Zielwerte überschreiben
   - Spezielle VPD-/EC-/pH-Targets setzen

### 5. Erste Schritte nach Installation

#### Entitäten prüfen:
Nach erfolgreicher Installation finden Sie diese Entitäten:

**Sensoren:**
- `sensor.athena_vwc` - Aktuelle Substratfeuchte
- `sensor.athena_ec_substrate` - EC-Wert des Substrats  
- `sensor.athena_vpd_calculated` - Berechnetes VPD
- `sensor.athena_dryback_percent` - Aktueller Dryback
- `sensor.athena_current_phase` - Aktuelle Irrigationsphase (P0-P3)

**Steuerung:**
- `switch.athena_automation_enabled` - Automatisierung ein/aus
- `select.athena_growth_phase` - Wachstumsphase auswählen
- `select.athena_crop_steering` - Crop Steering Strategie
- `button.athena_irrigation_shot_medium` - Manueller Bewässerungsschuss

#### Erste Bewässerung testen:
1. `button.athena_irrigation_shot_small` drücken (2% Schuss)
2. Beobachten Sie die VWC-Änderung in `sensor.athena_vwc`
3. Prüfen Sie den Dryback über Zeit

### 6. Dashboard einrichten

#### Schnelle Karte erstellen:
```yaml
# Zu dashboard hinzufügen
type: entities
title: Athena Plant Monitor
entities:
  - sensor.athena_vwc
  - sensor.athena_ec_substrate
  - sensor.athena_current_phase
  - select.athena_growth_phase
  - switch.athena_automation_enabled
  - button.athena_irrigation_shot_medium
```

#### Erweiterte Visualisierung:
```yaml
type: vertical-stack
cards:
  # Status-Übersicht
  - type: glance
    title: System Status
    entities:
      - entity: sensor.athena_current_phase
        name: Phase
      - entity: sensor.athena_vwc
        name: VWC
      - entity: sensor.athena_dryback_percent
        name: Dryback
      - entity: switch.athena_automation_enabled
        name: Auto

  # VWC Trend
  - type: history-graph
    title: VWC Verlauf (24h)
    entities:
      - sensor.athena_vwc
      - sensor.athena_vwc_target
    hours_to_show: 24
    refresh_interval: 0

  # Steuerung
  - type: entities
    title: Bewässerungssteuerung
    entities:
      - select.athena_growth_phase
      - select.athena_crop_steering
      - number.athena_substrate_size
      - button.athena_irrigation_shot_small
      - button.athena_irrigation_shot_medium
      - button.athena_irrigation_shot_large
```

### 7. Automatisierung einrichten

#### Basis-Automatisierung (P2 Maintenance):
```yaml
# configuration.yaml → automations:
- alias: "Athena P2 Maintenance Irrigation"
  trigger:
    - platform: numeric_state
      entity_id: sensor.athena_dryback_percent
      above: 5.0  # 5% Dryback löst Bewässerung aus
  condition:
    - condition: state
      entity_id: binary_sensor.athena_lights_on
      state: 'on'
    - condition: state  
      entity_id: switch.athena_automation_enabled
      state: 'on'
    - condition: state
      entity_id: sensor.athena_current_phase
      state: 'P2'  # Nur in Maintenance Phase
  action:
    - service: athena_plant_monitor.irrigation_shot
      data:
        shot_size: >
          {% if is_state('select.athena_crop_steering', 'vegetative') %}
            4.0
          {% elif is_state('select.athena_crop_steering', 'generative') %}
            2.5
          {% else %}
            3.0
          {% endif %}
        duration: 30
```

#### P1 Sättigungsphase (Morgens):
```yaml
- alias: "Athena P1 Saturation Sequence"
  trigger:
    - platform: state
      entity_id: light.athena_led_panel
      to: 'on'
  condition:
    - condition: state
      entity_id: switch.athena_automation_enabled
      state: 'on'
    - condition: time
      after: '06:00:00'
      before: '10:00:00'
  action:
    # P0 Phase: Warten für zusätzlichen Dryback
    - delay: '01:30:00'  # 1.5 Stunden warten
    # P1 Phase: Sättigungssequenz starten
    - service: athena_plant_monitor.p1_saturation_sequence
      data:
        shot_count: 3
        shot_size: 4.0
        interval_minutes: 20
```

### 8. Troubleshooting

#### Gerät wird nicht erkannt:
```bash
# ESPHome-Logs prüfen
esphome logs athena-node-1.yaml

# Home Assistant-Logs prüfen  
# Einstellungen → System → Logs
# Nach "athena_plant_monitor" filtern
```

#### Sensoren zeigen keine Werte:
1. ESPHome-Gerät online prüfen: **Einstellungen** → **ESPHome**
2. Entitäten prüfen: **Einstellungen** → **Entitäten** → nach "athena" filtern
3. Sensor-Kalibrierung in ESPHome prüfen

#### Bewässerung funktioniert nicht:
1. Pumpen-Entität manuell testen: `switch.athena_manual_pump`
2. ESPHome-GPIO-Pins prüfen
3. Services testen: **Entwicklertools** → **Services** → `athena_plant_monitor.irrigation_shot`

#### Performance-Optimierung:
```yaml
# In ESPHome Konfiguration
# Update-Intervalle reduzieren für bessere Performance
sensor:
  - platform: adc
    pin: A0
    name: "VWC"
    update_interval: 60s  # Statt 30s
    filters:
      - throttle: 30s     # Nur bei Änderungen senden
```

### 9. Erweiterte Features

#### InfluxDB Integration:
```yaml
# configuration.yaml
influxdb:
  host: localhost
  port: 8086
  database: homeassistant
  include:
    entities:
      - sensor.athena_vwc
      - sensor.athena_ec_substrate
      - sensor.athena_vpd_calculated
      - sensor.athena_dryback_percent
```

#### Benachrichtigungen:
```yaml
# Kritische Alerts
- alias: "Athena Critical Alert Notification"
  trigger:
    - platform: numeric_state
      entity_id: sensor.athena_alerts_critical
      above: 0
  action:
    - service: notify.mobile_app
      data:
        title: "🚨 Athena Critical Alert"
        message: >
          {% set alerts = state_attr('sensor.athena_alerts_critical', 'messages') %}
          {{ alerts | join(', ') if alerts else 'Kritischer Alert ausgelöst' }}
        data:
          priority: high
          tag: athena_critical
```

### 10. Support & Weiterführende Links

- **GitHub Issues**: [athena-plant-monitor/issues](https://github.com/avi23/athena-plant-monitor/issues)
- **Home Assistant Community**: [community.home-assistant.io](https://community.home-assistant.io)
- **ESPHome Dokumentation**: [esphome.io](https://esphome.io)
- **Athena Agriculture**: [athena.ag](https://athena.ag)

#### Häufige Fragen:
- **Q**: Welche ESPHome-Versionen werden unterstützt?
  **A**: ESPHome 2023.1+ empfohlen, funktioniert ab 2022.12

- **Q**: Kann ich mehrere Pflanzen überwachen?
  **A**: Ja, installieren Sie die Integration für jedes ESPHome-Gerät separat

- **Q**: Funktioniert es mit anderen Mikrocontrollern als ESP32?
  **A**: Ja, ESP8266 wird ebenfalls unterstützt, ESP32 ist jedoch empfohlen

---

**🎉 Herzlichen Glückwunsch!** Ihre Athena Plant Monitor Integration ist einsatzbereit. Beginnen Sie mit den Grundfunktionen und erweitern Sie schrittweise um erweiterte Automatisierungen.
