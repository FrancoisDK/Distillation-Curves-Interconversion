# Distillation Curve Interconversion GUI - User Guide

## Overview
This GUI application provides a comprehensive tool for converting between different distillation curve types commonly used in petroleum refining:
- **ASTM D86**: Atmospheric distillation (low efficiency)
- **ASTM D2887**: Simulated distillation by gas chromatography (SimDis)
- **TBP**: True Boiling Point distillation (high efficiency)

## Features

### Input Configuration
1. **Select Input Type**
   - Choose from D86, D2887, or TBP as your input distillation type
   - The application will convert your input to the other two types

2. **Select Basis**
   - **Volume %**: Traditional basis for D86 and TBP
   - **Weight %**: Common basis for D2887 (SimDis) results
   
   **Note on Basis:**
   - D86: Typically volume % (liquid volume distilled)
   - D2887 (SimDis): Can be either vol% or wt%, but wt% is common from GC analysis
   - TBP: Can be either vol% or wt% depending on the distillation setup
   - The GUI accepts either basis and performs conversions internally

3. **Material Properties**
   - **Density**: Enter the density of your petroleum fraction (600-1200 kg/m³)
   - Default is 800 kg/m³ (typical for middle distillates)
   - Used for calculating Watson K factor and other properties

### Data Input

#### Standard Distillation Points
The table pre-populates with standard distillation points:
- **IBP (0%)**: Initial Boiling Point
- **10%, 30%, 50%, 70%, 90%, 95%**: Standard cut points
- **FBP (100%)**: Final Boiling Point

#### Entering Data
1. Click on the temperature cells (second column)
2. Enter temperature values in **°C** (Celsius)
3. You don't need to fill all points - minimum 3 points required
4. The application uses PCHIP interpolation for smooth curves

#### Adding Custom Points
- **Add Point**: Click to add a custom distillation point
- **Remove Point**: Select a row and click to remove it
- **Clear All**: Reset all data to start fresh

### Conversion Options
Select which conversions you want to see:
- ☑ **Convert to D86**: Show D86 curve
- ☑ **Convert to D2887 (SimDis)**: Show D2887 curve
- ☑ **Convert to TBP**: Show TBP curves (both API and Daubert methods)

### Calculate Button
Click the **Calculate Conversions** button to:
1. Validate your input data
2. Perform all selected conversions
3. Display results in plot and tables
4. Calculate petroleum properties

## Output Display

### 1. Plot Tab
Shows a graphical comparison of all distillation curves:
- **Black dots**: Your input data points
- **Blue solid line**: D86 curve
- **Red dashed line**: D2887 (SimDis) curve
- **Green dash-dot line**: TBP (API method)
- **Magenta dotted line**: TBP (Daubert method)

**Plot Features:**
- Zoom, pan, and save using the matplotlib toolbar
- Legend showing all curves
- Grid for easy reading
- X-axis: Volume % distilled (0-100%)
- Y-axis: Temperature in °C

### 2. Data Table Tab
Detailed numerical results showing:
- Volume % distilled at 5% increments (0, 5, 10, ..., 95, 100)
- Your input temperatures (where entered)
- Converted temperatures for D86, D2887, and TBP
- All temperatures in °C with 2 decimal places

### 3. Properties Tab
Calculated petroleum properties:
- **Density**: Your input density (kg/m³)
- **Specific Gravity**: Calculated at 15°C/4°C
- **VABP**: Volume Average Boiling Point (°F)
- **MeABP**: Mean Average Boiling Point (°F)
- **Watson K Factor**: Characterization factor

**Note:** VABP and MeABP are displayed in °F as per industry convention.

## Exporting Results

### Export to CSV
1. Click **Export CSV** button
2. Choose save location
3. Creates a comma-separated file with:
   - Header information
   - Calculated properties
   - Complete data table (0-100% at 5% increments)

### Export to Excel
1. Click **Export Excel** button
2. Choose save location
3. Creates a formatted Excel workbook with:
   - Formatted headers and titles
   - Properties section
   - Data table with all conversions
   - Adjusted column widths for readability

## Example Usage

### Example 1: Converting D86 to D2887 and TBP

1. **Select Input**: D86 (Atmospheric Distillation)
2. **Select Basis**: Volume %
3. **Enter Density**: 820 kg/m³ (for diesel)
4. **Enter Data**:
   ```
   Vol %    Temp (°C)
   0        180
   10       220
   30       260
   50       290
   70       320
   90       350
   100      370
   ```
5. **Check**: All conversion options
6. **Click**: Calculate Conversions
7. **View**: Results in plot and tables
8. **Export**: Save to Excel for documentation

### Example 2: Converting D2887 (SimDis) to D86

1. **Select Input**: D2887 (SimDis - GC)
2. **Select Basis**: Weight % (typical for GC data)
3. **Enter Density**: 750 kg/m³ (for kerosene)
4. **Enter Data**: Your SimDis results from GC analysis
5. **Check**: Convert to D86 and TBP
6. **Click**: Calculate Conversions
7. **Compare**: D2887 input vs. converted D86 curve

### Example 3: Quick Check with Minimal Data

If you only have a few points:
1. Enter at least 3 points (e.g., 10%, 50%, 90%)
2. The PCHIP interpolation will create smooth curves
3. Results will be interpolated for all display points

## Technical Notes

### Conversion Methods

#### D86 to TBP
Two methods are provided:
1. **API Method (1993)**: Uses American Petroleum Institute correlations
2. **Daubert Method (1994)**: Alternative correlation from Hydrocarbon Processing

Both are industry-standard methods with similar accuracy.

#### D86 to D2887
Uses a modified Riazi-Daubert correlation specifically calibrated for simulated distillation by gas chromatography.

### Interpolation
- Uses PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)
- Preserves monotonicity
- No overshoot between data points
- Smooth first derivatives

### Temperature Units
- **Input**: Always °C (Celsius)
- **Display**: °C for distillation curves
- **Properties**: °F for VABP and MeABP (industry standard)
- **Internal**: Conversions use Rankine for accuracy

### Volume % vs. Weight %

**When to use Volume %:**
- D86 results (standard method measures liquid volume)
- Traditional refinery practice
- Product specifications

**When to use Weight %:**
- D2887/SimDis results from GC (detector response is mass-based)
- When dealing with composition data
- Research applications

**Conversion between vol% and wt%:**
The application internally handles basis conversions using density. For most petroleum fractions, the difference is small (< 2-3%) but can be significant for very light or very heavy cuts.

## Validation and Quality Checks

The application performs several checks:
1. **Minimum data points**: At least 3 points required
2. **Temperature monotonicity**: Warns if temperatures don't increase with volume %
3. **Range validation**: Checks for physically reasonable temperatures
4. **Density validation**: Ensures density is in typical petroleum range

## Troubleshooting

### "Insufficient Data" Error
- **Problem**: Less than 3 data points entered
- **Solution**: Enter at least 3 distillation points

### Unusual Curve Shape
- **Problem**: Non-monotonic or erratic curves
- **Solution**: Check input data for errors, ensure temperatures increase with volume %

### Large Differences Between Methods
- **Problem**: D86, D2887, and TBP show very different values
- **Solution**: 
  - Verify density is correct
  - Check if input type selection matches your data
  - Ensure temperature units are in °C

### Export Button Disabled
- **Problem**: Cannot export results
- **Solution**: First click "Calculate Conversions" to generate results

## Tips for Best Results

1. **Data Quality**: Enter accurate, well-spaced data points
2. **Standard Points**: Try to include standard points (10, 30, 50, 70, 90%)
3. **Density**: Use measured density for best accuracy
4. **Multiple Runs**: Compare results from different input types
5. **Documentation**: Export to Excel for record keeping

## Petroleum Fraction Guidelines

### Typical Density Ranges:
- **Gasoline**: 720-780 kg/m³
- **Kerosene/Jet Fuel**: 775-840 kg/m³
- **Diesel/Gas Oil**: 820-900 kg/m³
- **Heavy Gas Oil**: 880-950 kg/m³
- **Vacuum Gas Oil**: 900-1000 kg/m³

### Typical Boiling Ranges:
- **Gasoline**: 30-200°C
- **Kerosene**: 150-280°C
- **Diesel**: 180-360°C
- **Gas Oil**: 200-400°C
- **Vacuum Gas Oil**: 350-550°C

## References

1. ASTM D86-23: Standard Test Method for Distillation of Petroleum Products at Atmospheric Pressure
2. ASTM D2887-23: Standard Test Method for Boiling Range Distribution of Petroleum Fractions by Gas Chromatography
3. API Technical Data Book - Petroleum Refining (1993)
4. Daubert, T. (1994). "Petroleum Fractions Distillation Interconversion", Hydrocarbon Processing
5. Riazi, M.R. and Daubert, T.E. (1980). "Simplify Property Predictions", Hydrocarbon Processing

## Support and Feedback

For questions, issues, or suggestions, please refer to the project documentation or contact the development team.

---

**Version**: 1.0  
**Last Updated**: October 2025  
**Compatibility**: Python 3.8+, PySide6, Matplotlib, SciPy, NumPy
