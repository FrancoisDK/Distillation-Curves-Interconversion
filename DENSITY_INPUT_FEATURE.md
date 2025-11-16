# Density Input Feature

## Overview

The distillation converter GUI now includes a **per-cut density column** in the input data table, allowing users to enter density values directly for each distillation point.

## Feature Details

### Input Table Structure

The table now has **3 columns**:
1. **Vol % / Wt %** - Fixed column with standard boiling points (0, 5, 10, 20, ..., 95)
2. **Temperature (°C)** - User-entered distillation temperature data (editable)
3. **Density (kg/m³)** - **NEW** - Per-cut density values (optional, editable)

### Usage

#### Manual Entry
1. Click **➕ Add Point** to add a new row
2. Enter temperature in the "Temperature (°C)" column
3. (Optional) Enter density in the "Density (kg/m³)" column for that specific cut
4. Click **Calculate Conversions** to process

#### From CSV/Excel Import
- If your imported file contains a density column, values are automatically detected and populated
- Supported column names: `density`, `dens`, `kg/m³`, `kg/m3`, etc.
- Per-cut densities are stored and used for volume/weight conversions

### Density Validation

- **Valid range**: 600 - 1200 kg/m³
- **Invalid entry**: Shows warning dialog and clears the field
- **Optional**: Density is optional; if not provided, the average density spinbox value is used

### How Densities Are Used

#### Scenario 1: No per-cut density entered
- All cuts use the **average density** from the spinbox (e.g., 850 kg/m³)

#### Scenario 2: Per-cut densities entered
- Each cut uses its **specific density** from the table
- Better accuracy for oils with varying density across boiling points

#### Scenario 3: Mixed entry
- Cuts with density values use those values
- Cuts without density values fall back to the average density spinbox

### Data Cleanup

- **Removing a row**: Automatically clears the density entry for that point
- **Clear All**: Empties all data including densities
- **Changing basis**: Density column persists (still visible for Vol % or Wt %)

## Code Implementation

### Table Initialization
```python
self.input_table.setColumnCount(3)
self.input_table.setHorizontalHeaderLabels(["Vol %", "Temperature (°C)", "Density (kg/m³)"])
```

### Cell Change Handler
```python
def on_cell_changed(self, row, column):
    if column == 2:  # Density column
        density = float(self.input_table.item(row, 2).text())
        if 600 <= density <= 1200:
            self.input_densities[vol_pct] = density
```

### Data Collection in Conversions
```python
# Store per-cut density if provided
if dens_item and dens_item.text():
    density = float(dens_item.text())
    if 600 <= density <= 1200:
        self.input_densities[vol_pct] = density
```

## Integration with Conversion Features

The per-cut density column integrates seamlessly with:

1. **CSV/Excel Import**: Automatically detects and populates density columns
2. **Volume/Weight Conversion**: Uses per-cut densities for accurate vol% ↔ wt% conversions
3. **Density Spinbox**: Acts as fallback for any cut without an explicit density
4. **Basis Selection**: Density column visible regardless of Vol% or Wt% selection

## Examples

### Example 1: Constant Density
```
Vol %  | Temperature | Density
-------|-------------|----------
0      | 45          | 850
5      | 120         | 850
10     | 165         | 850
...
95     | 360         | 850
```
All densities the same → uses constant value

### Example 2: Variable Density (Real Oil)
```
Vol %  | Temperature | Density
-------|-------------|----------
0      | 45          | 810
5      | 120         | 815
10     | 165         | 820
...
95     | 360         | 875
```
Each cut has unique density → higher accuracy

### Example 3: Mixed (Some Blanks)
```
Vol %  | Temperature | Density
-------|-------------|----------
0      | 45          | 810
5      | 120         |         <- Uses avg (850)
10     | 165         | 820
...
95     | 360         |         <- Uses avg (850)
```
Combines per-cut and average densities

## Testing

The feature is tested in `tests/test_volume_weight_conversion.py`:
- Test with per-cut density dictionary
- Validation of density range
- Proper storage and retrieval

## Related Features

- **Volume/Weight Conversion**: Uses per-cut densities for accurate conversions
- **CSV/Excel Import**: Automatically extracts density columns
- **IMPORT_GUIDE.md**: Documentation on importing density data
- **VOLUME_WEIGHT_CONVERSION_GUIDE.md**: Details on density-based conversions

## Commit

- **Hash**: 5b53a76
- **Date**: November 16, 2025
- **Changes**: +44 lines, Table now has 3 columns with density input capability
