# Building Detector

AI-powered building detection from satellite imagery using SAM2.

Building Detector is a portfolio project by a Geoinformation student. The web app lets users select an area on a map, place guide points on buildings, and run SAM2-based detection with footprint regularization. Results can be exported as standard GeoJSON or in an OpenStreetMap-compatible format.

## Features

- Point-guided building detection from satellite imagery
- SAM2-based segmentation with footprint regularization
- Satellite image download through `leafmap`
- Dual export formats: standard GeoJSON and OSM-compatible GeoJSON
- Support for either a local SAM2 backend or a Colab-hosted backend

## Architecture

The project uses a simple two-part architecture:

- **Flask web app** for the browser UI, imagery download, and export flows
- **SAM2 backend** running either locally or through Colab for detection processing

UML diagrams and architecture notes are available in the [`UML/`](UML/) directory.

## Quickstart

1. Clone the repository.
2. Install the main application dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask app:
   ```bash
   python main.py
   ```
4. Configure either the local backend or the Colab backend before running detection.

For detailed backend setup, see [`local_backend/README.md`](local_backend/README.md).

## Tech Stack

- Python
- Flask
- SAM2 / `segment-geospatial`
- Leafmap
- Leaflet.js
- Rasterio
- GeoPandas

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).
