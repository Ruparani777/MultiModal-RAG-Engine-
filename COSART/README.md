# 🌌 CosArt - Cosmic Generative Art Studio

**Where Art, Math, and the Universe Meet**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-red.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

CosArt is a groundbreaking generative art platform that transforms complex GAN technology into an accessible creative tool infused with cosmic wonder. Generate artwork inspired by the physics, mystery, and beauty of the cosmos through physics-based controls.

---

## ✨ Features

### 🎨 Core Features

- **Multi-Style GAN Generation**: Create high-resolution cosmic artwork (512x512 to 4096x4096)
- **10+ Cosmic Presets**: Nebulae, black holes, galaxies, supernovae, and more
- **Physics-Inspired Controls**: Map scientific concepts to artistic parameters
  - Entropy (Chaos ↔ Order)
  - Spacetime Warp (Curvature)
  - Luminosity (Energy Density)
  - Cosmic Flow (Expansion Rate)
  - Pattern Collapse (Symmetry Breaking)
  - Gravitational Attraction
  - Quantum Uncertainty
  - Spectral Shift (Redshift)

### 🚀 Killer Features

- **🌌 Universe Mode**: Navigate a 3D latent space where each point represents a unique artwork
- **🪐 Generate a Universe**: Create 50-500 coherent artworks with shared "DNA"
- **🌊 Cosmic Evolution**: Smooth interpolation between artworks
- **⚛️ Gravitational Merging**: Mix multiple styles with physics-based blending
- **✨ Constellation Discovery**: Automatically identify clusters in latent space
- **🔭 Quantum Drift**: Automated exploration through latent space

### 🛠️ Technical Features

- Real-time WebSocket generation updates
- Batch processing for efficiency
- High-resolution export with metadata
- Custom model training
- RESTful API with full OpenAPI docs
- Docker deployment ready
- GPU acceleration support

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [API Reference](#api-reference)
4. [Physics Controls](#physics-controls)
5. [Cosmic Presets](#cosmic-presets)
6. [Universe Mode](#universe-mode)
7. [Architecture](#architecture)
8. [Development](#development)
9. [Deployment](#deployment)
10. [Contributing](#contributing)

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- CUDA 11.8+ (for GPU support)
- Docker & Docker Compose (optional)
- Node.js 18+ (for frontend)

### Option 1: Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/cosart.git
cd cosart

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn api.main:app --reload
```

### Option 2: Docker Installation

```bash
# Clone repository
git clone https://github.com/yourusername/cosart.git
cd cosart

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f cosart-api
```

### Option 3: Quick Start with Make

```bash
make install    # Install dependencies
make run        # Run development server
make docker-up  # Run with Docker
```

---

## ⚡ Quick Start

### Generate Your First Cosmic Artwork

```python
import requests

# Generate a nebula
response = requests.post('http://localhost:8000/api/generate', json={
    "preset": "nebula",
    "seed": 12345,
    "resolution": 512,
    "physics_params": {
        "entropy": 0.7,
        "warp": 0.5,
        "luminosity": 0.9
    }
})

result = response.json()
image_base64 = result['images'][0]
print(f"Generated artwork with ID: {result['generation_id']}")
```

### Generate a Complete Universe

```python
# Generate 50 coherent artworks
response = requests.post('http://localhost:8000/api/generate/universe', json={
    "num_artworks": 50,
    "coherence": 0.8,
    "evolution_steps": 10,
    "base_preset": "cosmic_deep_space"
})

universe = response.json()
print(f"Created universe with {universe['num_artworks']} artworks")
print(f"Coherence score: {universe['metadata']['coherence_score']}")
```

### Navigate the 3D Universe

```python
# Find artworks near a position
response = requests.get('http://localhost:8000/api/universe/navigate', params={
    "x": 0.5,
    "y": 0.5,
    "z": 0.5,
    "radius": 0.3
})

nearby = response.json()
print(f"Found {nearby['artworks_found']} nearby artworks")
for artwork in nearby['previews']:
    print(f"  Distance: {artwork['distance']:.3f}")
```

---

## 📚 API Reference

### Endpoints

#### `POST /api/generate`
Generate cosmic artwork with physics-based controls.

**Request Body:**
```json
{
  "preset": "nebula",
  "seed": 12345,
  "resolution": 512,
  "physics_params": {
    "entropy": 0.7,
    "warp": 0.5,
    "luminosity": 0.9,
    "cosmic_flow": 0.5,
    "pattern_collapse": 0.3,
    "attraction": 0.5,
    "uncertainty": 0.2,
    "spectral_shift": 0.5
  },
  "batch_size": 1
}
```

**Response:**
```json
{
  "success": true,
  "generation_id": "uuid-here",
  "images": ["base64-encoded-image"],
  "metadata": {
    "seed": 12345,
    "preset": "nebula",
    "physics_params": {...},
    "timestamp": "2025-12-28T..."
  }
}
```

#### `POST /api/generate/universe`
Generate a complete coherent universe (50-500 artworks).

#### `POST /api/interpolate`
Create smooth transitions between artworks (Cosmic Evolution).

#### `GET /api/universe/navigate`
Navigate the 3D universe and find nearby artworks.

#### `GET /api/presets`
List all available cosmic presets.

#### `POST /api/mix`
Mix multiple styles (Gravitational Merging).

**Full API documentation:** http://localhost:8000/docs

---

## ⚛️ Physics Controls

CosArt maps real physics concepts to artistic parameters:

| Parameter | Scientific Concept | Artistic Effect | Range |
|-----------|-------------------|-----------------|-------|
| **Entropy** | Thermodynamic disorder | Chaos ↔ Order | 0.0 - 1.0 |
| **Warp** | Spacetime curvature | Distortion intensity | 0.0 - 1.0 |
| **Luminosity** | Energy density | Brightness & glow | 0.0 - 1.0 |
| **Cosmic Flow** | Expansion rate | Animation speed | 0.0 - 1.0 |
| **Pattern Collapse** | Symmetry breaking | Structure transition | 0.0 - 1.0 |
| **Attraction** | Gravitational force | Element clustering | 0.0 - 1.0 |
| **Uncertainty** | Quantum fluctuation | Micro-variations | 0.0 - 1.0 |
| **Spectral Shift** | Doppler redshift | Color palette shift | 0.0 - 1.0 |

### Example: Creating a Black Hole

```python
physics_params = {
    "entropy": 0.3,        # Low entropy (ordered structure)
    "warp": 0.95,          # Maximum spacetime curvature
    "luminosity": 0.3,     # Dark (except accretion disk)
    "attraction": 0.95,    # Maximum gravitational pull
    "pattern_collapse": 0.8 # Strong symmetry breaking
}
```

---

## 🌌 Cosmic Presets

### Available Presets

1. **🌌 Nebula** - Colorful star-forming regions with flowing gas
2. **🕳️ Black Hole** - Event horizon with accretion disk
3. **🌀 Galaxy** - Spiral structure with billions of stars
4. **✨ Star Field** - Dense stellar populations
5. **👻 Dark Matter** - Invisible cosmic scaffolding
6. **🕸️ Cosmic Web** - Large-scale structure of the universe
7. **💥 Supernova** - Stellar explosion remnant
8. **📡 CMB Pattern** - Cosmic microwave background fluctuations
9. **🌟 Quasar** - Extremely luminous active galactic nucleus
10. **🪐 Exoplanet** - Alien world atmosphere

### Creating Custom Presets

```python
custom_preset = {
    'name': '🌊 Cosmic Ocean',
    'description': 'Fluid dynamics in space',
    'physics_params': {
        'entropy': 0.6,
        'warp': 0.4,
        'luminosity': 0.7,
        'cosmic_flow': 0.9,  # High flow rate
        'pattern_collapse': 0.2,
        'attraction': 0.5,
        'uncertainty': 0.5,
        'spectral_shift': 0.6
    }
}
```

---

## 🗺️ Universe Mode

Universe Mode is CosArt's **killer feature** - a 3D navigation system through GAN latent space.

### How It Works

1. **Pre-computation**: 10,000 latent codes are sampled and reduced to 3D using PCA
2. **Spatial Index**: KD-tree enables fast nearest-neighbor queries
3. **Constellation Discovery**: K-means clustering identifies 12 cosmic regions
4. **Real-time Navigation**: Users explore the space and generate artwork at any position

### Key Features

- **3D Coordinates**: Each point in [-1, 1]³ cube represents a unique artwork
- **Constellations**: Named clusters (e.g., "Nebula Prime", "Black Hole Basin")
- **Wormholes**: Fast travel between distant regions
- **Quantum Drift**: Automated random walk exploration

### Usage

```python
# Navigate to a position
response = requests.get('http://localhost:8000/api/universe/navigate', params={
    "x": 0.5, "y": 0.5, "z": 0.5, "radius": 0.3
})

# Find nearby constellations
nearby_constellations = response.json()['navigation_hints']

# Create a wormhole path
path = universe_navigator.create_wormhole(
    pos1=(0.0, 0.0, 0.0),
    pos2=(0.8, 0.8, 0.8),
    steps=20
)
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   React Frontend│
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│  FastAPI Server │
│   (Port 8000)   │
├─────────────────┤
│ - Generation    │
│ - Universe Mode │
│ - WebSocket     │
└────────┬────────┘
         │
    ┌────┴────┬────────┐
    │         │        │
┌───▼───┐ ┌──▼──┐ ┌──▼───┐
│ Redis │ │ GPU │ │ DB   │
│ Cache │ │ GAN │ │ Meta │
└───────┘ └─────┘ └──────┘
```

### Directory Structure

```
cosart/
├── api/                     # FastAPI application
│   ├── main.py             # Main API server
│   └── routes/             # API endpoints
├── models/                  # GAN implementations
│   └── cosmic_stylegan.py  # Cosmic StyleGAN2
├── inference/              # Generation logic
│   ├── generator.py        # Art generator
│   └── universe_builder.py # Universe navigator
├── cosmic/                 # Cosmic features
│   ├── presets.py          # Preset definitions
│   └── physics_mapper.py   # Physics controls
├── utils/                  # Utilities
│   └── image_processing.py # Image utils
├── config/                 # Configuration
│   └── settings.py         # App settings
├── frontend/               # React frontend
│   └── src/
│       └── App.jsx         # Main UI
└── tests/                  # Test suite
```

---

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_generator.py -v

# With coverage
pytest --cov=cosart tests/
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

### Adding New Presets

1. Edit `cosmic/presets.py`
2. Add preset definition to `CosmicPresets.presets`
3. Test with API call
4. Update documentation

### Training Custom Models

```python
# Start training (via API)
response = requests.post('http://localhost:8000/api/train/custom', 
    files={'dataset': open('my_cosmic_images.zip', 'rb')},
    data={
        'name': 'my_cosmic_style',
        'base_model': 'cosmic_base',
        'epochs': 100
    }
)
```

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose up -d --scale cosart-api=3
```

### Cloud Deployment (AWS Example)

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag cosart:latest <account>.dkr.ecr.us-east-1.amazonaws.com/cosart:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/cosart:latest

# Deploy to ECS or EKS
# (Configuration files in /deploy directory)
```

### Environment Variables (Production)

```bash
# Security
SECRET_KEY=<generate-secure-key>
JWT_SECRET=<generate-secure-key>

# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/cosart

# Storage
CLOUD_STORAGE_BUCKET=cosart-prod-models

# Performance
MAX_MODELS_IN_MEMORY=5
GPU_MEMORY_FRACTION=0.9
```

---

## 📈 Performance

### Benchmarks

| Resolution | Time (GPU) | Time (CPU) | Memory |
|-----------|-----------|-----------|---------|
| 512x512 | ~0.5s | ~5s | 2GB |
| 1024x1024 | ~1.5s | ~15s | 4GB |
| 2048x2048 | ~5s | ~60s | 8GB |

### Optimization Tips

1. **Enable Mixed Precision**: Set `MIXED_PRECISION=true`
2. **Batch Processing**: Generate multiple images at once
3. **Model Caching**: Keep frequently used models in memory
4. **Redis Caching**: Cache generation results
5. **Use Lower Resolution**: Start with 512x512, upscale later

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- 🎨 New cosmic presets
- 🧪 Model architectures (StyleGAN3, Diffusion)
- 🌐 Frontend improvements
- 📊 Visualization tools
- 🔬 Physics accuracy
- 📖 Documentation
- 🐛 Bug fixes

---

## 📖 Research & Publications

CosArt bridges art and science. Potential research directions:

1. **Physics-Informed GANs**: Using real physics equations in loss functions
2. **Cosmological Data Integration**: Training on NASA/ESA datasets
3. **Latent Space Topology**: Studying the structure of the "universe"
4. **Human Perception**: How physics parameters affect aesthetic preferences
5. **Educational Applications**: Teaching physics through art generation

---

## 🎓 Educational Use

CosArt is perfect for:

- **Physics Students**: Visualize abstract concepts
- **Art Students**: Explore generative techniques
- **Computer Science**: Learn GANs and deep learning
- **Interdisciplinary Projects**: Bridge art and science

### Example Assignments

1. "Create a visual representation of entropy"
2. "Generate artwork illustrating gravitational lensing"
3. "Explore how quantum uncertainty affects aesthetics"

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **NASA/ESA**: Public astronomical imagery
- **StyleGAN2 Team**: Original GAN architecture
- **FastAPI**: Modern Python web framework
- **PyTorch**: Deep learning framework
- **The Cosmos**: For endless inspiration

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/cosart/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cosart/discussions)
- **Email**: cosart@example.com
- **Twitter**: [@CosArtPlatform](https://twitter.com/CosArtPlatform)

---

## 🌟 Stargazers

If CosArt inspired you, please ⭐ star the repository!

---

**"Where algorithms dream in constellations and artists become cosmic architects."**

🌌 Built with ❤️ and stardust