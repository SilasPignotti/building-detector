// Map Module - Handles map operations
const MapModule = (function() {
    // Private variables
    let _map;
    let _drawnItems;
    let _markerGroup;
    let _currentBuildingLayer = null;
    let _currentSatelliteLayer = null;
    let _layerControl = null;
    let _baseMaps = {};
    let _overlayMaps = {};
    let _boundsCache = null;
    let _lastBoundsUpdateTime = 0;
    let _hasDrawnRectangle = false;
    const BOUNDS_CACHE_TTL = 1000; // Time in ms before bounds cache is considered stale

    // Initialize the map
    function init() {
        // Center map on Berlin
        _map = L.map('map').setView([52.5200, 13.4050], 12);

        // Define base layers
        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        });

        const satelliteBaseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        });

        // Base maps for Layer Control
        _baseMaps = {
            "OpenStreetMap": osmLayer,
            "Satellite": satelliteBaseLayer
        };

        // Add default layer
        osmLayer.addTo(_map);

        // Initialize Draw control
        _drawnItems = new L.FeatureGroup().addTo(_map);
        _markerGroup = new L.FeatureGroup().addTo(_map);

        // Initialize Draw control
        const drawControl = new L.Control.Draw({
            draw: {
                polygon: false,
                circle: false,
                circlemarker: false,
                polyline: false,
                marker: {
                    icon: new L.Icon.Default(),
                    repeatMode: true  // Keep marker mode active after placing a marker
                },
                rectangle: {
                    shapeOptions: {
                        color: '#3498db'
                    }
                }
            },
            edit: {
                featureGroup: _drawnItems
            }
        });
        _map.addControl(drawControl);

        // Add Layer Control (collapsed by default)
        _layerControl = L.control.layers(_baseMaps, {}, {
            position: 'topright',
            collapsed: true
        }).addTo(_map);

        // Set up listeners for map interactions
        _map.on('click', handleMapClick);
        _map.on('moveend', clearBoundsCache);
        _map.on('zoomend', clearBoundsCache);
        
        // Set up draw listeners
        _map.on('draw:created', function(e) {
            const type = e.layerType;
            const layer = e.layer;
            
            // Handle different layer types
            if (type === 'rectangle') {
                // Clear previously drawn rectangles
                _drawnItems.clearLayers();
                
                // Add the newly drawn rectangle
                _drawnItems.addLayer(layer);
                
                _hasDrawnRectangle = true;
                document.getElementById('get-satellite-btn').disabled = false;
                
                // Hide statistics panel when drawing a new area
                hideStatisticsPanel();
                
                // Clear previously added building layer if it exists
                if (_currentBuildingLayer) {
                    _map.removeLayer(_currentBuildingLayer);
                    _currentBuildingLayer = null;
                    document.getElementById('building-count').textContent = '0';
                }
                
                // Clear bounds cache
                clearBoundsCache();
            } 
            else if (type === 'marker') {
                // For markers, just add to marker group without clearing existing ones
                _markerGroup.addLayer(layer);
                
                // Enable detect buildings button if we have at least one marker
                document.getElementById('detect-buildings-btn').disabled = false;
            }
        });
        
        // Handle edit and delete events
        _map.on('draw:deleted', function(e) {
            const layers = e.layers;
            
            // Check if rectangle was deleted
            if (layers.getLayers().some(layer => layer instanceof L.Rectangle)) {
                _hasDrawnRectangle = false;
                document.getElementById('get-satellite-btn').disabled = true;
                UIModule.updateStatus("Draw an area to begin", true);
            }
        });

        // Initialize markers for building detection
        _map.on('draw:drawstart', function (e) {
            if (e.layerType === 'marker') {
                // Don't clear existing markers when placing new ones
                // Only hide statistics panel
                hideStatisticsPanel();
                
                // Clear building layer if it exists
                if (_currentBuildingLayer) {
                    _map.removeLayer(_currentBuildingLayer);
                    _currentBuildingLayer = null;
                    document.getElementById('building-count').textContent = '0';
                }
            }
        });
    }

    // Handle map click event
    function handleMapClick(e) {
        // Only add markers if in marker mode
        // Note: This is handled directly by the Leaflet.draw controls now
    }

    // Get map bounds with caching to prevent redundant calculations
    function getBounds() {
        const now = Date.now();
        // Use cached bounds if available and not too old
        if (_boundsCache && (now - _lastBoundsUpdateTime < BOUNDS_CACHE_TTL)) {
            return _boundsCache;
        }
        
        // Otherwise, get new bounds and cache them
        _boundsCache = _map.getBounds();
        _lastBoundsUpdateTime = now;
        return _boundsCache;
    }

    // Clear bounds cache when the map view changes
    function clearBoundsCache() {
        _boundsCache = null;
    }

    // Add GeoJSON data to the map
    function addGeoJSONLayer(geojsonData) {
        // Remove previous building layer if it exists
        if (_currentBuildingLayer) {
            _map.removeLayer(_currentBuildingLayer);
        }

        // Add new building layer with custom style
        _currentBuildingLayer = L.geoJSON(geojsonData, {
            style: {
                color: '#ff7800',
                weight: 2,
                opacity: 0.8,
                fillOpacity: 0.35
            }
        }).addTo(_map);
        
        // Update the building count
        const buildingCount = geojsonData.features ? geojsonData.features.length : 0;
        document.getElementById('building-count').textContent = buildingCount;
        
        // Calculate building statistics
        calculateBuildingStatistics(geojsonData);
        
        // Enable export buttons
        document.getElementById('download-geojson-btn').disabled = false;
        document.getElementById('download-osm-btn').disabled = false;
        
        // Update status
        UIModule.updateStatus("Buildings detected", true);
        
        return buildingCount;
    }
    
    // Calculate and display building statistics
    function calculateBuildingStatistics(geojsonData) {
        if (!geojsonData.features || geojsonData.features.length === 0) {
            return;
        }
        
        const features = geojsonData.features;
        const buildingCount = features.length;
        
        // Calculate areas
        let totalArea = 0;
        let minArea = Infinity;
        let maxArea = 0;
        
        for (const feature of features) {
            try {
                // Get area directly from properties if available
                let area = feature.properties.area;
                
                // If area property is not available, calculate using turf
                if (!area || area <= 0) {
                    try {
                        area = turf.area(feature);
                    } catch (calcError) {
                        console.warn('Error calculating area with turf:', calcError);
                        // Fallback to simple calculation if turf fails
                        const polygon = feature.geometry.coordinates[0];
                        area = calculatePolygonArea(polygon);
                    }
                }
                
                // Only add valid areas
                if (area && area > 0) {
                    totalArea += area;
                    minArea = Math.min(minArea, area);
                    maxArea = Math.max(maxArea, area);
                }
            } catch (error) {
                console.warn('Error processing feature:', error);
            }
        }
        
        const avgArea = buildingCount > 0 ? totalArea / buildingCount : 0;
        
        // Ensure minArea is valid
        if (minArea === Infinity || buildingCount === 0) {
            minArea = 0;
        }
        
        // Update statistics panel
        document.getElementById('stat-building-count').textContent = buildingCount;
        document.getElementById('stat-total-area').textContent = formatArea(totalArea);
        document.getElementById('stat-avg-area').textContent = formatArea(avgArea);
        document.getElementById('stat-min-area').textContent = formatArea(minArea);
        document.getElementById('stat-max-area').textContent = formatArea(maxArea);
        
        // Show the statistics panel
        document.getElementById('statistics-panel').classList.remove('hidden');
    }
    
    // Calculate polygon area using a simple algorithm (fallback)
    function calculatePolygonArea(polygon) {
        // Simple implementation of the Shoelace formula
        let area = 0;
        const n = polygon.length;
        
        for (let i = 0; i < n - 1; i++) {
            area += polygon[i][0] * polygon[i+1][1] - polygon[i+1][0] * polygon[i][1];
        }
        // Close the polygon
        area += polygon[n-1][0] * polygon[0][1] - polygon[0][0] * polygon[n-1][1];
        
        // Apply a scaling factor for geographic coordinates (rough approximation)
        // This approximation works for small areas but is not accurate for large regions
        const scale = 10000; // rough scaling for lat/lon to meters
        return Math.abs(area * scale / 2);
    }
    
    // Format area for display
    function formatArea(area) {
        if (!area || area <= 0) return "0 m²";
        
        if (area >= 1000000) {
            return `${(area / 1000000).toFixed(2)} km²`;
        } else {
            return `${Math.round(area)} m²`;
        }
    }

    // Add satellite image overlay to the map
    function addSatelliteOverlay(imageUrl, bounds) {
        // Remove previous satellite layer if it exists
        if (_currentSatelliteLayer) {
            _map.removeLayer(_currentSatelliteLayer);
        }
        
        // Add new satellite layer
        _currentSatelliteLayer = L.imageOverlay(imageUrl, bounds).addTo(_map);
        
        // Enable building detection
        document.getElementById('detect-buildings-btn').disabled = false;
        
        // Update status
        UIModule.updateStatus("Satellite image loaded", true);
    }
    
    // Get drawn rectangle bounds
    function getDrawnRectangleBounds() {
        if (_drawnItems.getLayers().length === 0) {
            return null;
        }
        
        return _drawnItems.getBounds();
    }
    
    // Check if rectangle has been drawn
    function hasDrawnRectangle() {
        return _hasDrawnRectangle;
    }
    
    // Get markers as array of coordinates
    function getMarkersAsPoints() {
        const points = [];
        _markerGroup.eachLayer(function(layer) {
            if (layer instanceof L.Marker) {
                const latlng = layer.getLatLng();
                points.push([latlng.lat, latlng.lng]);
            }
        });
        return points;
    }

    // Hide statistics panel
    function hideStatisticsPanel() {
        document.getElementById('statistics-panel').classList.add('hidden');
    }

    // Public API
    return {
        init: init,
        getBounds: getBounds,
        clearBoundsCache: clearBoundsCache,
        addGeoJSONLayer: addGeoJSONLayer,
        addSatelliteOverlay: addSatelliteOverlay,
        getDrawnRectangleBounds: getDrawnRectangleBounds,
        hasDrawnRectangle: hasDrawnRectangle,
        getMarkersAsPoints: getMarkersAsPoints,
        hideStatisticsPanel: hideStatisticsPanel
    };
})();

// UI Module - Handles user interface interactions
const UIModule = (function() {
    // Show loading overlay
    function showLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = 'flex';
    }

    // Hide loading overlay
    function hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = 'none';
    }
    
    // Update status bar
    function updateStatus(message, isReady) {
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.textContent = message;
            
            // Update status dot color
            const statusDot = document.querySelector('.status-dot');
            if (statusDot) {
                statusDot.style.backgroundColor = isReady ? '#10b981' : '#f59e0b';
            }
        }
    }

    // Show error message to user
    function showError(message) {
        const errorContainer = document.getElementById('error-message');
        if (!errorContainer) {
            // If error container doesn't exist, create one
            const container = document.createElement('div');
            container.id = 'error-message';
            container.className = 'error-notification';
            document.body.appendChild(container);
        }
        
        const errorBox = document.getElementById('error-message');
        errorBox.textContent = message;
        errorBox.style.display = 'block';
        
        // Update status
        updateStatus("Error: " + message, false);
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorBox.style.display = 'none';
        }, 5000);
    }

    // Show success message to user
    function showSuccess(message) {
        const successContainer = document.getElementById('success-message');
        if (!successContainer) {
            // If success container doesn't exist, create one
            const container = document.createElement('div');
            container.id = 'success-message';
            container.className = 'success-notification';
            document.body.appendChild(container);
        }
        
        const successBox = document.getElementById('success-message');
        successBox.textContent = message;
        successBox.style.display = 'block';
        
        // Hide after 3 seconds
        setTimeout(() => {
            successBox.style.display = 'none';
        }, 3000);
    }

    // Public API
    return {
        showLoading: showLoading,
        hideLoading: hideLoading,
        showError: showError,
        showSuccess: showSuccess,
        updateStatus: updateStatus
    };
})();

// API Module - Handles all server requests
const APIModule = (function() {
    // Get satellite image for the current view
    async function getSatelliteImage() {
        const bounds = MapModule.getDrawnRectangleBounds() || MapModule.getBounds();
        
        const data = {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        };

        try {
            UIModule.showLoading();
            UIModule.updateStatus("Downloading satellite imagery...", false);
            
            // Hide statistics panel when getting a new satellite image
            MapModule.hideStatisticsPanel();
            
            // Reset building count
            document.getElementById('building-count').textContent = '0';

            const response = await fetch('/get_satellite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to get satellite image');
            }

            const result = await response.json();
            
            if (result.success) {
                MapModule.addSatelliteOverlay(result.image_url, bounds);
                UIModule.showSuccess('Satellite image downloaded successfully');
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error:', error);
            UIModule.showError(`Failed to download satellite image: ${error.message}`);
        } finally {
            UIModule.hideLoading();
        }
    }

    // Process building detection
    async function processBuildings(points) {
        try {
            UIModule.showLoading();
            UIModule.updateStatus("Detecting buildings...", false);
            
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ points: points })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to process buildings');
            }

            const result = await response.json();
            
            if (result.success) {
                // Fetch and display the GeoJSON data
                const geojsonResponse = await fetch(result.result_url);
                if (!geojsonResponse.ok) {
                    throw new Error('Failed to load GeoJSON result');
                }
                
                const geojsonData = await geojsonResponse.json();
                const buildingCount = MapModule.addGeoJSONLayer(geojsonData);
                UIModule.showSuccess(`${buildingCount} buildings detected successfully`);
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error:', error);
            UIModule.showError(`Building detection failed: ${error.message}`);
            UIModule.updateStatus("Error detecting buildings", false);
        } finally {
            UIModule.hideLoading();
        }
    }

    // Public API
    return {
        getSatelliteImage: getSatelliteImage,
        processBuildings: processBuildings
    };
})();

// Detection Module - Handles building detection logic
const DetectionModule = (function() {
    /**
     * Process building detection from a click point
     */
    async function detectBuildings() {
        const points = MapModule.getMarkersAsPoints();
        
        // If no markers were placed, use the center of the map
        if (points.length === 0) {
            const center = MapModule.getBounds().getCenter();
            points.push([center.lat, center.lng]);
        }
        
        await APIModule.processBuildings(points);
    }
    
    // Public API
    return {
        detectBuildings: detectBuildings
    };
})();

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize map
    MapModule.init();
    
    // Initialize UI state
    UIModule.updateStatus("Draw an area to begin", true);
    
    // Set up button event listeners
    document.getElementById('get-satellite-btn').addEventListener('click', APIModule.getSatelliteImage);
    document.getElementById('detect-buildings-btn').addEventListener('click', DetectionModule.detectBuildings);
    
    // Set up download buttons
    document.getElementById('download-geojson-btn').addEventListener('click', function() {
        window.location.href = '/download';
    });
    
    document.getElementById('download-osm-btn').addEventListener('click', function() {
        // Get tags if available
        const tagsInput = document.getElementById('osm-tags');
        let tagsParameter = '';
        
        if (tagsInput && tagsInput.value) {
            try {
                // Convert key=value format to JSON
                const tagsText = tagsInput.value;
                const tagsLines = tagsText.split('\n');
                const tagsObject = {};
                
                tagsLines.forEach(line => {
                    if (line.trim()) {
                        const [key, value] = line.split('=');
                        if (key && value) {
                            tagsObject[key.trim()] = value.trim();
                        }
                    }
                });
                
                tagsParameter = `?tags=${encodeURIComponent(JSON.stringify(tagsObject))}`;
            } catch (error) {
                UIModule.showError('Invalid format for tags');
                return;
            }
        }
        
        window.location.href = '/download_osm' + tagsParameter;
    });
});
