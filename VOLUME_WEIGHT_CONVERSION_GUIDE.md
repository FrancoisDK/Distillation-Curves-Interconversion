# Volume/Weight Percentage Conversion with Per-Cut Density

**Status:** ✅ Implemented  
**Commit:** `1eace58`  
**Date:** 2025-01-09

## Overview

The GUI now supports **volume % to weight % conversion** using per-cut density values. If your import file contains density data for each distillation cut, the tool can convert between volume and weight percentages for accurate composition analysis.

## How It Works

### Per-Cut Density Storage

When you import a CSV or Excel file with a density column:

1. **Single Density:** If only one density is provided → Used for all cuts
2. **Per-Cut Densities:** If density varies by cut → Stored in `self.input_densities` dictionary

Example file structure:
```
Volume %,Temperature C,Density kg/m3
5,150,810          <- Density of 5% cut = 810 kg/m3
10,175,815         <- Density of 10% cut = 815 kg/m3
20,210,825         <- Density of 20% cut = 825 kg/m3
...
```

### Conversion Method

The conversion uses **cumulative mass calculations:**

**Volume % → Weight %:**
```
For each cut:
  vol_slice = vol[i] - vol[i-1]
  mass_slice = vol_slice × density[i]
  cumulative_mass += mass_slice
  wt%[i] = (cumulative_mass / total_mass) × 100
```

**Weight % → Volume %:**
```
For each cut:
  wt_slice = wt[i] - wt[i-1]
  vol_slice = wt_slice / density[i]
  cumulative_volume += vol_slice
  vol%[i] = (cumulative_volume / total_volume) × 100
```

## Using the Feature

### Step 1: Prepare Your Data File

Create a CSV or Excel file with per-cut density values:

**Option A - CSV Format:**
```csv
Volume %,Temperature C,Density kg/m3
5,150,810
10,175,815
20,210,825
30,245,835
40,280,845
50,315,850
60,350,855
70,385,860
80,420,865
90,455,870
95,475,875
```

**Option B - Excel Format:**
| Volume % | Temperature C | Density kg/m3 |
|----------|---------------|---------------|
| 5        | 150           | 810           |
| 10       | 175           | 815           |
| 20       | 210           | 825           |
| ...      | ...           | ...           |

### Step 2: Import the File

```
1. Click "📥 Import CSV" or "📥 Import Excel"
2. Select your file
3. GUI auto-detects Volume, Temperature, and Density columns
4. Density field shows average of per-cut values
5. Import success message shows: "N cuts with per-cut density"
```

Example success message:
```
Imported 11 data points from CSV (11 cuts with per-cut density)
```

### Step 3: Select Basis and Calculate

```
1. Choose input basis:
   - "📊 Volume %" → Input is volume percentages
   - "⚖️ Weight %" → Input is weight percentages
2. Click "🧮 Calculate Conversions"
3. Conversions are performed using per-cut density values
```

## Feature Details

### What Gets Stored

When you import data with per-cut densities:

```python
self.input_densities = {
    5: 810,    # 5% cut has density 810 kg/m3
    10: 815,   # 10% cut has density 815 kg/m3
    20: 825,   # 20% cut has density 825 kg/m3
    ...
}

# Average density calculated and stored in density_input field
avg_density = sum(densities) / len(densities)  # 845.9 kg/m3
```

### Basis Conversion Logic

**If input is Weight %:**
1. Gets per-cut densities from `self.input_densities`
2. Calls `convert_weight_to_volume_percent()`
3. Converts all input data to Volume %
4. Creates Oil object with converted Volume %
5. Results are still shown in Volume %

**If input is Volume %:**
1. Data used as-is
2. Per-cut densities available for future weight % exports

### Density Validation

- Per-cut densities must be in range: **600-1200 kg/m³**
- Invalid density values are skipped
- Out-of-range values are ignored with no error

### Fallback Behavior

If per-cut densities can't be detected:
1. First density value is used for all cuts
2. GUI stores it in the density field
3. Conversions use that single value as constant density

## Examples

### Example 1: Light Hydrocarbon (Density Increases)

Input file: kerosene_d86.csv
```
Volume %,Temp C,Density
5,150,810
10,175,815
20,210,825
...
95,475,875
```

Result:
- Average density: 845.9 kg/m³
- Light cuts (5-10%) have lower density
- Heavy cuts (90-95%) have higher density
- Conversion accounts for this variation
- Weight % curve shows less steep slope at beginning

### Example 2: Heavy Crude (Density Varies Widely)

Input file: heavy_crude.csv
```
Volume %,Temp C,Density
5,220,600
10,250,650
20,310,750
...
95,520,950
```

Result:
- Average density: 780 kg/m³
- Significant density variation (600→950)
- Conversion shows major vol% vs wt% differences
- Light cuts weigh much less than their volume suggests
- Accurate composition analysis with density effects

### Example 3: Constant Density (Uniform Crude)

Input file: uniform_crude.csv
```
Volume %,Temp C,Density
5,150,850
10,175,850
20,210,850
...
95,475,850
```

Result:
- All cuts at 850 kg/m³
- Volume % and Weight % are essentially identical
- Conversion still works, but differences are minimal

## Test Results

All conversion tests passing (5/5):

```
[TEST 1] Constant density → Conversion working
[TEST 2] Variable density (810-875) → Differences captured
[TEST 3] Extreme variation (600-1200) → Monotonicity preserved
[TEST 4] Weight→Volume conversion → Logically sound
[TEST 5] Per-cut storage → Dictionary properly maintained
```

## Code Structure

### New Methods in `distillation_converter_gui.py`

**`convert_volume_to_weight_percent(vol_percents, densities)`**
- Takes: List of volume %, list/float of densities
- Returns: List of weight percentages
- Handles: Single or per-cut densities

**`convert_weight_to_volume_percent(wt_percents, densities)`**
- Takes: List of weight %, list/float of densities
- Returns: List of volume percentages
- Handles: Single or per-cut densities

**`calculate_conversions()` Enhanced**
- Checks if input basis is "Weight %"
- Calls conversion method if needed
- Converts weight % input to volume % for processing
- Rest of workflow unchanged

### Enhanced Import Methods

**`import_csv()` - Updated**
- Initializes: `self.input_densities = {}`
- For each row: Stores `self.input_densities[vol%] = density`
- Average density: Calculated and set in GUI
- Success message: Shows per-cut density count

**`import_excel()` - Updated**
- Same logic as CSV import
- Reads first sheet automatically
- Identical per-cut density storage

## Usage Recommendations

### Best Practices

1. **Accurate Density Data**
   - Use measured densities if available
   - Interpolate from density tables if needed
   - Ensure values are in 600-1200 kg/m³ range

2. **Data Organization**
   - Keep cuts at standard points: 5, 10, 30, 50, 70, 90, 95
   - Use clear column names: "Density", "kg/m3", "dens"
   - Put density column after temperature

3. **Verification**
   - Check average density matches your material
   - For petroleum, typical range: 700-950 kg/m³
   - Light fractions (naphtha): 680-780 kg/m³
   - Heavy fractions (fuel oil): 850-950 kg/m³

### When to Use

✅ **Use Weight % Input When:**
- Your analysis data is in weight percentages
- You want accurate weight-based composition
- You have per-cut density measurements

✅ **Use Volume % Input When:**
- Your data is in volume percentages (D86, D2887, TBP)
- You don't have density measurements
- You want standard distillation curve format

## Limitations & Notes

- **Interpolation:** Density interpolated between measured points
- **Extrapolation:** Assumes constant density beyond last cut
- **Numerical:** Small rounding in cumulative calculations
- **Validation:** Only densities 600-1200 kg/m³ accepted
- **File Format:** Column names must contain detection keywords

## Future Enhancements

Optional future improvements:

1. **Density Interpolation:** Fit curve through density values
2. **Temperature-Based Density:** Use T-ρ correlations
3. **Export Conversions:** Save weight % results to file
4. **Density Preview:** Show table of per-cut densities in GUI
5. **Density Fitting:** Import density at 2-3 points, fit rest

## Sample Files

Included in `examples/`:

- **sample_d86.csv** - No density (uses average)
- **sample_d86_with_density.csv** - With per-cut densities
- **sample_d2887.csv** - No density

Test with `sample_d86_with_density.csv` to see per-cut conversion in action.

## Testing

Run the test suite:
```bash
python tests/test_volume_weight_conversion.py
```

Expected output:
```
[OK] ALL TESTS PASSED!
```

---

**Feature Status:** ✅ Complete and tested  
**Ready for:** Production use, TestPyPI release  
**Verified:** All conversion logic validated  
**Documented:** Full guide provided
