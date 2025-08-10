# Plant Monitoring System

Ein System zur Überwachung von Pflanzen mit verschiedenen Sensoren.

## Sensoren

| Sensor ID | Kategorie | Typ | Messbereich | Genauigkeit | Beschreibung | Status |
|-----------|-----------|-----|-------------|-------------|--------------|--------|
| TEMP-001 | Temperatur | DS18B20 | -55°C bis +125°C | ±0.5°C | Bodentemperatur | ✅ Aktiv |
| TEMP-002 | Temperatur | DHT22 | -40°C bis +80°C | ±0.5°C | Lufttemperatur | ✅ Aktiv |
| HUMID-001 | Feuchtigkeit | DHT22 | 0-100% RH | ±2-5% RH | Luftfeuchtigkeit | ✅ Aktiv |
| SOIL-001 | Feuchtigkeit | Kapazitiv | 0-100% | ±3% | Bodenfeuchtigkeit | ✅ Aktiv |
| LIGHT-001 | Licht | BH1750 | 1-65535 lux | ±20% | Umgebungslicht | ✅ Aktiv |
| UV-001 | Licht | VEML6070 | 0-15 UV Index | ±1 UV Index | UV-Strahlung | 🔧 Wartung |
| PH-001 | pH-Wert | Analog pH | 0-14 pH | ±0.1 pH | Boden pH-Wert | ✅ Aktiv |
| CO2-001 | Umwelt | MH-Z19B | 400-5000 ppm | ±50 ppm + 3% | CO2-Konzentration | ✅ Aktiv |
| PRESSURE-001 | Umwelt | BMP280 | 300-1100 hPa | ±1 hPa | Luftdruck | ✅ Aktiv |

## Status-Legende
- ✅ **Aktiv**: Sensor funktioniert normal
- 🔧 **Wartung**: Sensor benötigt Wartung
- ❌ **Defekt**: Sensor ist ausgefallen
- 🔄 **Konfiguration**: Sensor wird eingerichtet

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


