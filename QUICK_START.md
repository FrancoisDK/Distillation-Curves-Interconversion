# Quick Start Guide - Distillation Curve Converter

## Launch the Application

### Method 1: Using uv (Recommended)
```bash
cd Distillation_Curve_interconv
uv run python distillation_converter_gui.py
```

### Method 2: Direct Python
```bash
cd Distillation_Curve_interconv
python distillation_converter_gui.py
```

### Method 3: From anywhere
```bash
python "C:/Users/franc/pyScripts/Distillation_Curve_interconv/distillation_converter_gui.py"
```

## 5-Minute Tutorial

### Step 1: Launch the Application
The GUI will open with two main panels:
- **Left Panel**: Input controls and data entry
- **Right Panel**: Results display (plot, tables, properties)

### Step 2: Configure Input
1. **Select Input Type**: Choose from dropdown
   - D86 (Atmospheric Distillation)
   - D2887 (SimDis - GC)
   - TBP (True Boiling Point)

2. **Select Basis**: 
   - Volume % (typical for D86, TBP)
   - Weight % (typical for D2887/SimDis)

3. **Enter Density**: 
   - Default is 800 kg/m³
   - Adjust for your specific petroleum fraction:
     - Gasoline: 720-780
     - Kerosene: 775-840
     - Diesel: 820-900

### Step 3: Enter Data
The table is pre-populated with standard distillation points:
- 0% (IBP), 10%, 30%, 50%, 70%, 90%, 95%, 100% (FBP)

**To enter data:**
1. Click on a temperature cell (second column)
2. Type the temperature in °C
3. Press Enter or Tab to move to next cell
4. You don't need to fill all rows - minimum 3 points required

**Example data (Diesel):**
```
Vol %    Temperature (°C)
0        180
10       220
30       260
50       290
70       320
90       350
100      370
```

### Step 4: Select Conversions
Check the boxes for conversions you want:
- ☑ Convert to D86
- ☑ Convert to D2887 (SimDis)
- ☑ Convert to TBP

### Step 5: Calculate
Click the green **"Calculate Conversions"** button

### Step 6: View Results

#### Plot Tab
- Shows all curves on one graph
- Black dots = your input data
- Colored lines = converted curves
- Use toolbar to zoom, pan, save image

#### Data Table Tab
- Numerical results at 5% increments
- All temperatures in °C
- Easy to copy/paste values

#### Properties Tab
- VABP, MeABP, Watson K
- Specific gravity
- Characterization parameters

### Step 7: Export Results

**Export to CSV:**
1. Click "Export CSV"
2. Choose save location
3. Opens in Excel/spreadsheet software

**Export to Excel:**
1. Click "Export Excel"
2. Choose save location
3. Creates formatted .xlsx file

## Common Tasks

### Adding a Custom Point
1. Click "Add Point" button
2. Enter volume % in first column
3. Enter temperature in second column
4. Click "Calculate Conversions" again

### Removing a Point
1. Click on the row you want to remove
2. Click "Remove Point" button

### Starting Over
Click "Clear All" to reset the table

### Changing Input Type
1. Select different input type from dropdown
2. Data remains but will be interpreted differently
3. Recalculate to see new results

## Tips for Success

### Data Entry Tips
✓ Enter at least 3 points for meaningful curves  
✓ Include key points: IBP, 50%, FBP at minimum  
✓ More points = better interpolation  
✓ Standard points (10, 30, 50, 70, 90) are recommended  

### Temperature Tips
✓ Always use °C (Celsius) for input  
✓ Temperatures should increase with volume %  
✓ Check for typos - unrealistic values will show on plot  

### Density Tips
✓ Use measured density when available  
✓ Typical ranges by product:
  - Light naphtha: 650-720 kg/m³
  - Gasoline: 720-780 kg/m³
  - Kerosene/Jet: 775-840 kg/m³
  - Diesel: 820-900 kg/m³
  - Gas Oil: 880-950 kg/m³

### Plot Interpretation
- **D86 < D2887 ≈ TBP** is normal
- D86 is typically 10-20°C lower
- Large gaps may indicate data issues
- Smooth curves indicate good interpolation

## Troubleshooting

### "Insufficient Data" Error
**Problem**: Less than 3 points entered  
**Solution**: Enter at least 3 temperature values

### Strange Curve Shapes
**Problem**: Curves have kinks or weird shapes  
**Solution**: Check input data for errors, ensure temperatures increase monotonically

### Export Buttons Disabled
**Problem**: Cannot click export buttons  
**Solution**: Click "Calculate Conversions" first

### Application Won't Start
**Problem**: Error messages on launch  
**Solution**: 
```bash
# Reinstall dependencies
cd Distillation_Curve_interconv
uv sync --reinstall
```

## Example Workflows

### Workflow 1: Lab D86 to Process D2887
**Scenario**: You have D86 lab results, need D2887 for process simulator

1. Select: "D86 (Atmospheric Distillation)"
2. Select: "Volume %"
3. Enter density and D86 temperatures
4. Check: "Convert to D2887 (SimDis)"
5. Calculate
6. View D2887 results in table
7. Export to Excel for process team

### Workflow 2: GC SimDis to Product Spec
**Scenario**: You have D2887 from GC, need D86 for product specification

1. Select: "D2887 (SimDis - GC)"
2. Select: "Weight %"
3. Enter density and D2887 temperatures
4. Check: "Convert to D86"
5. Calculate
6. Check D86 values against spec limits
7. Export results for quality report

### Workflow 3: Compare All Methods
**Scenario**: Technical study comparing distillation methods

1. Enter your data (any type)
2. Check all conversion options
3. Calculate
4. View plot with all 4 curves:
   - Input data
   - D86
   - D2887
   - TBP (API and Daubert)
5. Save plot image using toolbar
6. Export data table for documentation

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Move to next cell |
| Shift+Tab | Move to previous cell |
| Enter | Move down one row |
| Delete | Clear cell contents |

## Next Steps

- Read the [Full User Guide](GUI_USER_GUIDE.md) for detailed information
- Check [D2887 Technical Notes](D2887_CONVERSION_NOTES.md) for conversion theory
- See [README](README_DISTILLATION.md) for Python API usage
- Try the example CSV files: `D86 Distillation.csv`, `Kero D86.csv`

## Sample Data Sets

### Diesel Example
```csv
Vol%,Temperature
0,182
10,223
30,264
50,293
70,322
90,355
100,371
```
Density: 835 kg/m³

### Kerosene Example
```csv
Vol%,Temperature
0,157
10,180
30,198
50,212
70,228
90,251
100,267
```
Density: 810 kg/m³

### Heavy Gas Oil Example
```csv
Vol%,Temperature
0,265
10,312
30,345
50,372
70,398
90,431
100,455
```
Density: 895 kg/m³

---

**Need Help?** 
- Check the [GUI User Guide](GUI_USER_GUIDE.md)
- Review the [Technical Notes](D2887_CONVERSION_NOTES.md)
- Examine code documentation in `bp_conversions.py`

**Ready to Go!** Start entering your distillation data and explore the conversions!
