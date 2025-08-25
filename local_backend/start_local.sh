#!/bin/bash
# Quick start script for local backend

echo "🏢 Building Detector - Local Backend Setup"
echo "========================================="

# Check if we're in the right directory
if [[ ! -f "local_server.py" ]]; then
    echo "❌ Error: Please run this script from the local_backend directory"
    echo "   cd local_backend && ./start_local.sh"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting local ML backend..."
echo "This will download SAM2 model weights on first run (~600MB)"
echo ""

# Set environment variable for main app
export COLAB_SERVER_URL='http://127.0.0.1:5001'
echo "✅ Set COLAB_SERVER_URL to local backend"

# Start the server
python local_server.py