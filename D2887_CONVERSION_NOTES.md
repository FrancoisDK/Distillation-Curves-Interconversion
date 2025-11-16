# ASTM D86 to D2887 Conversion

## Overview
Added a new method `D86_to_D2887()` to convert ASTM D86 distillation data to ASTM D2887 (Simulated Distillation by Gas Chromatography).

## What is ASTM D2887?
ASTM D2887 is a test method for determining the boiling range distribution of petroleum fractions using gas chromatography (GC). It's commonly referred to as "SimDis" (Simulated Distillation).

### Key Characteristics:
- **Essentially equivalent to TBP**: According to ASTM standards, D2887 results are essentially equivalent to True Boiling Point (TBP) distillation results
- **More accurate than D86**: Provides better separation and more precise boiling point determination
- **Faster analysis**: GC-based method is much faster than physical distillation
- **Lower sample volume**: Requires much smaller sample sizes
- **Temperature range**: Applicable to petroleum products with final boiling point ≤ 538°C (1000°F)

## Correlation Method
The conversion uses a modified Riazi-Daubert correlation:

```
D2887_R = a × (D86_R)^b
```

Where:
- D2887_R = D2887 temperature in Rankine
- D86_R = D86 temperature in Rankine
- a, b = correlation constants dependent on volume % distilled

### Correlation Constants:
| Volume % | a      | b      |
|----------|--------|--------|
| 0 (IBP)  | 0.9800 | 0.9960 |
| 5        | 0.7200 | 1.0650 |
| 10       | 0.5850 | 1.0820 |
| 30       | 0.7800 | 1.0360 |
| 50       | 0.9050 | 1.0150 |
| 70       | 0.8900 | 1.0190 |
| 90       | 0.9650 | 1.0080 |
| 95       | 0.8350 | 1.0310 |

## Usage

```python
from bp_conversions import Oil

# Read D86 data from CSV
d86_data = Oil.read_d86_csv('your_d86_data.csv')

# Create Oil object with D86 data and density
oil = Oil(d86_data, Density=800)  # Density in kg/m³

# Access D2887 interpolation
d2887_interp = oil.D2887_interp

# Get D2887 temperature at any volume %
temp_at_50 = d2887_interp(50)  # Temperature at 50% distilled

# Plot all curves including D2887
oil.plot_TBP_D86()  # Now includes D2887 curve
```

## Comparison of Methods

### D86 (ASTM D86)
- **Type**: Physical distillation
- **Efficiency**: Low efficiency, simple apparatus
- **Use**: Product specifications, quality control
- **Typical products**: Gasoline, diesel, kerosene, jet fuel

### TBP (True Boiling Point)
- **Type**: Physical distillation
- **Efficiency**: High efficiency, many theoretical plates
- **Use**: Refinery design, process simulation
- **Typical products**: Crude oil fractions

### D2887 (SimDis)
- **Type**: Gas chromatography
- **Efficiency**: Very high, excellent separation
- **Use**: Modern alternative to TBP, process control
- **Typical products**: All petroleum fractions up to 538°C

## Expected Differences

Generally, for the same petroleum fraction:
```
D86 < D2887 ≈ TBP
```

The D86 temperatures are typically lower because:
1. Lower distillation efficiency
2. Heat losses in the apparatus
3. Different thermodynamic conditions

The conversion accounts for these differences using empirical correlations.

## References

1. **Riazi, M.R., and Daubert, T.E. (1980)**  
   "Simplify Property Predictions"  
   *Hydrocarbon Processing*, 59(3), p. 115

2. **ASTM D2887-23**  
   "Standard Test Method for Boiling Range Distribution of Petroleum Fractions by Gas Chromatography"  
   ASTM International

3. **Riazi, M.R. (2005)**  
   "Characterization and Properties of Petroleum Fractions"  
   ASTM International

4. **American Petroleum Institute (1993)**  
   "Technical Data Book—Petroleum Refining"  
   American Petroleum Institute, Washington, DC

5. **Daubert, T. (1994)**  
   "Petroleum Fractions Distillation Interconversion"  
   *Hydrocarbon Processing*, 9, p. 75

## Notes

- The correlation is most accurate for middle distillates (kerosene, diesel, gas oil)
- For very light fractions (gasoline) or very heavy fractions (residues), additional corrections may be needed
- The method interpolates missing distillation points using PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) for smooth curves
- All temperature conversions properly handle Celsius, Fahrenheit, Kelvin, and Rankine units

## Example Output

```
MeABP: 206.14 °F
Watson K: 10.91
VABP: 224.42 °F

D86 to TBP (Daubert):
[(0, -5.33), (10, 27.53), (30, 66.74), (50, 101.66), (70, 138.14), (90, 184.63), (95, 201.12)]

D86 to D2887 (SimDis):
[(0, 22.73), (10, 49.73), (30, 71.30), (50, 100.71), (70, 134.52), (90, 178.00), (95, 199.52)]
```

All temperatures in the output lists are in °C.
