import os
import logging
from flask import Flask, request, jsonify, render_template, send_file
import leafmap
import requests
import uuid
import json
from datetime import datetime
from utils.logger import logger
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, COLAB_SERVER_URL

app = Flask(__name__)

app.logger.handlers = []
for handler in logging.getLogger('werkzeug').handlers:
    logging.getLogger('werkzeug').removeHandler(handler)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['COLAB_SERVER_URL'] = COLAB_SERVER_URL

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_file_path(filename):
    """Generate file path in the upload directory."""
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    """Render the main application page."""
    logger.info('Loading index page')
    cleanup_uploads()
    return render_template('index.html')

def cleanup_uploads():
    """Clean up uploads folder, preserving .gitkeep."""
    try:
        logger.info('Cleaning up uploads folder')
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        for file in files:
            if file != '.gitkeep':
                file_path = get_file_path(file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f'Deleted file: {file}')
        logger.info('Uploads folder cleanup complete')
    except Exception as e:
        logger.error(f"Error cleaning uploads folder: {str(e)}", exc_info=True)

@app.route('/get_satellite', methods=['POST'])
def get_satellite():
    """Download satellite imagery for specified bounding box."""
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
    """Process satellite image with points to detect buildings."""
    try:
        data = request.json
        points = data['points']
        logger.info(f"Received points: {points}")
        
        transformed_points = [[p[1], p[0]] for p in points]
        logger.info(f"Transformed points: {transformed_points}")
        
        satellite_images = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith('satellite_')]
        if not satellite_images:
            return jsonify({'error': 'No satellite image found'}), 400
            
        satellite_images.sort(key=lambda x: os.path.getctime(get_file_path(x)), reverse=True)
        latest_image = satellite_images[0]
        image_path = get_file_path(latest_image)
        logger.info(f"Using most recent image: {image_path} (created: {os.path.getctime(image_path)})")
        
        if not os.path.exists(image_path):
            return jsonify({'error': f'Image file not found: {image_path}'}), 400
        
        colab_url = f"{app.config['COLAB_SERVER_URL']}/detect"
        logger.info(f"Sending request to Colab server at: {colab_url}")
        logger.info(f"Number of points: {len(transformed_points)}")
        
        return send_to_colab_server(colab_url, image_path, latest_image, transformed_points)
                
    except Exception as e:
        logger.error(f"Error in process: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def send_to_colab_server(colab_url, image_path, image_filename, transformed_points):
    """Send image and points to Colab server for ML processing."""
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
    """Download building detection results as clean GeoJSON."""
    try:
        with open(get_file_path('building_regularized.geojson'), 'r') as f:
            geojson_data = json.load(f)
        
        clean_geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for feature in geojson_data['features']:
            clean_feature = {
                "type": "Feature",
                "properties": {
                    "building": "yes",
                    "source": "GeoAI Detection",
                    "source:date": datetime.now().strftime("%Y-%m-%d"),
                    "area": round(feature['properties'].get('area', 0), 1)
                },
                "geometry": feature['geometry']
            }
            clean_geojson['features'].append(clean_feature)
        
        # Save the cleaned GeoJSON
        clean_file_path = get_file_path('building_detection_clean.geojson')
        with open(clean_file_path, 'w') as f:
            json.dump(clean_geojson, f, ensure_ascii=False)
        
        return send_file(
            clean_file_path,
            as_attachment=True,
            download_name='building_detection_result.geojson'
        )
    except Exception as e:
        logger.error(f"Error in download: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/download_osm')
def download_osm():
    """Download results in OSM-compatible format."""
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
        
        # Ensure required tags are present
        if 'building' not in custom_tags:
            custom_tags['building'] = 'yes'
        if 'source' not in custom_tags:
            custom_tags['source'] = 'GeoAI Detection'
        if 'source:date' not in custom_tags:
            custom_tags['source:date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Convert to OSM-compatible GeoJSON
        osm_geojson = {
            "type": "FeatureCollection",
            "generator": "Building Detector",
            "features": []
        }

        for feature in geojson_data['features']:
            # Create a copy of custom tags for each feature
            feature_tags = custom_tags.copy()
            
            # Add area as a note tag if significant
            area = feature['properties'].get('area', 0)
            if area > 0:
                feature_tags['note'] = f"Detected building area: {round(area, 1)} m²"
            
            # Create the feature with optimized properties
            osm_feature = {
                "type": "Feature",
                "properties": feature_tags,
                "geometry": feature['geometry']
            }
            osm_geojson['features'].append(osm_feature)

        # Save as new file with UTF-8 encoding
        osm_file_path = get_file_path('buildings_for_osm.geojson')
        with open(osm_file_path, 'w', encoding='utf-8') as f:
            json.dump(osm_geojson, f, ensure_ascii=False)

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
    """Serve uploaded files."""
    return send_file(get_file_path(filename))

if __name__ == '__main__':
    logger.info('Starting Building Detector application')
    app.run(debug=False)
