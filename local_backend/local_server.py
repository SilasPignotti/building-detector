#!/usr/bin/env python3
"""
Local Backend Server for Building Detection

This is a local implementation of the building detection backend using the same
ML models and logic as the Colab notebook. It runs the SAM2 model locally
for actual building detection from satellite imagery.

Based on the original Colab notebook implementation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import json
import traceback
from datetime import datetime

try:
    from samgeo import SamGeo2, regularize
    import rasterio
    import numpy as np
    SAM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SAM dependencies not available: {e}")
    print("Install with: pip install segment-geospatial")
    SAM_AVAILABLE = False

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Building Detector Local Backend',
        'sam_available': SAM_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/detect', methods=['POST'])
def detect():
    """
    Building detection endpoint using SAM2.
    
    This is the exact same logic as in the Colab notebook, adapted for local execution.
    """
    if not SAM_AVAILABLE:
        return jsonify({
            'error': 'SAM dependencies not installed. Please run: pip install segment-geospatial'
        }), 500
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        if 'points' not in request.form:
            return jsonify({'error': 'No points data provided'}), 400

        points = json.loads(request.form['points'])
        print(f"Received points: {points}")

        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_image:
            request.files['image'].save(temp_image.name)
            image_path = temp_image.name
            print(f"Saved image to: {image_path}")

        print("Initializing SAM2 model...")
        sam = SamGeo2(
            model_id="sam2-hiera-large",
            automatic=False,
        )

        sam.set_image(image_path)
        print("SAM model initialized and image set")

        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_mask, \
            tempfile.NamedTemporaryFile(suffix='.geojson', delete=False) as temp_vector, \
            tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_buildings, \
            tempfile.NamedTemporaryFile(suffix='.geojson', delete=False) as output_regularized:

            print("Starting prediction with points...")
            sam.predict_by_points(
                point_coords_batch=points,
                point_crs="EPSG:4326",
                output=temp_mask.name,
                dtype="uint8",
            )
            print(f"Prediction completed, mask saved to: {temp_mask.name}")

            print("Starting region grouping...")
            array, gdf = sam.region_groups(
                temp_mask.name,
                min_size=200,
                out_vector=temp_vector.name,
                out_image=temp_buildings.name
            )
            print(f"Region grouping completed, vector saved to: {temp_vector.name}")

            print("Starting shape regularization...")
            regularize(temp_vector.name, output_regularized.name)
            print(f"Regularization completed, saved to: {output_regularized.name}")

            with open(output_regularized.name, 'rb') as f:
                result = f.read()
            print("Result read successfully")

        os.unlink(image_path)
        os.unlink(temp_mask.name)
        os.unlink(temp_vector.name)
        os.unlink(temp_buildings.name)
        os.unlink(output_regularized.name)

        return result, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"Error in detect: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500  # Return an error message with a 500 status code

@app.route('/status', methods=['GET'])
def get_status():
    """Get server status and capabilities."""
    return jsonify({
        'service': 'Building Detector Local Backend',
        'version': '2.0.0',
        'status': 'running',
        'sam_available': SAM_AVAILABLE,
        'capabilities': [
            'SAM2-based building detection',
            'Point-based guidance', 
            'Region grouping',
            'Shape regularization',
            'GeoJSON export'
        ] if SAM_AVAILABLE else ['Dependencies missing - install segment-geospatial'],
        'model': 'sam2-hiera-large' if SAM_AVAILABLE else None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Building Detector Local Backend...")
    print("This uses the same SAM2 model as the Colab notebook.")
    print("Server will be available at: http://127.0.0.1:5001/")
    
    if not SAM_AVAILABLE:
        print("\n⚠️  WARNING: SAM dependencies not installed!")
        print("Install with: pip install segment-geospatial")
        print("The server will start but detection will not work.\n")
    else:
        print("✅ SAM2 model available - ready for detection!")
    
    print("Health check: http://127.0.0.1:5001/health")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='127.0.0.1', port=5001, debug=False)