# Quick Reference Guide - Distillation Curve Interconversion

## 🎯 What This Project Does

Converts petroleum distillation data between three industry-standard formats:
- **D86** ← → **D2887** ← → **TBP**

### Why It Matters
Different labs/industries use different testing methods. This tool lets you convert between them for process design, simulation, and data comparison.

---

## 🚀 Fastest Way to Use It

### Option 1: GUI (Easiest)
```bash
python distillation_converter_gui.py
```
1. Select input type (D86/D2887/TBP)
2. Enter density (kg/m³)
3. Paste/type your data points
4. Click "Convert"
5. View plots and export results

### Option 2: Python Code (Most Flexible)
```python
from bp_conversions import Oil

# Your data: [Volume %, Temperature (°C)]
data = [
    [0, 160],     # IBP
    [50, 225],    # 50% point
    [100, 290]    # FBP
]

# Create Oil object
oil = Oil(data, Density=820, input_type='D86')

# Get conversions at any point
print(f"D2887 at 50%: {oil.D2887_interp(50):.1f}°C")
print(f"TBP at 50%:   {oil.TBP_interp(50):.1f}°C")

# Get properties
print(f"VABP: {oil.VABP}°F")
print(f"K-factor: {oil.WatsonK:.3f}")
```

---

## 📋 Core Classes & Methods

### Oil Class
```python
Oil(distillation_input, Density, input_type='D86')
```

**Parameters:**
- `distillation_input` (list): [[vol%, temp], [vol%, temp], ...]
- `Density` (float): kg/m³ (600-1200 valid range)
- `input_type` (str): 'D86', 'D2887', or 'TBP'

**Interpolators (return temperature in °C):**
```python
oil.D86_interp(volume_percent)      # Get D86 temp
oil.D2887_interp(volume_percent)    # Get D2887 temp
oil.TBP_interp(volume_percent)      # Get TBP temp
```

**Properties:**
```python
oil.VABP              # Volume Average Boiling Point (°F)
oil.MeABP             # Mean Average Boiling Point (°C)
oil.WatsonK           # Watson K-factor (characterization)
oil.Density           # Density (kg/m³)
```

---

## 📊 Data Format

### Input Format (Required)
```python
distillation_data = [
    [0, 160.0],      # [Volume %, Temperature (°C)]
    [10, 180.5],
    [30, 205.0],
    [50, 225.0],
    [70, 245.0],
    [90, 270.0],
    [100, 290.0]     # Must end at 100%
]
```

### Standard Points
Commonly used 8-point spread:
- IBP (0%)
- 5%, 10%, 30%, 50%, 70%, 90%, 95%
- FBP (100%)

**Minimum:** 3 points required
**Ordering:** Must be strictly increasing in both % and temperature

---

## 🔄 Conversion Methods

### Available Conversions
```
D86 → TBP    [API method or Daubert method]
D86 → D2887  [Riazi-based]
D2887 → D86  [Riazi-based, inverse]
D2887 → TBP  [Riazi-based]
TBP → D86    [Inverse correlations]
```

### Temperature Relationships (Always True)
```
D86 < D2887 < TBP
```

**Typical Differences (at 50% point):**
- D86 is 3-5°C LOWER than D2887
- TBP is 0.5-2.0°C HIGHER than D2887

---

## 🎛️ GUI Guide

### Input Panel
| Field | Purpose | Valid Range |
|-------|---------|-------------|
| Input Type | Choose D86/D2887/TBP | Dropdown |
| Density | Oil density | 600-1200 kg/m³ |
| Basis | Vol % or Wt % | Radio button |
| Data Table | Distillation points | Min 3 points |

### Actions
- **Add Point:** New row for custom point
- **Remove:** Delete selected row
- **Clear All:** Reset all data

### Conversion Options
- ☑ D86: Convert to ASTM D86
- ☑ D2887: Convert to SimDis
- ☑ TBP (API): API method
- ☑ TBP (Daubert): Daubert method

### Output Tabs
1. **Plot:** Interactive curves (zoom/pan/save)
2. **Data:** Numeric table at 8 standard points
3. **Properties:** Calculated VABP, MeABP, K-factor

### Export
- **CSV:** Spreadsheet-friendly format
- **Excel:** .xlsx with formatting

---

## 🧮 Common Formulas

### Temperature Conversions
```
Rankine (R) = Celsius (C) + 273.15 + 459.67
           = Fahrenheit (F) + 459.67
```

### Key Properties
```
VABP = Weighted average of distillation temperatures (volume basis)
MeABP = Arithmetic mean of distillation temperatures
Watson K = (Boiling Point)^(1/3) / Density   [Characterization factor]
```

---

## ⚠️ Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Need at least 3 points" | Too few data points | Add more distillation points |
| "Temperatures not increasing" | Out-of-order data | Sort by temperature (ascending) |
| "Density out of range" | Invalid density | Check range: 600-1200 kg/m³ |
| "Curves cross" | Data inconsistency | Verify input data accuracy |

---

## 📈 Example Workflow

### Step 1: Prepare Data
```python
kero_d2887 = [
    [0, 160.0],
    [10, 180.5],
    [30, 205.0],
    [50, 225.0],
    [70, 245.0],
    [90, 270.0],
    [100, 290.0]
]
density = 820  # kg/m³
```

### Step 2: Create Oil Object
```python
oil = Oil(kero_d2887, density, input_type='D2887')
```

### Step 3: Access Results
```python
# Get specific conversions
d86_mid = oil.D86_interp(50)        # ~221°C
tbp_mid = oil.TBP_interp(50)        # ~225.5°C

# Get properties
print(f"VABP: {oil.VABP}°F")
print(f"K-factor: {oil.WatsonK:.3f}")

# Export full table
for vol in [0, 10, 30, 50, 70, 90, 100]:
    print(f"{vol}%: D86={oil.D86_interp(vol):.1f}, "
          f"D2887={oil.D2887_interp(vol):.1f}, "
          f"TBP={oil.TBP_interp(vol):.1f}")
```

### Step 4: Save Results
```python
# Use GUI to export to CSV/Excel, or
# Manual export with pandas:
import pandas as pd

data = {
    'Volume_%': [0, 10, 30, 50, 70, 90, 100],
    'D86_C': [oil.D86_interp(v) for v in [0, 10, 30, 50, 70, 90, 100]],
    'D2887_C': [oil.D2887_interp(v) for v in [0, 10, 30, 50, 70, 90, 100]],
    'TBP_C': [oil.TBP_interp(v) for v in [0, 10, 30, 50, 70, 90, 100]]
}
df = pd.DataFrame(data)
df.to_csv('conversions.csv', index=False)
```

---

## 🔍 File Reference

| File | Purpose | Usage |
|------|---------|-------|
| `bp_conversions.py` | Core engine | `from bp_conversions import Oil` |
| `distillation_converter_gui.py` | GUI app | `python distillation_converter_gui.py` |
| `test_riazi_methods.py` | Validation | `python test_riazi_methods.py` |
| `analyze_curve_differences.py` | Analysis | Development/debugging |
| `RIAZI_IMPLEMENTATION.md` | Correlation details | Technical reference |
| `GUI_USER_GUIDE.md` | GUI help | User documentation |

---

## 🎓 Learning Path

1. **Read:** This quick reference (you're here!)
2. **Explore:** RIAZI_IMPLEMENTATION.md for technical details
3. **Try GUI:** `python distillation_converter_gui.py`
4. **Use Code:** Create Oil object with your data
5. **Reference:** GUI_USER_GUIDE.md for advanced features

---

## 💡 Tips & Tricks

### Fastest Conversions
```python
# One-liner
oil = Oil(your_data, 820, 'D86')
d2887_curve = [oil.D2887_interp(v) for v in range(0, 101, 10)]
```

### Working with CSV Files
```python
import pandas as pd
df = pd.read_csv('my_distillation.csv')
data = df[['Volume_%', 'Temp_C']].values.tolist()
oil = Oil(data, 820, 'D86')
```

### Batch Processing
```python
oils = {}
for name, data in [('crude1', data1), ('crude2', data2)]:
    oils[name] = Oil(data, 820, 'D86')

# Compare
for name, oil in oils.items():
    print(f"{name}: VABP={oil.VABP}°F, K={oil.WatsonK:.3f}")
```

---

## 🆘 Getting Help

1. **GUI not starting?** Check PySide6 installation: `pip install PySide6>=6.10.0`
2. **Import errors?** Ensure scipy installed: `pip install scipy>=1.16.2`
3. **Data issues?** Validate with `test_riazi_methods.py`
4. **Conversion questions?** See RIAZI_IMPLEMENTATION.md

---

## 📞 Quick Facts

- **Minimum data points:** 3
- **Valid density range:** 600-1200 kg/m³
- **Temperature units:** Input °C, output °C (VABP in °F)
- **Interpolation method:** PCHIP (smooth, non-oscillating)
- **Tested range:** Kerosene/diesel (160-290°C)
- **Python version:** 3.12+

---

**Version:** 1.0
**Last Updated:** November 16, 2025
**Status:** Ready to use
