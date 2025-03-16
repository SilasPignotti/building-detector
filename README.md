# Building Detector

A web application that helps detect and extract building outlines from satellite imagery.

## Overview

Building Detector is a tool designed to help users quickly identify and extract building geometries from satellite imagery using deep learning. The application provides a simple web interface where users can:

1. Select an area of interest on a map
2. Download satellite imagery for the selected area
3. Provide sample points to guide the building detection algorithm
4. Process the image to identify buildings
5. Download the detected buildings in GeoJSON format or OpenStreetMap-compatible format

The system uses a two-part architecture:
- A Flask web application (this repository) provides the user interface
- A machine learning model running on a Colab server (connected via ngrok) performs the actual building detection

## Features

- Interactive map-based interface for area selection
- One-click satellite imagery download
- Point-based guidance for the detection algorithm
- Building regularization to create clean geometries
- Export options:
  - Standard GeoJSON with building metadata
  - OpenStreetMap-compatible GeoJSON for easy OSM contributions

## Project Structure

```
building-detector/
│
├── app/ - Main application directory
│   ├── app.py - Main application file (Flask server)
│   ├── config.py - Configuration settings
│   ├── static/ - Static resources
│   │   ├── Logo.png - Application logo
│   │   ├── script.js - Frontend JavaScript
│   │   └── style.css - CSS styling
│   ├── templates/ - HTML Templates
│   │   └── index.html - Main page
│   ├── utils/ - Helper functions
│   │   └── logger.py - Logging functionality
│   └── logs/ - Directory for log files
│
├── uploads/ - Temporary storage for uploaded and processed files
└── requirements.txt - Python dependencies
```

## Architecture

This application follows a simplified MVC architecture:

- **Model**: Data processing and management occurs in app.py
- **View**: Presentation is controlled by templates/index.html and static/ files
- **Controller**: Route logic in app.py connects user actions with data processing

The application interacts with an external Colab server that hosts the machine learning model for building detection.

## Requirements

- Python 3.8+
- Flask
- leafmap (for satellite imagery)
- Modern web browser with JavaScript enabled
- Internet connection

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/building-detector.git
   cd building-detector
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the application:
   - Update the `COLAB_SERVER_URL` in `app/config.py` if necessary
   - Make sure the `uploads` directory exists and is writable

## Running the Application

1. Start the Flask server:
   ```bash
   python app/app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage

1. **Select Area**: Use the map interface to navigate to your area of interest
2. **Download Satellite Image**: Click "Download Satellite Image" for the visible area
3. **Provide Guidance**: Place points on buildings to guide the detection algorithm
4. **Process**: Click "Detect Buildings" to run the building detection process
5. **Download Results**: Download the detected buildings in standard GeoJSON format or OpenStreetMap-compatible format

## Colab Server Setup

This application requires a companion Colab server running the building detection model. 

If you want to use this application locally, follow these steps:

1. Access the Colab notebook at: [Building Detector Colab Server](https://colab.research.google.com/drive/1aKfw2RQrQkvgA0oXCKz_iMguSdGdbFaC?usp=sharing)

2. Make a copy of the notebook to your own Google Drive

3. Get an ngrok authentication token:
   - Sign up at [ngrok.com](https://ngrok.com)
   - Find your auth token in your ngrok dashboard

4. Run the Colab notebook:
   - Enter your ngrok token when prompted
   - The notebook will provide you with a public URL

5. Copy the ngrok URL provided by the notebook and paste it into the `COLAB_SERVER_URL` variable in your `app/config.py` file

Remember that the ngrok URL will change each time you restart the Colab notebook, so you'll need to update the configuration accordingly.

## Contributors

Silas Pignotti

## Acknowledgments

- This project was developed as part of the course "Entwurfsmethoden und Muster" in the Geoinformatics Master's program.