# 📚 You Are Now Up to Speed: Distillation Curve Interconversion

## ✅ What You Just Learned

You now understand:

1. **What the project does:** Converts between 3 petroleum distillation standards (D86 ↔ D2887 ↔ TBP)
2. **Why it matters:** Different labs use different methods; conversions enable compatibility
3. **How it works:** Uses physics-based Riazi-Daubert correlations (power-law equations)
4. **Architecture:** Input → normalize to D86 → apply correlations → get all 3 curves
5. **Core class:** `Oil` from `bp_conversions.py` does all conversions automatically

---

## 🎯 Essential Quick Facts

| Aspect | Detail |
|--------|--------|
| **Main Class** | `Oil` (bp_conversions.py) |
| **Core Methods** | Riazi-Daubert power-law correlations |
| **Temperature Units** | Input/output °C, internal Rankine |
| **Data Format** | `[[vol%, temp], [vol%, temp], ...]` |
| **Min Points** | 3 (standard 8 recommended) |
| **Order (Always)** | D86 < D2887 < TBP |
| **Typical Diffs** | D86 is 3-7°C lower, TBP is 0.5-2°C higher |

---

## 🚀 How to Use in 30 Seconds

```python
from bp_conversions import Oil

# Input data (volume %, temperature in °C)
data = [[0, 160], [50, 225], [100, 290]]

# Create Oil object (1 line!)
oil = Oil(data, Density=820, input_type='D86')

# Get conversions anywhere on curve
d2887_at_50pct = oil.D2887_interp(50)  # ~228°C
tbp_at_50pct = oil.TBP_interp(50)      # ~253°C

# Get properties
print(f"VABP: {oil.VABP}°F")
print(f"K-factor: {oil.WatsonK}")
```

---

## 📂 File Guide

### Core Code
- **bp_conversions.py** (719 lines) - The entire conversion engine
  - `Oil` class with all methods
  - Temperature conversions
  - Property calculations
  
- **distillation_converter_gui.py** (1073 lines) - Qt GUI application
  - `InteractiveTableWidget` - Data entry table
  - `PlotCanvas` - Matplotlib integration
  - `DistillationConverterGUI` - Main window
  - Full UI with plots, tables, properties, export

### Testing & Analysis
- **test_riazi_methods.py** - Validates Riazi correlations
- **analyze_curve_differences.py** - Compares conversion methods
- **debug_*.py** - Development scripts

### Documentation (You'll Want These!)
1. **CODEBASE_OVERVIEW.md** (NEW) ← Architecture & architecture guide
2. **QUICK_REFERENCE.md** (NEW) ← Fast lookup
3. **ARCHITECTURE.md** (NEW) ← Data flows & diagrams
4. **RIAZI_IMPLEMENTATION.md** - Technical correlation details
5. **GUI_USER_GUIDE.md** - GUI help
6. **README_DISTILLATION.md** - Project overview

---

## 🧠 Mental Model

```
Think of it like currency conversion:

"I have USD data, but I need EUR and GBP"

Oil class does the same for distillation:

"I have D86 data, but I need D2887 and TBP"

Oil instance = your converter
  • Store input in any format
  • Get output in any format
  • Properties calculated automatically
```

---

## 🔑 5 Key Methods You'll Use

1. **Create Oil object**
   ```python
   oil = Oil(data, density, input_type)
   ```
   Creates all 3 interpolators in one go

2. **Get temperature at any %**
   ```python
   d86_temp = oil.D86_interp(50)      # °C at 50%
   d2887_temp = oil.D2887_interp(50)
   tbp_temp = oil.TBP_interp(50)
   ```

3. **Get properties**
   ```python
   oil.VABP      # °F
   oil.MeABP     # °C
   oil.WatsonK   # Dimensionless
   ```

4. **Temperature conversion**
   ```python
   celsius = oil.convert_temperature(100, 'F', 'C')
   ```

5. **Use GUI**
   ```bash
   python distillation_converter_gui.py
   ```

---

## 📊 The Conversion Chain

```
Input Data (Any type: D86, D2887, or TBP)
         ↓
    Detect Type
         ↓
    Convert to D86 (if needed)
         ↓
    Apply 3 Correlation Methods:
    • D86 (baseline, no conversion)
    • D2887 (Riazi power-law)
    • TBP (API or Daubert method)
         ↓
    Create 3 PCHIP Interpolators
    (Smooth curves through all points)
         ↓
    Ready to Query: oil.D86_interp(%), oil.D2887_interp(%), etc.
         ↓
    Calculate Properties: VABP, MeABP, Watson K
         ↓
    Output: Curves, Tables, Export, or Python access
```

---

## 🎓 Understanding the Correlations

### Why They Exist
Different distillation methods measure the same product differently:
- **D86:** Direct heating → some heat loss → measured temps are ~5°C LOWER
- **D2887:** GC-based simulation → no heat loss → "true" temps
- **TBP:** Theoretical equilibrium → perfectly efficient → slightly HIGHER temps

### The Order (Physics)
```
D86 < D2887 < TBP  (Always, at every point)

Examples at 50% point:
D86 = 220°C
D2887 = 225°C  (≈5°C higher than D86)
TBP = 226°C    (≈1°C higher than D2887)
```

### Why Riazi Formulas
```
Power-law correlations are more accurate than simple offsets because:
1. Physically justified (empirical from large data sets)
2. Account for varying pressure effects
3. Different coefficients for different % points
4. Non-linear relationships
```

---

## ⚠️ Important Constraints

- **Minimum points:** 3 (more is better, 8 is typical)
- **Density range:** 600-1200 kg/m³ (typical oils)
- **Temperature:** Strictly increasing, no duplicates
- **Volume %:** Must go 0% → 100%
- **Validated for:** Kerosene/diesel (160-290°C)

---

## 🎯 Common Tasks

### Task: Convert my D86 data to D2887
```python
d86_data = [[0, 160], [50, 225], [100, 290]]
oil = Oil(d86_data, 820, 'D86')
d2887_curve = [oil.D2887_interp(v) for v in range(0, 101, 10)]
```

### Task: Read CSV, convert, export
```python
import pandas as pd
df = pd.read_csv('my_data.csv')
data = df[['Vol%', 'TempC']].values.tolist()
oil = Oil(data, 820, 'D86')
# Use GUI to export, or manual:
results = [[v, oil.D86_interp(v), oil.D2887_interp(v)] 
           for v in range(0, 101, 10)]
```

### Task: Compare two oils
```python
oils = {
    'crude1': Oil(data1, 820, 'D86'),
    'crude2': Oil(data2, 850, 'D86')
}
for name, oil in oils.items():
    print(f"{name}: VABP={oil.VABP}°F, K={oil.WatsonK:.3f}")
```

---

## 🔍 What Each File Does

| File | Purpose | When to Use |
|------|---------|-------------|
| `bp_conversions.py` | Core engine | Always (imported by GUI & scripts) |
| `distillation_converter_gui.py` | GUI app | `python distillation_converter_gui.py` |
| `test_riazi_methods.py` | Validation | Debugging or development |
| `CODEBASE_OVERVIEW.md` | You are here! | Learning the project |
| `QUICK_REFERENCE.md` | Fast lookup | Quick answers |
| `ARCHITECTURE.md` | Data flow diagrams | Understanding flow |
| `RIAZI_IMPLEMENTATION.md` | Technical details | Deep dive into correlations |

---

## 💡 Pro Tips

1. **Always pass density** - even if you don't think it matters
2. **Use 8 points** - standard: 0%, 10%, 30%, 50%, 70%, 90%, 95%, 100%
3. **Check order** - D86 < D2887 < TBP always; if not, data is wrong
4. **Use GUI** for one-off conversions
5. **Use code** for batch processing
6. **Export to CSV** for external use (spreadsheets, other tools)

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Import error | Install: `pip install -r requirements.txt` |
| GUI won't start | Check PySide6: `pip install PySide6>=6.10.0` |
| Curves cross | Check input data order and monotonicity |
| Results seem wrong | Verify density is in 600-1200 kg/m³ range |
| Conversion seems off | Check RIAZI_IMPLEMENTATION.md for expected ranges |

---

## 🎬 Next Steps

1. **Read:** QUICK_REFERENCE.md (1 min)
2. **Try GUI:** `python distillation_converter_gui.py` (2 min)
3. **Run code:** Use Oil class with sample data (2 min)
4. **Deep dive:** Read RIAZI_IMPLEMENTATION.md if curious (10 min)

**Total onboarding time:** ~15 minutes

---

## 📞 Quick Reference

```python
# The two-liner quickstart
from bp_conversions import Oil
oil = Oil([[0, 160], [50, 225], [100, 290]], 820, 'D86')

# Now you can:
oil.D86_interp(50)      # Query any %
oil.D2887_interp(50)    # Get any curve
oil.TBP_interp(50)      # At any point
oil.VABP                # Get properties
oil.WatsonK             
```

---

## ✨ What Makes This Project Good

1. **Physics-based:** Riazi correlations, not guesses
2. **Complete:** Handles all 3 conversions both ways
3. **Flexible:** Use GUI, Python code, or library
4. **Tested:** Validation tests included
5. **Documented:** 6 doc files for all levels
6. **Professional:** Qt GUI with plots, tables, export

---

## 🎯 Key Takeaway

You now know:
- ✅ **What** it does (converts distillation curves)
- ✅ **How** it works (Riazi correlations + PCHIP)
- ✅ **Why** it matters (enable compatibility)
- ✅ **How to use** it (Oil class or GUI)
- ✅ **Where** to find help (6 documentation files)

**You're ready to use this project!**

---

**Welcome aboard!**
**Status:** ✅ READY TO USE
**Last Updated:** November 16, 2025
