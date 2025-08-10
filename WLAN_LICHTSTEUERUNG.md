# WLAN-Steckdosen Lichtsteuerung - Dashboard Beispiele

## 🔗 Integration mit WLAN-Steckdosen

Die Athena Plant Monitor Integration unterstützt jetzt **WLAN-Steckdosen** und andere externe Switch-Entitäten zur Lichtsteuerung. Dies ermöglicht eine nahtlose Tag/Nacht-Erkennung auch bei Verwendung von Standard-WLAN-Steckdosen wie:

- **Shelly Plug S**
- **TP-Link Kasa HS100/HS110**
- **Sonoff S31**
- **Philips Wiz Smart Plugs**
- **Tasmota-basierte Steckdosen**
- Jede andere Switch-Entität in Home Assistant

## ⚙️ Konfiguration

### 1. WLAN-Steckdose in Home Assistant einrichten
Stellen Sie sicher, dass Ihre WLAN-Steckdose bereits als Switch-Entität in Home Assistant verfügbar ist:

```yaml
# Beispiel für eine Shelly Steckdose
switch:
  - platform: shelly
    host: 192.168.1.100
    name: "Growlight Steckdose"
```

### 2. Athena Integration konfigurieren
Bei der Einrichtung der Athena Plant Monitor Integration:

1. **Grundkonfiguration**: ESPHome-Gerät und Parameter wählen
2. **Lichtsteuerung**: Ihre WLAN-Steckdose aus der automatisch erkannten Liste auswählen
3. **Zeitplan**: Backup-Zeiten für automatische Steuerung (da kein Lichtsensor vorhanden)

### 3. Tag/Nacht-Erkennung (ohne Lichtsensor)
Die Integration nutzt folgende Methoden in Prioritätsreihenfolge:
1. **Externe Lichtentität** (WLAN-Steckdose) - Primäre Methode
2. **ESPHome LED Panel** (falls vorhanden)
3. **ESPHome Growlight Switch** (falls vorhanden)
4. **Zeitbasierte Erkennung** (Fallback: 06:00-22:00 oder konfigurierbar)

## 📱 Dashboard-Karten

### Lichtsteuerungs-Karte
```yaml
type: entities
title: Wachstumslicht Steuerung
entities:
  - entity: switch.athena_external_grow_light
    name: Wachstumslicht
    icon: mdi:lightbulb-on
  - entity: sensor.athena_is_day_cycle
    name: Tag/Nacht Status
  - entity: sensor.athena_temperature_target
    name: Temperatur Ziel (dynamisch)
  - entity: sensor.athena_vpd_target
    name: VPD Ziel (dynamisch)
  - type: divider
  - entity: switch.growlight_steckdose  # Ihre originale Steckdose
    name: Direkte Steckdosen-Steuerung
```

### Tag/Nacht Übersicht
```yaml
type: glance
title: Tag/Nacht Klimaziele
entities:
  - entity: sensor.athena_is_day_cycle
    name: Zyklus
  - entity: sensor.athena_temperature_target
    name: Temp Ziel
  - entity: sensor.athena_humidity_target
    name: Feuchte Ziel
  - entity: sensor.athena_vpd_target
    name: VPD Ziel
  - entity: sensor.athena_co2_target
    name: CO₂ Ziel
```

### Zeitplan-Steuerung
```yaml
type: entities
title: Licht-Zeitplan
entities:
  - entity: input_datetime.light_schedule_start
    name: Licht An
  - entity: input_datetime.light_schedule_end
    name: Licht Aus
  - entity: automation.athena_light_schedule
    name: Automatik
```

## 🤖 Automatisierungen

### Automatische Lichtsteuerung basierend auf Zeitplan
```yaml
automation:
  - alias: "Athena Licht Ein"
    trigger:
      - platform: time
        at: "06:00:00"  # Oder aus Konfiguration
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.athena_external_grow_light
      - service: athena_plant_monitor.optimize_vpd
        # Optimiert VPD für Tag-Zyklus

  - alias: "Athena Licht Aus"
    trigger:
      - platform: time
        at: "22:00:00"  # Oder aus Konfiguration
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.athena_external_grow_light
      - service: athena_plant_monitor.optimize_vpd
        # Optimiert VPD für Nacht-Zyklus
```

### Tag/Nacht-basierte Klimaanpassung
```yaml
automation:
  - alias: "Athena Tag/Nacht Klimaanpassung"
    trigger:
      - platform: state
        entity_id: sensor.athena_is_day_cycle
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.grow_room_climate
        data:
          temperature: "{{ states('sensor.athena_temperature_target') | float }}"
      - service: climate.set_humidity
        target:
          entity_id: climate.grow_room_climate
        data:
          humidity: "{{ states('sensor.athena_humidity_target') | float }}"
```

### Erweiterte Lichtsteuerung mit Dimming (falls unterstützt)
```yaml
automation:
  - alias: "Sunrise Dimming"
    trigger:
      - platform: time
        at: "05:30:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.growlight_dimmer
        data:
          brightness: 1
      - repeat:
          count: 30
          sequence:
            - delay: "00:01:00"
            - service: light.turn_on
              target:
                entity_id: light.growlight_dimmer
              data:
                brightness: "{{ (repeat.index * 8) | int }}"
```

## 📊 Überwachung und Alerts

### Licht-Status Überwachung
```yaml
automation:
  - alias: "Licht-Ausfall Alert"
    trigger:
      - platform: state
        entity_id: sensor.athena_is_day_cycle
        to: "Tag"
        for: "00:15:00"  # 15 Minuten nach geplantem Start
    condition:
      - condition: state
        entity_id: switch.athena_external_grow_light
        state: "off"
    action:
      - service: notify.mobile_app
        data:
          title: "🚨 Athena Alert"
          message: "Wachstumslicht ist aus, obwohl Tag-Zyklus aktiv sein sollte!"
```

### Energieverbrauch Tracking
```yaml
sensor:
  - platform: history_stats
    name: "Growlight Tagesstunden"
    entity_id: switch.athena_external_grow_light
    state: "on"
    type: time
    start: "{{ now().replace(hour=0, minute=0, second=0) }}"
    end: "{{ now() }}"

  - platform: template
    sensors:
      growlight_daily_cost:
        friendly_name: "Growlight Tageskosten"
        unit_of_measurement: "€"
        value_template: >
          {% set hours = states('sensor.growlight_tagesstunden') | float %}
          {% set power = 300 %}  # Watt
          {% set cost_per_kwh = 0.30 %}  # €/kWh
          {{ ((hours * power / 1000) * cost_per_kwh) | round(2) }}
```

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. Steckdose wird nicht erkannt
```yaml
# Manuell zur Liste hinzufügen
# In der Integration-Konfiguration:
external_light_entity: "switch.ihre_steckdose_hier"
```

#### 2. Tag/Nacht Erkennung funktioniert nicht
- Prüfen Sie die Logs: `custom_components.athena_plant_monitor.coordinator`
- Stellen Sie sicher, dass die Steckdose korrekt geschaltet wird
- Überprüfen Sie die Zeitplan-Konfiguration

#### 3. Verzögerung bei Klimaanpassung
```yaml
# Forciere sofortige Anpassung
automation:
  - alias: "Force Climate Update"
    trigger:
      - platform: state
        entity_id: switch.athena_external_grow_light
    action:
      - service: homeassistant.update_entity
        target:
          entity_id: sensor.athena_is_day_cycle
      - delay: "00:00:05"
      - service: athena_plant_monitor.optimize_vpd
```

## 💡 Pro-Tipps

### 1. Backup-Sensoren nutzen
```yaml
# Kombiniere mehrere Erkennungsmethoden
template:
  - sensor:
      - name: "Athena Smart Day Cycle"
        state: >
          {% if is_state('switch.athena_external_grow_light', 'on') %}
            Tag
          {% elif now().hour >= 6 and now().hour < 22 %}
            Tag
          {% else %}
            Nacht
          {% endif %}
```

### 2. Energie-effiziente Zeiten nutzen
```yaml
# Lichtzeiten an günstige Stromtarife anpassen
automation:
  - alias: "Günstige Strom-Zeiten nutzen"
    trigger:
      - platform: time
        at: "22:00:00"  # Nachtstrom beginnt
    condition:
      - condition: state
        entity_id: binary_sensor.electricity_cheap
        state: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.athena_external_grow_light
```

### 3. Redundanz für kritische Phasen
```yaml
# Backup-Steuerung für wichtige Wachstumsphasen
automation:
  - alias: "Blütephase Licht-Backup"
    trigger:
      - platform: state
        entity_id: switch.athena_external_grow_light
        to: "off"
        for: "00:05:00"
    condition:
      - condition: state
        entity_id: select.athena_growth_phase
        state: "flowering_bulk"
      - condition: state
        entity_id: sensor.athena_is_day_cycle
        state: "Tag"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.backup_growlight
      - service: notify.critical
        data:
          message: "Hauptlicht ausgefallen - Backup aktiviert!"
```

---

## ✅ Zusammenfassung

Mit der erweiterten Lichtsteuerungs-Integration können Sie:

- **WLAN-Steckdosen** für Growlights nutzen
- **Automatische Tag/Nacht-Erkennung** über beliebige Switch-Entitäten
- **Dynamische Klimaziele** basierend auf Licht-Status
- **Flexible Zeitpläne** mit Backup-Mechanismen
- **Umfassende Überwachung** und Alerts

Die Integration ist **vollständig kompatibel** mit allen gängigen Smart Home Geräten und bietet maximale Flexibilität bei der Lichtsteuerung! 💡🌱
