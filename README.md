# Building Detector 🏢

*An AI-powered web application for detecting and extracting building footprints from satellite imagery*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Building Detector is a sophisticated tool that leverages deep learning to identify and extract building geometries from satellite imagery. The application provides an intuitive web interface where users can:

✅ **Select areas of interest** on an interactive map  
✅ **Download high-resolution** satellite imagery  
✅ **Place reference points** on specific buildings to guide the detection algorithm  
✅ **Process images** to identify marked buildings  
✅ **Export results** in GeoJSON format or OpenStreetMap-compatible format  

## Architecture

The system uses a **two-tier architecture**:

- **Frontend (Flask Web App)**: Provides the user interface and handles satellite imagery downloads
- **Backend (Colab ML Server)**: Runs the machine learning model using Segment Anything Model 2 (SAM2)

## Key Features

- 🗺️ **Interactive map-based interface** for area selection
- 📡 **One-click satellite image download** for any region
- 🎯 **Point-based detection control** - users specify exactly which buildings to detect
- 🔧 **Building regularization** for clean, precise geometries  
- 📊 **Dual export options**:
  - Standard GeoJSON with building metadata
  - OpenStreetMap-compatible GeoJSON for easy OSM contributions

## Project Structure

```
building-detector/
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
│
├── app/                      # Main application directory
│   ├── app.py               # Flask server & routing logic
│   ├── config.py            # Configuration settings
│   ├── config.py.template   # Configuration template
│   ├── static/              # Static assets (CSS, JS, images)
│   ├── templates/           # HTML templates
│   └── utils/               # Utility functions
│
├── local_backend/           # 🆕 Local ML backend (SAM2)
│   ├── local_server.py     # Local SAM2 server
│   ├── requirements.txt    # ML dependencies
│   └── README.md           # Setup instructions
│
├── uploads/                 # Temporary storage (auto-created)
├── UML/                    # System documentation
├── building-detector.ipynb # Colab notebook
└── .env.example           # Environment template
```

## Technology Stack

- **Backend**: Flask, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript, Leaflet.js
- **AI/ML**: Segment Anything Model 2 (SAM2)
- **Geospatial**: leafmap, GeoJSON
- **Deployment**: ngrok (for Colab connectivity)

## Prerequisites

- **Python 3.8** or higher
- Modern **web browser** with JavaScript enabled
- **Internet connection** for satellite imagery and ML processing
- **Google Colab account** (for ML backend)

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/building-detector.git
cd building-detector
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

### 5. Access the Web Interface
Open your browser and navigate to: **http://127.0.0.1:5000/**

## Configuration

### Option 1: Google Colab Backend (Recommended)

1. **Access the Colab notebook**: [Building Detector ML Server](https://colab.research.google.com/drive/1aKfw2RQrQkvgA0oXCKz_iMguSdGdbFaC?usp=sharing)
2. **Make a copy** to your Google Drive
3. **Get ngrok token**: Register at [ngrok.com](https://ngrok.com) and copy your auth token
4. **Run the notebook**: Enter your ngrok token when prompted
5. **Update configuration**: Copy the ngrok URL to `app/config.py`:
   ```python
   COLAB_SERVER_URL = 'https://your-ngrok-url.ngrok.io'
   ```

### Option 2: Local Backend (Full SAM2 Implementation)

**NEW!** Run the complete AI pipeline locally using the same SAM2 model as Colab:

1. **Install local backend**:
   ```bash
   cd local_backend
   pip install -r requirements.txt
   ```

2. **Start local ML server**:
   ```bash
   python local_server.py  # Runs on port 5001
   ```

3. **Configure main app**:
   ```bash
   export COLAB_SERVER_URL='http://127.0.0.1:5001'
   python main.py
   ```

**Benefits**: No cloud dependencies, data privacy, no session timeouts
**Requirements**: 8GB+ RAM, Python 3.8+, optional GPU for speed

See [local_backend/README.md](local_backend/README.md) for detailed setup instructions.

## Usage Guide

1. **📍 Select Area**: Navigate to your area of interest on the interactive map
2. **📡 Download Imagery**: Click "Download Satellite Image" for the visible region
3. **🎯 Place Points**: Click on buildings you want to detect (each click marks a building)
4. **⚙️ Process**: Click "Detect Buildings" to start the AI processing
5. **💾 Export Results**: Download detected buildings as GeoJSON files

## Security & Configuration

- API keys and credentials are externalized to environment variables
- Sensitive data is excluded from version control via `.gitignore`
- Upload directory is automatically cleaned between sessions

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Silas Pignotti**

---

*Built with ❤️ for the geospatial and OpenStreetMap communities*