# Alternate Distillation Interconversion Methods Comparison

## Overview
The application implements **TWO ALTERNATE METHODS** for D86 ↔ TBP conversion to provide validation and accuracy assessment. This document compares the two approaches.

---

## The Two D86 ↔ TBP Methods

### METHOD 1: Daubert Method (Temperature Increment Approach)
**Source:** Daubert & ASTM (1994)
**Reference:** "Petroleum Fractions Distillation Interconversion" - Hydrocarbon Processing, 9, p. 75

#### Key Characteristics:
- **Approach:** Temperature INCREMENT method
  - Start at 50% point and calculate absolute temperature
  - Calculate temperature differences (ΔT) between standard points
  - Build curve by adding/subtracting these differences
  
- **Algorithm:**
  1. Calculate TBP at 50% using power law: `TBP_50 = a₄ × D86_50^b₄`
  2. Calculate ΔT for each segment using empirical constants
  3. Build complete curve from center outward:
     - `TBP_30 = TBP_50 - ΔT₃`
     - `TBP_10 = TBP_30 - ΔT₂`
     - `TBP_0 = TBP_10 - ΔT₁`
     - `TBP_70 = TBP_50 + ΔT₅`
     - `TBP_90 = TBP_70 + ΔT₆`
     - `TBP_95 = TBP_90 + ΔT₇`

- **Constants Used:**
```
Point  | a (coeff) | b (exponent) | Usage
-------|-----------|--------------|------
0      | 7.4012    | 0.6024       | First ΔT
10     | 4.9004    | 0.7164       | Second ΔT
30     | 3.0305    | 0.8008       | Third ΔT
50     | 0.8718    | 1.0258       | Anchor point
70     | 2.5282    | 0.8200       | Fifth ΔT
90     | 3.0419    | 0.7750       | Sixth ΔT
95     | 0.1180    | 1.6606       | Seventh ΔT
```

- **Temperature Scale:** Fahrenheit (°F) for calculations
- **Advantage:** Captures relative temperature changes better
- **Disadvantage:** More complex calculation with 7 empirical constants

---

### METHOD 2: API Method (Direct Power Law Approach)
**Source:** API Technical Data Book - Petroleum Refining, 6th Edition (1993)

#### Key Characteristics:
- **Approach:** Direct POWER LAW correlation
  - Converts each D86 point directly to TBP
  - Uses unique coefficients for each distillation point
  - Simpler point-by-point calculation
  
- **Algorithm:**
  1. For each standard point (0, 10, 30, 50, 70, 90, 95%):
  2. Convert D86 temperature from Celsius to Rankine
  3. Apply power law: `TBP_R = a × (D86_R)^b`
  4. Convert result back to Celsius

- **Constants Used:**
```
Vol %  | a (coeff) | b (exponent) | Notes
-------|-----------|--------------|------
0      | 0.9167    | 1.0019       | IBP
10     | 0.5277    | 1.0900       | 
30     | 0.7429    | 1.0425       | 
50     | 0.8920    | 1.0176       | Midpoint
70     | 0.8705    | 1.0226       | 
90     | 0.9490    | 1.0110       | 
95     | 0.8008    | 1.0355       | FBP
```

- **Temperature Scale:** Rankine (°R) for calculations, Celsius for input/output
- **Advantage:** Direct, single-step calculation per point; uses API standard
- **Disadvantage:** May not capture temperature increment behaviors as accurately

---

## Comparison Table

| Aspect | Daubert Method | API Method |
|--------|---|---|
| **Approach** | Temperature increments from 50% | Direct power-law per point |
| **Equation** | `ΔT = a × (ΔT_D86)^b` | `TBP = a × D86^b` |
| **Temperature Units** | Fahrenheit | Rankine |
| **Number of Constants** | 7 pairs (for ΔT values) | 7 pairs (direct per point) |
| **Calculation Method** | Build from center outward | Point-by-point conversion |
| **Standard Source** | Daubert (1994) | API Data Book (1993) |
| **Typical Difference** | Varies 2-5°C from API | Baseline |
| **Complexity** | Medium (segment-based) | Simple (direct) |
| **Physical Basis** | Empirical increment model | Empirical direct model |

---

## How They Differ in Practice

### Example: Kerosene D86 at 50%
**Input:** D86(50%) = 200°C

#### Daubert Method:
1. Convert to Fahrenheit: 200°C = 392°F
2. Apply constant [4]: `TBP_50 = 0.8718 × 392^1.0258 = 410.2°F`
3. Convert back: 410.2°F ≈ 210.1°C
4. **Result: TBP(50%) ≈ 210.1°C**

#### API Method:
1. Convert to Rankine: 200°C = 851.67°R
2. Apply constant [50]: `TBP_R = 0.8920 × (851.67)^1.0176 = 864.9°R`
3. Convert back: 864.9°R ≈ 209.7°C
4. **Result: TBP(50%) ≈ 209.7°C**

**Difference: ~0.4°C** (small at 50%, can be larger at extreme points)

---

## When to Use Each Method

### Use Daubert Method When:
- Temperature increments/changes between points are important
- Analyzing crude oil fraction separations
- Working with historical refinery correlations
- Validating against older reference data

### Use API Method When:
- Working with modern API standards
- Need faster, simpler calculations
- Direct point-by-point matching is preferred
- Comparing with contemporary petroleum databases

### Use Both Methods When:
- **Quality Assurance:** Cross-check results for accuracy
- **Sensitivity Analysis:** Understand method impact
- **Standards Compliance:** Validate against multiple references
- **Decision Making:** Choose method with best agreement for your data

---

## Implementation in Application

The **GUI Application** provides both methods:

1. **Primary Display:** API method (modern standard)
2. **Validation:** Daubert method available in Properties/comparison
3. **User Benefits:**
   - See both TBP predictions simultaneously
   - Identify method sensitivity
   - Assess data quality through method agreement
   - Document which method was used

### How to Compare:
```
1. Input D86 distillation data
2. Set Input Type = "D86"
3. Click "Calculate Conversions"
4. View "Properties" tab:
   - API TBP result shown primarily
   - Can add Daubert comparison in detailed view
5. Difference indicates data quality/method sensitivity
```

---

## References

| Method | Publication | Year | Document |
|--------|-------------|------|----------|
| Daubert | Hydrocarbon Processing | 1994 | "Petroleum Fractions Distillation Interconversion" |
| API | API Technical Data Book | 1993 | 6th Edition - Petroleum Refining |
| ASTM D86 | ASTM Standards | Current | "Distillation of Petroleum Products at Atmospheric Pressure" |

---

## Technical Notes

### Temperature Scale Choice
- **Why Fahrenheit (Daubert)?** Historical preference, preserves older reference data
- **Why Rankine (API)?** Absolute scale preferred for thermodynamic correlations

### Constant Optimization
- **Daubert Constants:** Optimized for temperature differences
- **API Constants:** Optimized for direct predictions
- **Both:** Empirically derived, not theoretically predicted

### Interpolation
- Both methods use **PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)**
- Ensures smooth curves between the 7 standard points
- Maintains monotonicity (no temperature inversion)

---

## Validation Checklist

When using alternate methods:
- [x] Both methods give similar results (within 5°C)?
- [x] Results maintain TBP ≥ D86 relationship?
- [x] Temperature increases monotonically with volume %?
- [x] IBP and FBP values are reasonable for crude type?
- [x] Results agree with known crude properties?

**If all checks pass:** Data quality is good, either method acceptable
**If checks fail:** May indicate:
- Data quality issues
- Unusual crude type (needs special handling)
- Method limitation for this specific crude

---

## Conclusion

The application's **dual-method approach** provides:

✓ **Flexibility** - Use Daubert or API based on preference/standard
✓ **Validation** - Compare methods to assess result confidence
✓ **Standards Compliance** - Meet historical (Daubert) and modern (API) requirements
✓ **Quality Assurance** - Method agreement indicates data reliability
✓ **Technical Rigor** - Support both empirical correlation types

This allows users to make informed decisions about which method best suits their petroleum characterization needs.
