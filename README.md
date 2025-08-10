# Plant Monitoring System

Ein System zur Überwachung von Pflanzen mit verschiedenen Sensoren.

## Sensoren

| Sensor ID | Kategorie | Typ | Beschreibung |
|-----------|-----------|-----|--------------|
| TEMP-002 | Temperatur | BME280| Lufttemperatur Innen |
| HUMID-001 | Feuchtigkeit | BME280 | Luftfeuchtigkeit Innen|
| PRESSURE-001 | Umwelt | BME280 | Luftdruck Innen|
| VPD-001 | VPD | Calc | VPD Innen |
| TEMP-003 | Temperatur | DHT22| Lufttemperatur Außen |
| HUMID-002 | Feuchtigkeit | DHT22 | Luftfeuchtigkeit Außen|
| VPD-002 | VPD | Calc | VPD Außen |
| LIGHT-001 | Licht | BH1750 | Umgebungslicht |
| UV-001 | Licht | VEML6070 | UV-Strahlung |
| TEMP-001 | Temperatur | DS18B20 | Bodentemperatur |
| PH-001 | pH-Wert | Analog pH | Boden pH-Wert |
| EC-001 | EC-Wert | DS18B20 | Boden Ec-Wert |
| VWC-001 | Bodenfeuchtigkeit | DS18B20 | Bodenfeuchtigkeit |
| CO2-001 | Umwelt | MH-Z19B | CO2-Konzentration |



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


