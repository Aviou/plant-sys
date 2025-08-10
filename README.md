# Plant Monitoring System

Ein System zur Überwachung von Pflanzen mit verschiedenen Sensoren.
g
## Sensoren

| Sensor ID | Kategorie | Typ | Beschreibung |
|-----------|-----------|-----|--------------|
| TEMP-001 | Temperatur | BME280| Lufttemperatur Innen |
| HUMID-001 | Feuchtigkeit | BME280 | Luftfeuchtigkeit Innen|
| PRESSURE-001 | Umwelt | BME280 | Luftdruck Innen|
| VPD-001 | VPD | Calc | VPD Innen |
| TEMP-002 | Temperatur | DHT22| Lufttemperatur Außen |
| HUMID-002 | Feuchtigkeit | DHT22 | Luftfeuchtigkeit Außen|
| VPD-002 | VPD | Calc | VPD Außen |
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
| DRYBACK-001 | Rücktrockung | Calc| Soil Dryback |
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
| DEHUMIDIFIER-001 | Entfeuchtung | Pletier  | Luftentfeuchter |


## Messwerte
Alle Sensoren werden kontinuierlich überwacht und die Daten werden gespeichert für:
- Echtzeit-Monitoring
- Historische Datenanalyse
- Benachrichtigungen bei kritischen Werten
- Automatische Bewässerung und Klimasteuerung

## Hinweise
- Sensoren werden alle 30 Sekunden ausgelesen
- Kalibrierung erfolgt monatlich
- Bei Sensorausfall wird automatisch eine Benachrichtigung gesendet

---
*Letzte Aktualisierung: August 2025*


