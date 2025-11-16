"""
Debug API 3A3.1 implementation to verify the calculations
"""
from bp_conversions import Oil

# Test data
d2887_input = [
    [0, 160.0],
    [10, 176.7],
    [30, 193.3],
    [50, 206.7],
    [70, 222.8],
    [90, 243.9],
    [95, 251.0],
    [100, 260.0]
]

density = 800

print("=" * 80)
print("Debugging API 3A3.1 Implementation")
print("=" * 80)

# Create interpolator manually to show calculations
from scipy.interpolate import PchipInterpolator

vol_distilled = [p[0] for p in d2887_input]
temperatures = [p[1] for p in d2887_input]
D2887_interp = PchipInterpolator(vol_distilled, temperatures)

def convert_temp(value, from_unit, to_unit):
    """Simple temperature conversion"""
    if from_unit == 'C' and to_unit == 'F':
        return value * 9/5 + 32
    elif from_unit == 'F' and to_unit == 'C':
        return (value - 32) * 5/9
    return value

# API 3A3.1 constants
API_constants = {
    '100-95': (0.02172, 1.9733),
    '95-90':  (0.97476, 0.8723),
    '90-70':  (0.31531, 1.2938),
    '70-50':  (0.19861, 1.3975),
    '50-30':  (0.05342, 1.6988),
    '30-10':  (0.011903, 2.0253),
    '10-5':   (0.15779, 1.4295)
}

print("\nAPI 3A3.1 Step-by-Step Calculation:")
print("-" * 80)

# Step 1: TBP(50) = SD(50)
SD_50_C = D2887_interp(50)
TBP_50_C = SD_50_C
TBP_50_F = convert_temp(TBP_50_C, 'C', 'F')
print(f"Step 1: TBP(50) = SD(50)")
print(f"  SD(50) = {SD_50_C:.2f}°C = {TBP_50_F:.2f}°F")
print(f"  TBP(50) = {TBP_50_C:.2f}°C = {TBP_50_F:.2f}°F")

print(f"\nStep 2: Calculate temperature differences Wi = C × Vi^D")
print("-" * 80)

# Above 50%
SD_50_F = convert_temp(SD_50_C, 'C', 'F')
SD_70_C = D2887_interp(70)
SD_70_F = convert_temp(SD_70_C, 'C', 'F')
V4 = abs(SD_70_F - SD_50_F)
C, D = API_constants['70-50']
W4 = C * (V4 ** D)
TBP_70_F = TBP_50_F + W4
TBP_70_C = convert_temp(TBP_70_F, 'F', 'C')

print(f"\n70-50% range:")
print(f"  SD(70) = {SD_70_C:.2f}°C = {SD_70_F:.2f}°F")
print(f"  V4 = |SD(70) - SD(50)| = |{SD_70_F:.2f} - {SD_50_F:.2f}| = {V4:.2f}°F")
print(f"  C = {C:.5f}, D = {D:.4f}")
print(f"  W4 = {C:.5f} × {V4:.2f}^{D:.4f} = {W4:.2f}°F")
print(f"  TBP(70) = TBP(50) + W4 = {TBP_50_F:.2f} + {W4:.2f} = {TBP_70_F:.2f}°F = {TBP_70_C:.2f}°C")
print(f"  Difference: TBP(70) - SD(70) = {TBP_70_C - SD_70_C:.2f}°C")

SD_90_C = D2887_interp(90)
SD_90_F = convert_temp(SD_90_C, 'C', 'F')
V3 = abs(SD_90_F - SD_70_F)
C, D = API_constants['90-70']
W3 = C * (V3 ** D)
TBP_90_F = TBP_70_F + W3
TBP_90_C = convert_temp(TBP_90_F, 'F', 'C')

print(f"\n90-70% range:")
print(f"  SD(90) = {SD_90_C:.2f}°C = {SD_90_F:.2f}°F")
print(f"  V3 = |SD(90) - SD(70)| = |{SD_90_F:.2f} - {SD_70_F:.2f}| = {V3:.2f}°F")
print(f"  C = {C:.5f}, D = {D:.4f}")
print(f"  W3 = {C:.5f} × {V3:.2f}^{D:.4f} = {W3:.2f}°F")
print(f"  TBP(90) = TBP(70) + W3 = {TBP_70_F:.2f} + {W3:.2f} = {TBP_90_F:.2f}°F = {TBP_90_C:.2f}°C")
print(f"  Difference: TBP(90) - SD(90) = {TBP_90_C - SD_90_C:.2f}°C")

# Below 50%
SD_30_C = D2887_interp(30)
SD_30_F = convert_temp(SD_30_C, 'C', 'F')
V5 = abs(SD_50_F - SD_30_F)
C, D = API_constants['50-30']
W5 = C * (V5 ** D)
TBP_30_F = TBP_50_F - W5
TBP_30_C = convert_temp(TBP_30_F, 'F', 'C')

print(f"\n50-30% range:")
print(f"  SD(30) = {SD_30_C:.2f}°C = {SD_30_F:.2f}°F")
print(f"  V5 = |SD(50) - SD(30)| = |{SD_50_F:.2f} - {SD_30_F:.2f}| = {V5:.2f}°F")
print(f"  C = {C:.5f}, D = {D:.4f}")
print(f"  W5 = {C:.5f} × {V5:.2f}^{D:.4f} = {W5:.2f}°F")
print(f"  TBP(30) = TBP(50) - W5 = {TBP_50_F:.2f} - {W5:.2f} = {TBP_30_F:.2f}°F = {TBP_30_C:.2f}°C")
print(f"  Difference: TBP(30) - SD(30) = {TBP_30_C - SD_30_C:.2f}°C")

print("\n" + "=" * 80)
print("Analysis:")
print("=" * 80)
print("""
The API 3A3.1 method appears to produce TBP values that are:
- HIGHER than SimDist at low vol% (good!)
- EQUAL to SimDist at 50% (by definition)
- LOWER than SimDist at high vol% (unexpected!)

This might indicate:
1. The method was designed for a specific type of petroleum fraction
2. There might be additional corrections needed
3. The constants may have been optimized for narrower cut ranges

Note: The document says this procedure was RETIRED in 2025 and replaced by 3A3.4.
This might explain why the results don't match expected behavior for all fractions.
""")
