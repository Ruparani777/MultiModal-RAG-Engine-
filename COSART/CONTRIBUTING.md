# Contributing to CosArt

Thank you for your interest in contributing to CosArt! 🌌 We welcome contributions from artists, scientists, developers, and cosmic dreamers of all backgrounds.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend development)
- Git
- Docker & Docker Compose (optional)

### Quick Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/cosart.git
cd cosart

# Set up development environment
make install
cp .env.example .env

# Start development
make dev
```

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/yourusername/cosart.git
cd cosart
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# At minimum, set SECRET_KEY for development
```

### 4. Run Tests

```bash
# Run backend tests
pytest tests/ -v

# Run frontend tests
cd frontend && npm test
```

### 5. Start Development Server

```bash
# Start backend (in one terminal)
make run

# Start frontend (in another terminal)
make frontend
```

## 🎯 How to Contribute

### Types of Contributions

- **🐛 Bug Fixes**: Fix issues in the codebase
- **✨ New Features**: Add new functionality
- **🎨 Cosmic Presets**: Create new cosmic art presets
- **📚 Documentation**: Improve docs, tutorials, examples
- **🧪 Tests**: Add or improve test coverage
- **🔬 Research**: Scientific improvements and physics accuracy
- **🎪 Frontend**: UI/UX improvements and new components

### Finding Issues to Work On

1. Check [GitHub Issues](https://github.com/yourusername/cosart/issues) for open tasks
2. Look for issues labeled `good first issue` or `help wanted`
3. Check the [Roadmap](#roadmap) for planned features
4. Join our [Discord](https://discord.gg/cosart) to discuss ideas

### Contribution Workflow

1. **Choose an Issue**: Find or create an issue to work on
2. **Create a Branch**: `git checkout -b feature/your-feature-name`
3. **Make Changes**: Implement your solution
4. **Write Tests**: Add tests for new functionality
5. **Update Docs**: Update documentation if needed
6. **Test Locally**: Ensure everything works
7. **Submit PR**: Create a pull request

## 📝 Development Guidelines

### Code Style

#### Python (Backend)

```python
# Use black for formatting
# Follow PEP 8
# Use type hints
# Write docstrings

def generate_cosmic_art(
    preset: str,
    seed: int,
    physics_params: Dict[str, float]
) -> Dict[str, Any]:
    """
    Generate cosmic artwork with physics-based controls.

    Args:
        preset: Cosmic preset name
        seed: Random seed for reproducibility
        physics_params: Physics parameter dictionary

    Returns:
        Dictionary containing generated images and metadata
    """
    pass
```

#### JavaScript/React (Frontend)

```javascript
// Use ESLint and Prettier
// Follow React best practices
// Use functional components with hooks
// Write meaningful component names

const CosmicGenerator = ({ preset, onGenerate }) => {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await onGenerate(preset);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="cosmic-generator">
      {/* Component JSX */}
    </div>
  );
};
```

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(generation): add black hole preset with accretion disk physics
fix(api): resolve memory leak in batch generation
docs(readme): update installation instructions
```

### Branch Naming

```
feature/description-of-feature
bugfix/issue-description
hotfix/critical-fix
docs/update-documentation
```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=cosart --cov-report=html

# Run specific test
pytest tests/test_generator.py::test_cosmic_generation -v

# Run tests in watch mode
pytest-watch tests/
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests once
npm run test:ci

# Run with coverage
npm run test:coverage
```

### Writing Tests

#### Python Tests

```python
import pytest
from cosart.inference.generator import ArtGenerator

class TestArtGenerator:
    def test_generate_basic(self):
        """Test basic art generation."""
        generator = ArtGenerator()
        result = generator.generate("nebula", seed=42)

        assert "images" in result
        assert len(result["images"]) > 0
        assert result["metadata"]["seed"] == 42

    def test_physics_params_validation(self):
        """Test physics parameter validation."""
        generator = ArtGenerator()

        # Valid parameters
        valid_params = {"entropy": 0.5, "warp": 0.3}
        result = generator.generate("nebula", physics_params=valid_params)
        assert result["success"] is True

        # Invalid parameters
        invalid_params = {"entropy": 1.5}  # Out of range
        with pytest.raises(ValueError):
            generator.generate("nebula", physics_params=invalid_params)
```

#### React Tests

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import CosmicGenerator from './CosmicGenerator';

describe('CosmicGenerator', () => {
  it('renders generate button', () => {
    render(<CosmicGenerator preset="nebula" onGenerate={() => {}} />);
    expect(screen.getByText('Generate')).toBeInTheDocument();
  });

  it('calls onGenerate when button is clicked', () => {
    const mockOnGenerate = jest.fn();
    render(<CosmicGenerator preset="nebula" onGenerate={mockOnGenerate} />);

    fireEvent.click(screen.getByText('Generate'));
    expect(mockOnGenerate).toHaveBeenCalledWith('nebula');
  });
});
```

## 📤 Submitting Changes

### Pull Request Process

1. **Ensure Tests Pass**: All tests must pass locally
2. **Update Documentation**: Update README, API docs, etc. if needed
3. **Write Clear Description**: Explain what your PR does
4. **Reference Issues**: Link to related issues with `Closes #123`
5. **Request Review**: Tag maintainers for review

### PR Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Screenshots (if applicable)
Add screenshots of UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🌟 Adding Cosmic Presets

CosArt thrives on community-created presets! Here's how to add one:

### 1. Create Preset Definition

Add to `cosmic/presets.py`:

```python
"cosmic_ocean": {
    'name': '🌊 Cosmic Ocean',
    'description': 'Fluid dynamics in deep space',
    'physics_params': {
        'entropy': 0.6,
        'warp': 0.4,
        'luminosity': 0.7,
        'cosmic_flow': 0.9,
        'pattern_collapse': 0.2,
        'attraction': 0.5,
        'uncertainty': 0.5,
        'spectral_shift': 0.6
    },
    'tags': ['fluid', 'space', 'dynamic']
}
```

### 2. Test the Preset

```python
# Test with API
response = requests.post('http://localhost:8000/api/generate', json={
    "preset": "cosmic_ocean",
    "seed": 12345
})
```

### 3. Add Documentation

Update the README with your new preset in the cosmic presets section.

## 🎨 Frontend Contributions

### Component Structure

```
frontend/src/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── cosmic/       # Cosmic-specific components
│   └── universe/     # Universe mode components
├── hooks/            # Custom React hooks
├── utils/            # Frontend utilities
└── styles/           # CSS and styling
```

### State Management

Use Zustand for global state:

```javascript
// stores/useGenerationStore.js
import create from 'zustand';

const useGenerationStore = create((set) => ({
  isGenerating: false,
  currentGeneration: null,
  setGenerating: (generating) => set({ isGenerating: generating }),
  setCurrentGeneration: (generation) => set({ currentGeneration: generation }),
}));
```

## 🔬 Research Contributions

### Physics Accuracy

When contributing physics-related features:

1. **Cite Sources**: Reference scientific papers
2. **Validate Equations**: Ensure mathematical correctness
3. **Test Edge Cases**: Verify behavior at extremes
4. **Document Assumptions**: Explain simplifications made

### Example: Adding New Physics Parameter

```python
# In physics_mapper.py
@dataclass
class PhysicsParams:
    # Existing parameters...
    new_param: float = Field(default=0.5, ge=0.0, le=1.0)

    def apply_new_param(self, latent: torch.Tensor) -> torch.Tensor:
        """
        Apply new physics parameter to latent space.

        Based on: [Citation to scientific paper]
        """
        # Implementation based on physics equations
        return modified_latent
```

## 📚 Documentation Contributions

### Types of Documentation

- **API Documentation**: Update OpenAPI specs
- **User Guides**: Tutorials and examples
- **Research Papers**: Scientific background
- **Code Comments**: Inline documentation
- **README Updates**: Feature descriptions

### Documentation Standards

- Use clear, concise language
- Include code examples
- Provide context and background
- Keep examples up-to-date
- Use consistent formatting

## 🤗 Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord**: Real-time chat and support
- **Twitter**: Updates and announcements

### Recognition

Contributors are recognized through:
- GitHub contributor statistics
- Mention in release notes
- Featured in community showcases
- Co-authorship on research papers

### Governance

- **Maintainers**: Core team managing the project
- **Contributors**: Community members with merge rights
- **Community**: All users and contributors

## 📄 License

By contributing to CosArt, you agree that your contributions will be licensed under the MIT License.

## 🙏 Acknowledgments

Thank you for contributing to CosArt! Your work helps bridge the gap between art, science, and technology. Together, we're creating something truly cosmic. 🌌

---

**"The best way to predict the future is to create it."**
*- Peter Drucker*