# Local Backend Server

This directory contains a **full local implementation** of the building detection backend using the **same SAM2 model and logic** as the Colab notebook. This allows you to run the complete AI-powered building detection pipeline locally without relying on Google Colab or cloud services.

## 🚀 Features

- **Same ML model**: Uses SAM2 (Segment Anything Model 2) with `sam2-hiera-large`
- **Identical logic**: Exact same processing pipeline as the Colab notebook
- **Point-guided detection**: Click on buildings to guide the AI detection
- **Shape regularization**: Produces clean, accurate building polygons
- **Local processing**: No cloud dependencies once set up

## 📋 System Requirements

- **Python 3.8+**
- **8GB+ RAM** (recommended for SAM2 model)
- **GPU support** (optional but recommended for faster processing):
  - NVIDIA GPU with CUDA support
  - Intel GPU with OpenVINO (experimental)
  - Apple Silicon Mac (uses Metal Performance Shaders)

## ⚡ Quick Start

### 1. Install Dependencies

```bash
cd local_backend
pip install -r requirements.txt
```

**Note**: The installation may take some time as it downloads the SAM2 model weights (~600MB) on first run.

### 2. Run the Local Server

```bash
python local_server.py
```

The server will start on `http://127.0.0.1:5001/`

You'll see output like:
```
Starting Building Detector Local Backend...
This uses the same SAM2 model as the Colab notebook.
Server will be available at: http://127.0.0.1:5001/
✅ SAM2 model available - ready for detection!
```

### 3. Configure the Main App

**Option A: Environment Variable**
```bash
export COLAB_SERVER_URL='http://127.0.0.1:5001'
python main.py
```

**Option B: Update Config File**
In your `app/config.py`, change:
```python
COLAB_SERVER_URL = 'http://127.0.0.1:5001'
```

### 4. Start the Main Application
```bash
python main.py
```

Now both servers are running:
- **Main App**: http://127.0.0.1:5000/ (web interface)
- **ML Backend**: http://127.0.0.1:5001/ (AI processing)

## 🔧 API Endpoints

- **GET /health** - Health check and dependency status
- **GET /status** - Detailed server capabilities and model info
- **POST /detect** - AI-powered building detection (same interface as Colab)

## 🐛 Troubleshooting

### Dependencies Not Available
If you see warnings about missing SAM dependencies:
```bash
pip install segment-geospatial
```

### CUDA/GPU Issues
For NVIDIA GPU support:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

For CPU-only (slower but works everywhere):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Memory Issues
If you encounter out-of-memory errors:
- Ensure you have at least 8GB RAM
- Close other applications
- Consider using a smaller model (modify `model_id` in the code)

### First Run is Slow
The first detection takes longer as it downloads model weights. Subsequent runs are much faster.

## 📊 Performance Comparison

| Backend Type | Setup Time | Processing Speed | GPU Required | Internet Required |
|--------------|------------|------------------|--------------|-------------------|
| Colab        | ~2 minutes | Fast             | ✅ (Free)    | ✅ Always        |
| Local        | ~10 minutes| Variable*        | ⚪ Optional  | ⚪ Setup only    |

*Local speed depends on your hardware: GPU > Apple Silicon > CPU

## 🔄 Switching Between Backends

You can easily switch between Colab and local backends:

1. **Use Colab**: Set `COLAB_SERVER_URL` to your ngrok URL
2. **Use Local**: Set `COLAB_SERVER_URL` to `http://127.0.0.1:5001`

Both use identical APIs, so switching is seamless!

## 🆚 Local vs Colab Trade-offs

### Local Backend Advantages
- ✅ No internet required after setup
- ✅ Data privacy (nothing sent to cloud)
- ✅ No session timeouts
- ✅ Customizable processing parameters

### Colab Backend Advantages  
- ✅ No local setup required
- ✅ Always latest GPU hardware
- ✅ No local storage requirements
- ✅ Quick to get started

## 🔧 Advanced Configuration

You can modify the detection parameters in `local_server.py`:

```python
# Model selection (trade-off between accuracy and speed)
model_id="sam2-hiera-large"    # Best accuracy (default)
model_id="sam2-hiera-base"     # Balanced
model_id="sam2-hiera-small"    # Faster

# Detection sensitivity
min_size=200    # Minimum building size (pixels)
min_size=100    # Detect smaller buildings
min_size=500    # Only detect larger buildings
```