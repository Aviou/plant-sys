# Athena Plant Monitor - Home Assistant Integration

Eine fortschrittliche HACS-Integration für Home Assistant zur Überwachung und Steuerung von Pflanzen basierend auf den wissenschaftlich validierten Athena® Standards.

## 🌱 Features

### Vollständige Athena® Implementation
- **P0-P3 Bewässerungsphasen**: Komplette Umsetzung aller vier Athena® Irrigationsphasen
- **Crop Steering**: Vegetative, generative und ausgewogene Steuerungsstrategien
- **VPD-gesteuerte Klimakontrolle**: Automatische VPD-Berechnung und -Steuerung mit Tag/Nacht-Unterscheidung
- **Tag/Nacht-Zyklen**: Dynamische Zielwerte für Temperatur, Luftfeuchtigkeit, VPD und CO₂
- **EC-Stacking**: Intelligente Nährstoffmanagement-Strategien
- **Dryback-Targets**: Präzise Rücktrocknungssteuerung nach Wachstumsphase
- **9 Klimastrategien**: Von "Optimale Bedingungen halten" bis "Aktive Kühlung"
- **6 Lüftungsmodi**: Intelligente Ventilationssteuerung

### ESPHome Integration
- **Automatische Erkennung**: Findet automatisch ESPHome-Geräte mit Pflanzensensoren
- **Native Entitäten**: Alle Sensoren und Aktoren als Home Assistant Entitäten
- **Echtzeit-Monitoring**: Kontinuierliche Datenaktualisierung alle 30 Sekunden
- **Fehlerbehandlung**: Robuste Behandlung von Sensorausfällen

### UI-basierte Konfiguration
- **Kein YAML erforderlich**: Vollständige Konfiguration über die Home Assistant UI
- **Automatische Entdeckung**: Erkennt verfügbare ESPHome-Geräte automatisch
- **Erweiterte Optionen**: Feinabstimmung aller Parameter über Optionsflow

## 📊 Sensoren

### Umweltmonitoring
- Lufttemperatur, Luftfeuchtigkeit, Luftdruck (innen & außen)
- CO₂-Konzentration
- **VPD (berechnet)**: Automatische Dampfdruckdefizit-Berechnung für innen & außen
- **Differenzialsensoren**: Temperatur-, Luftfeuchtigkeits- und VPD-Unterschiede
- **Tag/Nacht-Status**: Automatische Erkennung über WLAN-Lichtsteuerung oder Zeitplan

### Substratmonitoring
- **VWC (Volumetrischer Wassergehalt)**: Substratfeuchte-Messung
- **EC Substrat**: Elektrische Leitfähigkeit für Nährstoffüberwachung
- **pH Substrat**: pH-Wert des Substrats
- Substrattemperatur
- **Dryback Prozent**: Automatische Dryback-Berechnung

### Zielwert-Sensoren
- **VPD, Temperatur, Luftfeuchtigkeit, CO₂**: Dynamische Zielwerte basierend auf Tag/Nacht-Zyklus
- **VWC, EC, pH**: Zielwerte basierend auf Wachstumsphase und Crop Steering
- **Automatische Anpassung** basierend auf aktueller Phase und Zeit
- **Abweichungsberechnung** von aktuellen zu Zielwerten mit Prozentangabe

### Status-Sensoren
- **Aktuelle Irrigationsphase** (P0, P1, P2, P3)
- **Wachstumsphase** (Vegetativ, Blütephase, etc.)
- **Crop Steering Strategie** (Vegetativ, Generativ, Ausgewogen)
- **Tag/Nacht-Zyklus**: Zeigt aktuellen Status ("Tag" oder "Nacht")
- **Tageswassermenge** und **Max VWC Heute**

## 🔧 Aktoren & Steuerung

### Schalter
- **Automatische Bewässerung**: Ein/Aus-Steuerung der Automatisierung
- **Manuelle Pumpe**: Direktsteuerung der Bewässerungspumpe
- **Klimasteuerung**: Zu-/Abluft, Be-/Entfeuchter, CO₂-Ventil
- **Automatische Klimaregelung**: Aktiviert/deaktiviert die automatische Klimaoptimierung
- **VPD-Optimierung**: Intelligente VPD-basierte Klimasteuerung
- **Notfall-Lüftung**: Maximale Belüftung in Notsituationen

### Eingabefelder
- **Substratgröße**: Einstellung des Substratvolumens
- **Manuelle Zielwerte**: Überschreibung der automatischen Zielwerte
- **Bewässerungsparameter**: Schussgröße und -dauer

### Auswahlfelder
- **Wachstumsphase**: Vegetativ, Blütephase (Stretch, Bulk, Finish)
- **Crop Steering**: Vegetativ, Generativ, Ausgewogen

### Aktionsbuttons
- **Bewässerungsschüsse**: Klein (2%), Mittel (3%), Groß (5%)
- **Zähler-Reset**: Tageswasser und Max VWC zurücksetzen
- **Sensor-Kalibrierung**: Triggert ESPHome-Kalibrierung
- **Notfall-Stopp**: Sofortiger Stopp aller Bewässerung

## 🚨 Alert-System

### Kritische Alerts
- **VWC kritisch niedrig**: < 50% (Notfall-Bewässerung)
- **EC kritisch hoch**: > 10 ppm (Salzstress)

### Warnungen
- **VWC sehr hoch**: > 95% (Staunässe)
- **EC niedrig**: < 2 ppm (Nährstoffmangel)
- **pH außerhalb Bereich**: < 5.0 oder > 7.0
- **VPD hoch**: > 2.0 kPa (Trockenstress)

### Informationen
- **VPD niedrig**: < 0.5 kPa (Schimmelrisiko)

## 🛠️ Services

### `athena_plant_monitor.irrigation_shot`
Führt einen manuellen Bewässerungsschuss aus
```yaml
service: athena_plant_monitor.irrigation_shot
data:
  shot_size: 3.0  # Prozent des Substratvolumens
  duration: 30    # Sekunden
```

### `athena_plant_monitor.set_growth_phase`
Setzt die Wachstumsphase
```yaml
service: athena_plant_monitor.set_growth_phase
data:
  phase: flowering_bulk
```

### `athena_plant_monitor.set_crop_steering`
Setzt die Crop Steering Strategie
```yaml
service: athena_plant_monitor.set_crop_steering
data:
  strategy: generative
```

### `athena_plant_monitor.p1_saturation_sequence`
Führt die komplette P1 Sättigungsphase aus
```yaml
service: athena_plant_monitor.p1_saturation_sequence
data:
  shot_count: 3
  shot_size: 4.0
  interval_minutes: 20
```

### `athena_plant_monitor.emergency_protocol`
Aktiviert Notfallprotokoll
```yaml
service: athena_plant_monitor.emergency_protocol
data:
  disable_automation: true
  stop_all_pumps: true
```

### `athena_plant_monitor.apply_climate_strategy`
Wendet eine Klimastrategie an
```yaml
service: athena_plant_monitor.apply_climate_strategy
data:
  strategy: heat_dehumidify  # Optional, automatisch wenn nicht angegeben
```

### `athena_plant_monitor.set_ventilation_mode`
Setzt den Lüftungsmodus
```yaml
service: athena_plant_monitor.set_ventilation_mode
data:
  mode: increase_intake
```

### `athena_plant_monitor.optimize_vpd`
Optimiert das VPD
```yaml
service: athena_plant_monitor.optimize_vpd
data:
  target_vpd: 1.2  # Optional, automatisch wenn nicht angegeben
```

## 📦 Installation

### Über HACS (empfohlen)
1. HACS in Home Assistant installieren
2. "Benutzerdefinierte Repositories" → Repository hinzufügen
3. URL: `https://github.com/avi23/athena-plant-monitor`
4. Kategorie: "Integration"
5. Integration installieren und Home Assistant neu starten

### Manuelle Installation
1. Repository herunterladen
2. `custom_components/athena_plant_monitor/` nach Home Assistant kopieren
3. Home Assistant neu starten

## ⚙️ Konfiguration

### 1. ESPHome Gerät vorbereiten
Stellen Sie sicher, dass Ihr ESPHome-Gerät folgende Entitäten hat:
```yaml
# Minimum erforderlich:
sensor:
  - platform: ...
    name: "VWC"
    id: vwc_sensor
    
switch:
  - platform: gpio
    name: "Pump"
    id: pump_switch
```

### 2. Integration hinzufügen
1. **Einstellungen** → **Geräte & Services** → **Integration hinzufügen**
2. "Athena Plant Monitor" suchen
3. ESPHome-Gerät auswählen
4. Grundkonfiguration vornehmen
5. Optional: Erweiterte Einstellungen konfigurieren

### 3. Automatisierungen
Die Integration funktioniert am besten mit den mitgelieferten Automatisierungs-Blueprints:

```yaml
# Beispiel Automatisierung für P2 Maintenance Phase
- alias: "Athena P2 Maintenance Irrigation"
  trigger:
    platform: numeric_state
    entity_id: sensor.athena_dryback_percent
    above: 5.0  # 5% Dryback löst Bewässerung aus
  condition:
    - condition: state
      entity_id: binary_sensor.athena_lights_on
      state: 'on'
    - condition: state
      entity_id: switch.athena_automation_enabled
      state: 'on'
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
```

## 📊 Dashboard-Beispiel

```yaml
type: vertical-stack
cards:
  # System Status
  - type: entities
    title: Athena System Status
    entities:
      - entity: sensor.athena_current_phase
        name: Aktuelle Phase
      - entity: select.athena_growth_phase
        name: Wachstumsphase
      - entity: select.athena_crop_steering
        name: Crop Steering
      - entity: switch.athena_automation_enabled
        name: Automatisierung

  # Aktueller Zustand
  - type: glance
    title: Aktuelle Messwerte
    entities:
      - entity: sensor.athena_vwc
        name: VWC
      - entity: sensor.athena_ec_substrate
        name: EC
      - entity: sensor.athena_ph_substrate
        name: pH
      - entity: sensor.athena_vpd_calculated
        name: VPD
      - entity: sensor.athena_dryback_percent
        name: Dryback

  # Zielwerte vs. Ist-Werte
  - type: custom:mini-graph-card
    name: VWC Trend mit Zielwert
    entities:
      - entity: sensor.athena_vwc
        name: VWC Ist
      - entity: sensor.athena_vwc_target
        name: VWC Ziel
        show_line: false
        show_points: false
        y_axis: secondary
    hours_to_show: 24
    points_per_hour: 2

  # Bewässerungssteuerung
  - type: entities
    title: Bewässerungssteuerung
    entities:
      - entity: button.athena_irrigation_shot_small
        name: Kleiner Schuss (2%)
      - entity: button.athena_irrigation_shot_medium
        name: Mittlerer Schuss (3%)
      - entity: button.athena_irrigation_shot_large
        name: Großer Schuss (5%)
      - entity: sensor.athena_daily_water_total
        name: Tageswasser
      - entity: switch.athena_manual_pump
        name: Pumpe

  # Alerts
  - type: conditional
    conditions:
      - entity: sensor.athena_alerts_critical
        state_not: "0"
    card:
      type: entities
      title: 🚨 Kritische Alerts
      state_color: true
      entities:
        - entity: sensor.athena_alerts_critical
```

## 🔧 ESPHome Konfiguration

Beispiel für eine vollständige ESPHome-Konfiguration:

```yaml
esphome:
  name: athena-node-1
  
# ... WiFi, API, etc. ...

sensor:
  # Umweltsensoren
  - platform: bme280
    temperature:
      name: "Temperature"
      id: temp_sensor
    humidity:
      name: "Humidity"
      id: humidity_sensor
    pressure:
      name: "Pressure"
      id: pressure_sensor
      
  # Substrat VWC
  - platform: capacitive_soil_moisture
    pin: A0
    name: "VWC"
    id: vwc_sensor
    update_interval: 30s
    calibration:
      dry_value: 595
      wet_value: 295
    filters:
      - calibrate_linear:
        - 0.0 -> 0.0
        - 1.0 -> 100.0
        
  # EC Sensor
  - platform: ads1115
    multiplexer: 'A0_GND'
    gain: 4.096
    name: "EC Substrate"
    id: ec_sensor
    update_interval: 30s
    unit_of_measurement: "ppm"
    accuracy_decimals: 1
    
  # pH Sensor  
  - platform: ads1115
    multiplexer: 'A1_GND'
    gain: 4.096
    name: "pH Substrate"
    id: ph_sensor
    update_interval: 30s
    accuracy_decimals: 1
    
  # Substrattemperatur
  - platform: dallas
    address: 0x123456789ABCDEF0
    name: "Temp Substrate"
    id: temp_substrate_sensor
    
  # CO2
  - platform: senseair
    co2:
      name: "CO2"
      id: co2_sensor
      
  # Wassertank
  - platform: ultrasonic
    trigger_pin: D1
    echo_pin: D2
    name: "Water Level"
    id: water_level_sensor
    unit_of_measurement: "%"
    
binary_sensor:
  # Leckage-Sensor
  - platform: gpio
    pin: D3
    name: "Leak Sensor"
    id: leak_sensor
    device_class: moisture
    
switch:
  # Pumpe
  - platform: gpio
    pin: D4
    name: "Pump"
    id: pump_switch
    
  # Ventilatoren
  - platform: gpio
    pin: D5
    name: "Fan Intake"
    id: fan_intake_switch
    
  - platform: gpio
    pin: D6
    name: "Fan Exhaust"  
    id: fan_exhaust_switch
    
  # Luftbefeuchter/Entfeuchter
  - platform: gpio
    pin: D7
    name: "Humidifier"
    id: humidifier_switch
    
  - platform: gpio
    pin: D8
    name: "Dehumidifier"
    id: dehumidifier_switch
    
  # CO2 Ventil
  - platform: gpio
    pin: D9
    name: "CO2 Valve"
    id: co2_valve_switch
    
light:
  # LED Panel
  - platform: neopixelbus
    type: GRB
    variant: WS2812
    pin: D10
    num_leds: 30
    name: "LED Panel"
    id: led_panel
```

## 🚀 Roadmap

### Geplante Features
- [ ] **Grafische Trends**: Erweiterte Visualisierung mit Apex Charts
- [ ] **Machine Learning**: Vorhersage optimaler Bewässerungszeiten
- [ ] **Multi-Zone Support**: Unterstützung für mehrere Bewässerungszonen
- [ ] **Runoff-Messung**: Integration von Runoff-Sensoren für erweiterte Analytik
- [ ] **Backup/Restore**: Konfiguration und historische Daten sichern
- [ ] **Mobile Widgets**: Spezielle Widgets für die Home Assistant Mobile App

### Integrationen
- [ ] **InfluxDB**: Erweiterte Datenanalyse und -speicherung
- [ ] **Grafana**: Professionelle Dashboard-Erstellung
- [ ] **Telegram/Discord**: Benachrichtigungen und Fernsteuerung
- [ ] **Node-RED**: Erweiterte Automatisierungslogik

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte lesen Sie [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

### Entwicklung
```bash
# Repository klonen
git clone https://github.com/avi23/athena-plant-monitor.git

# Development Container verwenden
code athena-plant-monitor
# "Reopen in Container" auswählen

# Tests ausführen
pytest

# Code formatieren
black custom_components/
isort custom_components/
```

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- **Athena Agriculture** für die wissenschaftlichen Standards
- **ESPHome Team** für die hervorragende IoT-Plattform
- **Home Assistant Community** für die kontinuierliche Unterstützung

## 📞 Support

- **GitHub Issues**: [Issues](https://github.com/avi23/athena-plant-monitor/issues)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)
- **Discord**: [Home Assistant Discord](https://discord.gg/home-assistant)

---

**⚠️ Hinweis**: Diese Integration ist für Bildungs- und Hobbyzwecke gedacht. Befolgen Sie immer die örtlichen Gesetze und Vorschriften bezüglich des Pflanzenanbaus.
