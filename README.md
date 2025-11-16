# Distillation Curve Interconversion

[![PyPI version](https://badge.fury.io/py/distillation-curve-interconv.svg)](https://badge.fury.io/py/distillation-curve-interconv)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Tests](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/workflows/Tests/badge.svg)](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Convert between petroleum distillation standards with physics-based correlations.

**Supports:** D86 (ASTM D86) ↔ D2887 (SimDis) ↔ TBP (True Boiling Point)

## Why Use This?

Different distillation methods are used in different labs and regions. This library converts between them seamlessly using proven Riazi-Daubert correlations.

```python
from bp_conversions import Oil

# Input D86 data
d86_data = [[0, 160], [50, 225], [100, 290]]

# Create Oil object (all conversions automatic)
oil = Oil(d86_data, Density=820, input_type='D86')

# Get conversions at any point
d2887_at_50pct = oil.D2887_interp(50)  # ~228°C
tbp_at_50pct = oil.TBP_interp(50)      # ~253°C

# Get properties
print(f"VABP: {oil.VABP}°F")
print(f"Watson K: {oil.WatsonK:.3f}")
```

## Installation

### From PyPI (Recommended)
```bash
pip install distillation-curve-interconv
```

### With GUI (includes PySide6)
```bash
pip install distillation-curve-interconv[gui]
```

### For Development
```bash
git clone https://github.com/FrancoisDK/Distillation-Curves-Interconversion.git
cd Distillation-Curves-Interconversion
pip install -e ".[dev,gui]"
```

## Quick Start

### Use the GUI
```bash
distillation-gui
```

Or directly:
```bash
python distillation_converter_gui.py
```

### Use the Python API
```python
from bp_conversions import Oil

# Create from D86 data
oil = Oil([[0, 160], [50, 225], [100, 290]], Density=820, input_type='D86')

# Query conversions
d2887_temps = [oil.D2887_interp(v) for v in range(0, 101, 10)]
tbp_temps = [oil.TBP_interp(v) for v in range(0, 101, 10)]

# Export to CSV
import pandas as pd
results = pd.DataFrame({
    'Vol%': range(0, 101, 10),
    'D86_C': [oil.D86_interp(v) for v in range(0, 101, 10)],
    'D2887_C': d2887_temps,
    'TBP_C': tbp_temps,
})
results.to_csv('conversions.csv', index=False)
```

### Try the Jupyter Tutorial
```bash
jupyter notebook examples/tutorial.ipynb
```

## Key Features

✅ **Multi-directional Conversion**
- D86 → D2887, TBP
- D2887 → D86, TBP  
- TBP → D86, D2887

✅ **Physics-Based Correlations**
- Riazi-Daubert power-law equations
- Temperature-dependent coefficients
- Validated against industry standards

✅ **Professional GUI**
- Interactive plotting
- Real-time conversions
- CSV/Excel export
- Copy/paste from Excel

✅ **Complete Python API**
- Simple Oil class interface
- Smooth PCHIP interpolation
- Property calculations (VABP, MeABP, Watson K)
- Temperature unit conversions

✅ **Well Tested**
- 50+ unit tests
- CI/CD on Windows, macOS, Linux
- Python 3.12+ support

## Physical Relationships

The library enforces fundamental thermodynamic relationships:

```
D86 < D2887 < TBP  (Always)

- D86: 3-7°C lower (heat losses in ASTM method)
- D2887: Middle (GC-based SimDis method)
- TBP: 0.5-2°C higher (theoretical equilibrium)
```

## Supported Temperature Range

- **Typical:** 160-320°C (D86)
- **Validated:** Kerosene, diesel, light crude oils
- **Density range:** 600-1200 kg/m³

## Data Format

Input data should be a list of [volume%, temperature] pairs:

```python
data = [
    [0, 160],      # IBP (Initial Boiling Point)
    [10, 172],
    [30, 192],
    [50, 225],
    [70, 260],
    [90, 280],
    [100, 290]     # FBP (Final Boiling Point)
]
```

**Requirements:**
- Minimum 3 points
- Temperatures strictly increasing
- Volume percentages 0-100% inclusive
- Density: 600-1200 kg/m³

## API Reference

### Oil Class

```python
Oil(distillation_input, Density, input_type='D86')
```

**Parameters:**
- `distillation_input` (list): [[vol%, temp], ...] pairs
- `Density` (float): kg/m³ (required for properties)
- `input_type` (str): 'D86', 'D2887', or 'TBP'

**Methods:**
- `D86_interp(vol_pct)` → temperature °C
- `D2887_interp(vol_pct)` → temperature °C
- `TBP_interp(vol_pct)` → temperature °C
- `Daubert_TBP_interp(vol_pct)` → temperature °C (alternative)
- `convert_temperature(value, from_unit, to_unit)` → converted temperature

**Properties:**
- `.VABP` → °F (Volume Average Boiling Point)
- `.MeABP` → °C (Mean Average Boiling Point)
- `.WatsonK` → dimensionless (Characterization factor)
- `.Density` → kg/m³
- `.D86`, `.D2887`, `.TBP` → raw data lists

## Examples

### Round-Trip Conversion
```python
# D86 → D2887 → D86 (test round-trip accuracy)
oil1 = Oil([[0, 160], [50, 225], [100, 290]], 820, 'D86')
d2887_data = [[v, oil1.D2887_interp(v)] for v in [0, 50, 100]]
oil2 = Oil(d2887_data, 820, 'D2887')
d86_back = [oil2.D86_interp(v) for v in [0, 50, 100]]
```

### Batch Processing
```python
import pandas as pd
from pathlib import Path

# Process all CSV files in directory
for csv_file in Path('data/').glob('*.csv'):
    df = pd.read_csv(csv_file)
    oil = Oil(df[['Vol%', 'TempC']].values.tolist(), 820, 'D86')
    
    # Save results
    output = pd.DataFrame({
        'Vol%': range(0, 101, 10),
        'D2887_C': [oil.D2887_interp(v) for v in range(0, 101, 10)],
        'TBP_C': [oil.TBP_interp(v) for v in range(0, 101, 10)],
    })
    output.to_csv(f'converted/{csv_file.stem}_converted.csv', index=False)
```

### Compare Multiple Oils
```python
samples = {
    'Light Crude': Oil([[0, 155], [50, 220], [100, 285]], 750, 'D86'),
    'Medium Crude': Oil([[0, 160], [50, 225], [100, 290]], 820, 'D86'),
    'Heavy Crude': Oil([[0, 170], [50, 235], [100, 305]], 900, 'D86'),
}

for name, oil in samples.items():
    print(f"{name}: VABP={oil.VABP}°F, K={oil.WatsonK:.3f}")
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test class
pytest tests/test_bp_conversions.py::TestConversionPhysics -v
```

## Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Onboarding guide (15 min)
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - API reference (5 min)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep-dive
- **[examples/tutorial.ipynb](examples/tutorial.ipynb)** - Interactive Jupyter notebook
- **[GUI_USER_GUIDE.md](GUI_USER_GUIDE.md)** - GUI documentation

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setup instructions
- Testing guidelines
- Code style requirements
- Pull request process

### Quick Contribution Areas
- 🐛 Bug fixes
- ✨ New conversion methods
- 📚 Documentation improvements
- 🧪 Additional test cases
- 🎯 GUI enhancements

## Technical Details

### Riazi-Daubert Correlations

The library uses proven power-law correlations for conversions:

**D86 to D2887:**
```
T_D2887 = T_D86 + a·(vol%)^b + c·(vol%)^d
```

**D2887 to TBP:**
```
T_TBP = T_D2887 + e·(vol%)^f + g·(vol%)^h
```

Coefficients are temperature-dependent and validated against:
- ASTM standards
- API technical literature
- Published industry data

### Interpolation

Uses PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) from scipy:
- Monotonic between data points
- No overshooting oscillations
- Smooth first derivative

## Limitations

- **Validated for:** 160-320°C range (kerosene/diesel)
- **Density range:** 600-1200 kg/m³
- **Minimum points:** 3 (8 recommended)
- **Assumption:** Standard atmospheric pressure

For crude oils outside this range, accuracy may decrease. Heavy vacuum distillates are not supported.

## Troubleshooting

### Curves crossing (D86 > D2887 or D2887 > TBP)
Check data monotonicity:
```python
# Temperatures should be strictly increasing
temps = [p[1] for p in data]
assert all(temps[i] < temps[i+1] for i in range(len(temps)-1))
```

### Results seem wrong
Verify:
1. Input data is correct (check original lab report)
2. Density is reasonable (600-1200 kg/m³)
3. Temperature range is within 160-320°C
4. No duplicate temperature values

### GUI won't start
Ensure PySide6 is installed:
```bash
pip install distillation-curve-interconv[gui]
```

## References

1. Riazi, M. R., & Daubert, T. E. (1987). Characterization of petroleum fractions. Industrial & Engineering Chemistry Research, 26(4), 755-759.

2. ASTM D86-23: Standard test method for distillation of petroleum products at atmospheric pressure

3. ASTM D2887-19: Standard test method for boiling range distribution of petroleum fractions by gas chromatography

4. API Technical Report 582 (2015): Crude oil properties correlation

## License

MIT License - see [LICENSE](LICENSE) for details

## Citation

If you use this library in academic work, please cite:

```bibtex
@software{distillation_curves_2025,
  title = {Distillation Curve Interconversion},
  author = {François, D. K.},
  year = {2025},
  url = {https://github.com/FrancoisDK/Distillation-Curves-Interconversion},
}
```

## Support

- 📖 **Documentation:** See docs/ directory
- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/discussions)
- 📧 **Email:** For sensitive inquiries

## Changelog

### v0.2.0 (2025-11-16)
- ✨ Official PyPI package release
- 🧪 50+ comprehensive unit tests
- 🔄 GitHub Actions CI/CD
- 📚 Complete documentation suite
- 📓 Jupyter tutorial notebook
- 🤝 Contributing guidelines

### v0.1.0 (Initial)
- Core conversion engine
- GUI application
- D86 ↔ D2887 ↔ TBP support

---

**Made with ❤️ for chemical engineers and petroleum scientists**
