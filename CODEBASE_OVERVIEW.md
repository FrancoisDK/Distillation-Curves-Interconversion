# Distillation Curve Interconversion Codebase Overview

## 🎯 Project Purpose
A comprehensive tool for converting between three petroleum distillation curve standards:
- **ASTM D86**: Distillation test method
- **ASTM D2887**: Simulated distillation (GC-based)
- **TBP**: True Boiling Point (theoretical equilibrium)

---

## 📦 Core Architecture

### Main Components

#### 1. **bp_conversions.py** (719 lines)
Core conversion engine with the `Oil` class.

**Key Features:**
- Multi-directional conversions (D86 ↔ D2887 ↔ TBP)
- Riazi-Daubert power-law correlations for accuracy
- PCHIP interpolation for smooth curves
- Temperature unit conversion (°C, °F, K, °R)
- Petroleum property calculations

**Main Methods:**
```python
Oil.__init__(distillation_input, Density, input_type='D86')
  # Initialize with D86, D2887, or TBP data
  # Automatically creates all 3 interpolators

# Conversion methods:
Oil.API_D86_TBP(d86_data)           # D86 → TBP (API method)
Oil.Daubert_ASTM_D86_TBP(d86_data)  # D86 → TBP (Daubert method)
Oil.D86_to_D2887(d86_data)          # D86 → D2887
Oil.D2887_to_D86(d2887_data)        # D2887 → D86 (Riazi-based)
Oil.D2887_to_TBP_direct(d2887_data) # D2887 → TBP (Riazi-based)

# Property methods:
Oil.VABP_(interpolator)             # Volume Average Boiling Point
Oil.MeABP_(interpolator)            # Mean Average Boiling Point
Oil.WatsonK_()                      # Watson K-factor

# Interpolators (scipy PCHIP):
Oil.D86_interp(volume_percent)      # Get D86 temp at any %
Oil.D2887_interp(volume_percent)
Oil.TBP_interp(volume_percent)
```

**Data Structure:**
```python
distillation_input = [
    [0, 160.0],      # [Volume %, Temperature (°C)]
    [10, 180.5],
    [30, 205.0],
    ...
    [100, 290.0]
]
```

**Standard Points:** IBP (0%), 10%, 30%, 50%, 70%, 90%, 95%, FBP (100%)

---

#### 2. **distillation_converter_gui.py** (1073 lines)
Professional Qt-based GUI application.

**Architecture:**
- `InteractiveTableWidget`: Custom table with clipboard support
- `PlotCanvas`: Matplotlib integration
- `DistillationConverterGUI`: Main application window

**Features:**

**Input Panel:**
- Dropdown to select input type (D86/D2887/TBP)
- Density input (600-1200 kg/m³ validated)
- Basis selection (Volume % or Weight %)
- Data table with 8 standard points pre-populated
- Add/Remove rows for custom points
- Clear all data button

**Conversion Options:**
- ☑ Convert to D86
- ☑ Convert to D2887 (SimDis)
- ☑ Convert to TBP (API method)
- ☑ Convert to TBP (Daubert method)

**Output Display (3 Tabs):**
1. **Plot Tab**
   - Interactive matplotlib figure
   - Multiple curves on single plot
   - Zoom, pan, save toolbar
   - Legend and grid
   - All temperatures in °C

2. **Data Table Tab**
   - Numerical results (IBP, 5%, 10%, 30%, 50%, 70%, 90%, 95%, FBP)
   - All in °C
   - Copyable to clipboard/Excel
   - Professional formatting

3. **Properties Tab**
   - Calculated petroleum properties
   - VABP (Volume Avg Boiling Point) - °F
   - MeABP (Mean Avg Boiling Point) - °C
   - Watson K-factor
   - Density (kg/m³)
   - Specific gravity

**Export:**
- CSV export (full data)
- Excel export (.xlsx with formatting)

---

## 🧪 Conversion Methods

### API D86 → TBP (1993)
**Method:** Linear regression on experimental data
**Equation:** TBP = 0.833 × D86 + 6.75 (approximation)
**Accuracy:** Good for most petroleum cuts
**Use Case:** Standard industrial method

### Daubert D86 → TBP (1994)
**Method:** Temperature-dependent polynomial correlations
**Equation:** Complex multi-parameter fit
**Accuracy:** Better for wide boiling range fractions
**Use Case:** More precise calculations

### Riazi-Daubert D2887 ↔ D86
**Method:** Power-law correlation (physics-based)
**Equation:** `T_R = a × (T_R')^b` (Rankine temperatures)
**Key Insight:** D86 is ~3-7°C lower than D2887 (heat loss effects)
**Validation Range:** Kerosene/diesel (160-290°C)

**Coefficients Table** (Volume % basis):
```
D2887 → D86:
Vol %    a       b       ΔT (°C)
0        0.9965  0.9985  5-6
10       0.9970  0.9988  4-5
30       0.9975  0.9990  3-4
50       0.9977  0.9992  3-4
70       0.9975  0.9990  3.5-4.5
90       0.9968  0.9986  5-7
100      0.9960  0.9982  6-8
```

### Riazi D2887 → TBP
**Correlation:** Similar power-law structure
**Key Insight:** TBP is ~0.5-2.0°C higher than D2887
**Reason:** D2887 is GC-based with VLE correction; TBP is theoretical equilibrium

---

## 📊 Data Validation Rules

1. **Minimum Points:** At least 3 distillation points
2. **Temperature Monotonicity:** Must be strictly increasing
3. **Density Range:** 600-1200 kg/m³
4. **Physical Order:** D86 < D2887 < TBP (always)
5. **Interpolation:** PCHIP ensures smooth, non-oscillating curves

---

## 🔄 Workflow Example

```python
from bp_conversions import Oil

# Input: D2887 data for kerosene
d2887_data = [
    [0, 160.0],
    [10, 180.5],
    [30, 205.0],
    [50, 225.0],
    [70, 245.0],
    [90, 270.0],
    [100, 290.0]
]

# Create Oil object (automatically converts to all 3 types)
oil = Oil(d2887_data, Density=820, input_type='D2887')

# Get temperature at any point
d86_at_50pct = oil.D86_interp(50)      # ~221°C
d2887_at_50pct = oil.D2887_interp(50)  # ~225°C
tbp_at_50pct = oil.TBP_interp(50)      # ~225.5°C

# Get properties
print(f"VABP: {oil.VABP}°F")    # Volume Average Boiling Point
print(f"MeABP: {oil.MeABP}°C")  # Mean Average Boiling Point
print(f"Watson K: {oil.WatsonK}")
```

---

## 📁 File Structure

```
Distillation_Curve_interconv/
│
├── bp_conversions.py                    # Core conversion engine
├── distillation_converter_gui.py        # Qt GUI application
├── test_riazi_methods.py               # Validation tests for Riazi correlations
├── analyze_curve_differences.py        # Analysis/comparison tools
├── debug_*.py                          # Development debug scripts
│
├── README_DISTILLATION.md              # Comprehensive documentation
├── GUI_USER_GUIDE.md                   # User guide for GUI
├── QUICK_START.md                      # 5-minute quickstart
├── RIAZI_IMPLEMENTATION.md             # Correlation technical details
├── D2887_CONVERSION_NOTES.md           # D2887 method specifics
├── DEVELOPMENT_SUMMARY.md              # Feature overview
│
├── Kero D86.csv                        # Sample kerosene D86 data
├── D86 Distillation.csv               # Sample D86 data
├── example.csv                         # Example export
├── example.xlsx                        # Example Excel export
│
├── pyproject.toml                      # Project dependencies (Python 3.12+)
├── uv.lock                             # Lock file for dependency versions
└── .python-version                     # Python version specification
```

---

## 🛠️ Dependencies

```toml
matplotlib >= 3.10.7   # Plotting & visualization
scipy >= 1.16.2       # Scientific computing (PCHIP interpolation)
PySide6 >= 6.10.0     # Qt6 GUI framework
pandas >= 2.3.3       # Data manipulation
openpyxl >= 3.1.5     # Excel file writing
```

**Python Version:** 3.12+

---

## 🚀 Quick Start

### Running the GUI
```bash
python distillation_converter_gui.py
```

### Using as a Library
```python
from bp_conversions import Oil

# Create Oil object with D86 data
d86_data = [[0, 160], [50, 225], [100, 290]]
oil = Oil(d86_data, Density=820, input_type='D86')

# Access conversions
d2887_temp = oil.D2887_interp(50)
tbp_temp = oil.TBP_interp(50)
```

### Running Tests
```bash
python test_riazi_methods.py
```

---

## 🔑 Key Concepts

### Distillation Curve Types

| Method | Type | Basis | Pressure | Notes |
|--------|------|-------|----------|-------|
| **D86** | ASTM | Experimental distillation | 101.3 kPa | Heat loss effects, ~3-7°C lower than true boiling |
| **D2887** | ASTM | Simulated (GC-based) | Virtual | Lab standard, faster, reproducible |
| **TBP** | Theoretical | True boiling point | Vapor pressure | Equilibrium basis, 15/5 rectification |

### Why Conversions Matter
- Industry uses different methods
- Design engineers need TBP for process simulation
- Analytical labs report D2887 (SimDis)
- Legacy data in D86 format
- Conversions enable comparison and compatibility

### Temperature Order (Always)
```
D86 < D2887 < TBP
 ↓     ↓      ↓
Heat  VLE    Perfect
loss  corr   equilibrium
```

---

## 📈 Recent Development History

- **Phase 1:** Core D86 ↔ TBP conversions (API, Daubert methods)
- **Phase 2:** Added D86 ↔ D2887 conversion (Riazi-based)
- **Phase 3:** GUI development with Qt/PySide6
- **Phase 4:** Riazi correlation refinement & validation
- **Phase 5:** Documentation suite & export features

---

## 💡 Development Notes

### Testing Strategy
- **test_riazi_methods.py:** Validates Riazi correlations with known kerosene data
- **analyze_curve_differences.py:** Compares API vs Daubert TBP methods
- **debug_* scripts:** Development-stage testing

### Key Validation Points
1. ✅ D86 < D2887 < TBP order maintained
2. ✅ Temperature differences within physical ranges
3. ✅ Smooth interpolation (no oscillations)
4. ✅ Property calculations (VABP, MeABP, K-factor)
5. ✅ Unit conversions accurate

### Known Limitations
- Correlations validated for kerosene/diesel range (160-300°C)
- Not tested on very light (gasoline) or very heavy (fuel oil) cuts
- Assumes API < 50 (petroleum range)
- Density must be 600-1200 kg/m³

---

## 🎓 References

1. **API Technical Data Book (1993)**
   - D86 to TBP conversion (API method)

2. **Hydrocarbon Processing (1994) - Daubert**
   - Temperature-dependent TBP correlations

3. **Riazi-Daubert Correlations**
   - Power-law relationships (physics-based)
   - Published in petroleum literature

4. **ASTM Standards**
   - ASTM D86: Distillation
   - ASTM D2887: Simulated distillation

---

## 🔗 Next Steps for Contributing

1. **To fix bugs:** Check `debug_*.py` files for known issues
2. **To add features:** Extend `bp_conversions.Oil` class
3. **To improve GUI:** Modify `distillation_converter_gui.py`
4. **To validate:** Run `test_riazi_methods.py` after changes
5. **To document:** Update relevant `.md` files

---

**Last Updated:** November 16, 2025
**Python Version:** 3.12+
**Status:** Active development
