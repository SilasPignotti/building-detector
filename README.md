# Building Detector

Eine Webanwendung zur Erkennung und Extraktion von Gebäudeumrissen aus Satellitenbildern.

## Übersicht

Building Detector ist ein Tool, das Nutzern hilft, Gebäudegeometrien aus Satellitenbildern mittels Deep Learning schnell zu identifizieren und zu extrahieren. Die Anwendung bietet eine einfache Weboberfläche, auf der Nutzer:

1. Ein Interessengebiet auf einer Karte auswählen können
2. Satellitenbilder für das ausgewählte Gebiet herunterladen können
3. Referenzpunkte auf spezifischen Gebäuden platzieren können, um den Erkennungsalgorithmus gezielt zu steuern
4. Das Bild verarbeiten können, um die markierten Gebäude zu identifizieren
5. Die erkannten Gebäude im GeoJSON-Format oder im OpenStreetMap-kompatiblen Format herunterladen können

Das System nutzt eine zweiteilige Architektur:
- Eine Flask-Webanwendung (dieses Repository) stellt die Benutzeroberfläche bereit
- Ein Machine-Learning-Modell, das auf einem Colab-Server läuft (verbunden über ngrok), führt die eigentliche Gebäudeerkennung durch

## Funktionen

- Interaktive kartenbasierte Oberfläche zur Gebietsauswahl
- Ein-Klick-Download von Satellitenbildern
- Punktbasierte Steuerung des Erkennungsalgorithmus
  - Der Nutzer bestimmt durch Punktsetzung präzise, welche spezifischen Gebäude erkannt werden sollen
  - Nur die markierten Gebäude werden vom Algorithmus verarbeitet und zurückgegeben
- Gebäuderegularisierung zur Erzeugung sauberer Geometrien
- Exportoptionen:
  - Standard-GeoJSON mit Gebäudemetadaten
  - OpenStreetMap-kompatibles GeoJSON für einfache OSM-Beiträge

## Projektstruktur

```
building-detector/
│
├── app/ - Hauptanwendungsverzeichnis
│   ├── app.py - Hauptanwendungsdatei (Flask-Server)
│   ├── config.py - Konfigurationseinstellungen
│   ├── static/ - Statische Ressourcen
│   │   ├── Logo.png - Anwendungslogo
│   │   ├── script.js - Frontend-JavaScript
│   │   └── style.css - CSS-Styling
│   ├── templates/ - HTML-Vorlagen
│   │   └── index.html - Hauptseite
│   ├── utils/ - Hilfsfunktionen
│   │   └── logger.py - Logging-Funktionalität
│   └── logs/ - Verzeichnis für Protokolldateien
│
├── uploads/ - Temporärer Speicher für hochgeladene und verarbeitete Dateien
└── requirements.txt - Python-Abhängigkeiten
```

## Architektur

Diese Anwendung folgt einer vereinfachten MVC-Architektur:

- **Model**: Die Datenverarbeitung und -verwaltung erfolgt in app.py
- **View**: Die Darstellung wird durch templates/index.html und static/-Dateien gesteuert
- **Controller**: Die Routenlogik in app.py verbindet Benutzeraktionen mit der Datenverarbeitung

Die Anwendung interagiert mit einem externen Colab-Server, der das Machine-Learning-Modell für die Gebäudeerkennung hostet.

## Technische Realisierung

### Frontend (Flask Web App)
- Interaktive Karte mit Leaflet
- Benutzerinterface für Punktsetzung und Steuerung des Erkennungsprozesses
- HTTP-Kommunikation mit dem ML-Backend

### Backend (Colab ML Server)
- Flask-API mit flask-cors für Cross-Origin-Anfragen
- Segment Anything Model 2 (SAM2) für präzise Bildsegmentierung
- Verarbeitungsablauf:
  1. Empfang von Satellitenbild und Punktkoordinaten
  2. Anwendung des SAM2-Modells zur Erkennung der durch Punkte markierten Gebäude
  3. Regionengruppierung zur Bildung zusammenhängender Gebäudestrukturen
  4. Geometrieregularisierung für präzisere Gebäudeumrisse
  5. Rückgabe der erkannten Gebäude als GeoJSON

## Voraussetzungen

- Python 3.8+
- Flask
- leafmap (für Satellitenbilder)
- Moderner Webbrowser mit aktiviertem JavaScript
- Internetverbindung

## Installation

1. Klonen Sie dieses Repository:
   ```bash
   git clone https://github.com/yourusername/building-detector.git
   cd building-detector
   ```

2. Erstellen Sie eine virtuelle Umgebung (empfohlen):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   ```

3. Installieren Sie die erforderlichen Pakete:
   ```bash
   pip install -r requirements.txt
   ```

4. Konfigurieren Sie die Anwendung:
   - Aktualisieren Sie die `COLAB_SERVER_URL` in `app/config.py` falls erforderlich
   - Stellen Sie sicher, dass das Verzeichnis `uploads` existiert und beschreibbar ist

## Ausführen der Anwendung

1. Starten Sie den Flask-Server:
   ```bash
   python app/app.py
   ```

2. Öffnen Sie einen Webbrowser und navigieren Sie zu:
   ```
   http://127.0.0.1:5000/
   ```

## Verwendung

1. **Gebiet auswählen**: Nutzen Sie die Kartenoberfläche, um zu Ihrem Interessengebiet zu navigieren
2. **Satellitenbild herunterladen**: Klicken Sie auf "Satellitenbild herunterladen" für den sichtbaren Bereich
3. **Punkte setzen**: Platzieren Sie Punkte auf den zu erkennenden Gebäuden
   - Jeder Punkt markiert ein spezifisches Gebäude zur Erkennung
   - Nur die markierten Gebäude werden vom Algorithmus verarbeitet
4. **Verarbeiten**: Klicken Sie auf "Gebäude erkennen", um den Erkennungsprozess zu starten
5. **Ergebnisse herunterladen**: Laden Sie die erkannten Gebäude im Standard-GeoJSON-Format oder im OpenStreetMap-kompatiblen Format herunter

## Colab-Server-Einrichtung

Diese Anwendung benötigt einen Colab-Server, auf dem das Gebäudeerkennungsmodell läuft.

Wenn Sie diese Anwendung lokal verwenden möchten, führen Sie folgende Schritte aus:

1. Zugriff auf das Colab-Notebook unter: [Building Detector Colab Server](https://colab.research.google.com/drive/1aKfw2RQrQkvgA0oXCKz_iMguSdGdbFaC?usp=sharing)

2. Erstellen Sie eine Kopie des Notebooks in Ihrem eigenen Google Drive

3. Besorgen Sie sich ein ngrok-Authentifizierungstoken:
   - Registrieren Sie sich auf [ngrok.com](https://ngrok.com)
   - Finden Sie Ihr Auth-Token in Ihrem ngrok-Dashboard

4. Führen Sie das Colab-Notebook aus:
   - Geben Sie Ihr ngrok-Token ein, wenn Sie dazu aufgefordert werden
   - Das Notebook stellt Ihnen eine öffentliche URL zur Verfügung

5. Kopieren Sie die vom Notebook bereitgestellte ngrok-URL und fügen Sie sie in die Variable `COLAB_SERVER_URL` in Ihrer Datei `app/config.py` ein

Denken Sie daran, dass sich die ngrok-URL bei jedem Neustart des Colab-Notebooks ändert, sodass Sie die Konfiguration entsprechend aktualisieren müssen.

## Autor

Silas Pignotti