# CSV/Excel Import Feature Guide

## Overview

The Distillation Curve Interconversion Tool now supports importing distillation curve data directly from CSV and Excel files. This feature streamlines the process of converting data from existing spreadsheets.

## Features

### Import Methods

#### CSV File Import
- Click "📥 Import CSV" button in the GUI
- Select a `.csv` file from your computer
- The tool will automatically detect column headers
- Data is loaded into the input table

#### Excel File Import
- Click "📥 Import Excel" button in the GUI
- Select a `.xlsx` or `.xls` file from your computer
- The tool automatically reads the first sheet
- Column detection works the same as CSV

### Column Auto-Detection

The import feature intelligently detects required columns:

#### Volume Column Detection
Recognizes columns containing:
- "vol" (case-insensitive)
- "percentage"
- "%" 
- "cut"

Examples of valid volume column names:
- Volume %
- Vol%
- % Volume
- Volume Percent
- Cut %

#### Temperature Column Detection
Recognizes columns containing:
- "temp" (case-insensitive)
- "temperature"
- "°c" or "°C"
- "celsius"
- "deg" or "degree"

Examples of valid temperature column names:
- Temperature C
- Temp °C
- Temp Celsius
- Temperature Deg
- Degrees C

#### Optional Density Column Detection
The tool can also auto-detect and load density:
- "dens" (case-insensitive)
- "density"
- "kg/m" or "kg/m3"

If a density column is found and the value is within valid range (600-1200 kg/m³), it will automatically update the density input field.

### Input Type Auto-Detection

The tool attempts to automatically determine the input type based on the filename:

- **D86** (default): Assumed for most files
- **D2887**: Auto-detected if filename contains "d2887"
- **TBP**: Auto-detected if filename contains "tbp" or "atm"

You can always manually change the input type after import using the dropdown menu.

## File Format Requirements

### CSV Format Example
```csv
Volume %,Temperature C,Density kg/m3
5,150,850
10,175,850
20,210,850
30,245,850
40,280,850
50,315,850
60,350,850
70,385,850
80,420,850
90,455,850
95,475,850
```

### Excel Format Example
| Volume % | Temperature C | Density kg/m3 |
|----------|---------------|---------------|
| 5        | 150           | 850           |
| 10       | 175           | 850           |
| 20       | 210           | 850           |
| 30       | 245           | 850           |
| 40       | 280           | 850           |
| 50       | 315           | 850           |
| 60       | 350           | 850           |
| 70       | 385           | 850           |
| 80       | 420           | 850           |
| 90       | 455           | 850           |
| 95       | 475           | 850           |

## Workflow Example

1. **Prepare your file** (CSV or Excel) with:
   - Column for volume percentages
   - Column for temperatures (in °C)
   - Optional: Column for density (kg/m³)

2. **Open the GUI**:
   ```bash
   python distillation_converter_gui.py
   # or if installed via pip:
   distillation-gui
   ```

3. **Click Import Button**:
   - Click "📥 Import CSV" or "📥 Import Excel"
   - Select your file from the file browser
   - The data automatically loads into the table

4. **Verify Settings**:
   - Check that input type (D86/D2887/TBP) is correct
   - Confirm density value if applicable
   - Adjust the basis (Vol% or Wt%) if needed

5. **Perform Conversions**:
   - Select conversion checkboxes (D86, D2887, TBP)
   - Click "🧮 Calculate Conversions"
   - View results in the plot and data tabs

6. **Export Results**:
   - Save as CSV, Excel, or JSON using export buttons
   - Results include all conversions and properties

## Error Handling

### "Could not auto-detect required columns"
This error occurs when the tool cannot find columns for volume and temperature. To fix:

1. **Rename columns** in your file to include:
   - "Volume" or "Vol" or "%" for the volume column
   - "Temperature" or "Temp" or "Celsius" for the temperature column

2. **Check column headers** - they must be in the first row

3. **Verify column names** - use standard naming conventions

### Example of Problematic Columns
- "cut" (ambiguous - contains both vol and temp keywords)
- Unlabeled columns (use "Volume %" and "Temp C" instead)

### Data Validation
After import, the tool validates:
- Temperature values are numeric
- Density (if present) is in valid range: 600-1200 kg/m³
- Data points are properly formatted

Invalid rows are skipped with a message, allowing partial imports.

## Sample Files

Sample CSV and Excel files are included in the `examples/` directory:
- `sample_d86.csv` - D86 distillation curve example
- `sample_d2887.csv` - D2887 distillation curve example
- `sample_distillation_data.xlsx` - Excel workbook with multiple sheets

## Tips for Best Results

1. **Use clear column names**: More descriptive names improve auto-detection
2. **Start with a small file**: Test with 5-10 data points first
3. **Check data order**: Volume percentages should be in ascending order (0→100%)
4. **Validate temperatures**: Temperatures should increase with volume percentage
5. **Set density correctly**: Accurate density affects properties calculations
6. **Use consistent units**: Always use °C for temperature, kg/m³ for density, and %v for volume

## Troubleshooting

### Import dialog doesn't appear
- Make sure you're using a recent version of the GUI
- Check that PySide6 is properly installed

### Data doesn't load into table
- Verify file format (CSV or Excel)
- Check that column names match detection keywords
- Ensure no special characters in data values

### Incorrect input type detected
- Manually select the correct type from the dropdown
- The filename-based detection is just a convenience feature

### Calculation fails after import
- Check that temperature values are monotonically increasing
- Verify density is in the valid range (600-1200 kg/m³)
- Make sure there are at least 2 data points

## Support

For issues with the import feature:
1. Check the Examples folder for sample files
2. Review the error message carefully
3. Ensure data format matches examples
4. Try manually entering a few data points to verify calculations work
