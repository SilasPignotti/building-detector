import os
import logging
from flask import Flask, request, jsonify, render_template, send_file
import leafmap
import requests
import uuid
import json
from datetime import datetime
from utils.logger import logger

app = Flask(__name__)

# Disable Flask's default logging to stdout
app.logger.handlers = []
for handler in logging.getLogger('werkzeug').handlers:
    logging.getLogger('werkzeug').removeHandler(handler)

# Set upload folder relative to project directory, not app directory
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['COLAB_SERVER_URL'] = 'https://5a71-34-139-152-103.ngrok-free.app'  # Updated ngrok URL from Colab Server

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_file_path(filename):
    """
    Helper function to generate file paths in the upload directory.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        str: Complete path to the file in the upload directory
    """
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    """
    Render the main application page.
    
    Returns:
        HTML: The rendered index.html template
    """
    logger.info('Loading index page')
    return render_template('index.html')

@app.route('/get_satellite', methods=['POST'])
def get_satellite():
    """
    Download satellite imagery for the specified bounding box.
    
    Expects a JSON with west, south, east, north coordinates.
    Returns a JSON with the image URL and ID.
    
    Returns:
        JSON: Response with image URL and ID, or error message
    """
    try:
        data = request.json
        bbox = [data['west'], data['south'], data['east'], data['north']]
        logger.info(f"Received bbox: {bbox}")
        
        # Generate unique filename
        image_id = str(uuid.uuid4())
        tif_path = get_file_path(f'satellite_{image_id}.tif')
        logger.info(f"Will save to: {tif_path}")
        
        try:
            # Download satellite image
            logger.info("Starting download with leafmap...")
            leafmap.map_tiles_to_geotiff(
                output=tif_path,
                bbox=bbox,
                zoom=18,
                source="Satellite",
                overwrite=True
            )
            logger.info("Download completed successfully")
        except Exception as download_error:
            logger.error(f"Error during download: {str(download_error)}", exc_info=True)
            raise download_error

        # Check if file exists and its size
        if os.path.exists(tif_path):
            file_size = os.path.getsize(tif_path)
            logger.info(f"TIF file exists, size: {file_size} bytes")
        else:
            raise FileNotFoundError(f"TIF file was not created at {tif_path}")
        
        return jsonify({
            'success': True,
            'image_url': f'/uploads/satellite_{image_id}.tif',
            'image_id': image_id
        })
    except Exception as e:
        logger.error(f"Error in get_satellite: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process():
    """
    Process a satellite image with the provided points to detect buildings.
    
    Expects a JSON with points array (lat, lon pairs).
    Sends the image and points to a Colab server for processing.
    Returns the URL to the processed GeoJSON result.
    
    Returns:
        JSON: Response with result URL or error message
    """
    try:
        data = request.json
        points = data['points']
        logger.info(f"Received points: {points}")
        
        # Transform points from [lat, lon] to [lon, lat] format
        transformed_points = [[p[1], p[0]] for p in points]  # Swap lat/lon to lon/lat
        logger.info(f"Transformed points: {transformed_points}")
        
        # Find the latest satellite image based on creation time
        satellite_images = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith('satellite_')]
        if not satellite_images:
            return jsonify({'error': 'No satellite image found'}), 400
            
        # Sort by creation time, newest first
        satellite_images.sort(key=lambda x: os.path.getctime(get_file_path(x)), reverse=True)
        latest_image = satellite_images[0]
        image_path = get_file_path(latest_image)
        logger.info(f"Using most recent image: {image_path} (created: {os.path.getctime(image_path)})")
        
        if not os.path.exists(image_path):
            return jsonify({'error': f'Image file not found: {image_path}'}), 400
        
        # Send image and points to Colab server
        colab_url = f"{app.config['COLAB_SERVER_URL']}/detect"
        logger.info(f"Sending request to Colab server at: {colab_url}")
        logger.info(f"Number of points: {len(transformed_points)}")
        
        return send_to_colab_server(colab_url, image_path, latest_image, transformed_points)
                
    except Exception as e:
        logger.error(f"Error in process: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def send_to_colab_server(colab_url, image_path, image_filename, transformed_points):
    """
    Send the image and points to the Colab server for processing.
    
    Args:
        colab_url (str): URL of the Colab server endpoint
        image_path (str): Path to the image file
        image_filename (str): Name of the image file
        transformed_points (list): List of [lon, lat] coordinates
        
    Returns:
        JSON: Response with result URL or error message
    """
    try:
        # Prepare multipart form data
        with open(image_path, 'rb') as f:
            image_data = f.read()
            logger.info(f"Image size: {len(image_data)} bytes")

        # Create multipart form data
        files = {
            'image': (image_filename, image_data, 'image/tiff')
        }
        
        # Send transformed points as form data
        data = {
            'points': json.dumps(transformed_points)
        }
        
        response = requests.post(
            colab_url,
            files=files,
            data=data,
            timeout=300  # Set timeout to 5 minutes for large images
        )
        
        logger.info(f"Colab server response status: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        
        try:
            response_text = response.text
            logger.debug(f"Response text: {response_text}")
        except:
            logger.warning("Could not decode response text")
        
        if response.status_code != 200:
            error_msg = f"Processing failed on Colab server (Status {response.status_code})"
            try:
                error_msg += f": {response.text}"
            except:
                pass
            return jsonify({'error': error_msg}), 500
        
        # Save results
        result_path = get_file_path('building_regularized.geojson')
        with open(result_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Results saved to: {result_path}")
        return jsonify({
            'success': True,
            'result_url': '/uploads/building_regularized.geojson'
        })
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Colab server: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to connect to Colab server: {str(e)}'}), 500

@app.route('/download')
def download():
    """
    Download the building detection results as a GeoJSON file.
    
    Returns:
        File: GeoJSON file with building detection results
    """
    try:
        return send_file(
            get_file_path('building_regularized.geojson'),
            as_attachment=True,
            download_name='building_detection_result.geojson'
        )
    except Exception as e:
        logger.error(f"Error in download: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/download_osm')
def download_osm():
    """
    Download the building detection results in OSM-compatible format.
    
    Accepts optional tag parameters to customize the OSM tags.
    
    Returns:
        File: GeoJSON file formatted for OSM import
    """
    try:
        # Read the GeoJSON file
        with open(get_file_path('building_regularized.geojson'), 'r') as f:
            geojson_data = json.load(f)

        # Get tags from request parameters
        custom_tags = {}
        if request.args.get('tags'):
            try:
                custom_tags = json.loads(request.args.get('tags'))
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in tags parameter")
                # Continue with default tags

        # Make sure there's at least a building tag
        if 'building' not in custom_tags:
            custom_tags['building'] = 'yes'
            
        # Add generation date if not provided
        if 'source:date' not in custom_tags:
            custom_tags['source:date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Convert to OSM-compatible GeoJSON
        osm_geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for feature in geojson_data['features']:
            # Use the custom tags for each building
            feature['properties'] = custom_tags.copy()
            osm_geojson['features'].append(feature)

        # Save as new file
        osm_file_path = get_file_path('buildings_for_osm.geojson')
        with open(osm_file_path, 'w') as f:
            json.dump(osm_geojson, f)

        return send_file(
            osm_file_path,
            as_attachment=True,
            download_name='buildings_for_osm_import.geojson'
        )
    except Exception as e:
        logger.error(f"Error in download_osm: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve uploaded files.
    
    Args:
        filename (str): Name of the file to serve
        
    Returns:
        File: The requested file
    """
    return send_file(get_file_path(filename))

if __name__ == '__main__':
    logger.info('Starting OSM Building Detector application')
    app.run(debug=False)
