"""
Debug the D86 curve shape when D2887 is input
"""
from bp_conversions import Oil
import matplotlib.pyplot as plt

# Data from your plot (D2887 input)
d2887_input = [
    [0, 160],
    [10, 176.7],
    [30, 193.3],
    [50, 206.7],
    [70, 222.8],
    [90, 243.9],
    [100, 255]
]

density = 800

print("=" * 80)
print("Analyzing D86 Curve Shape from D2887 Input")
print("=" * 80)

oil = Oil(d2887_input, Density=density, input_type='D2887')

print("\nD2887→D86 Conversion Results:")
print("-" * 80)
print(f"{'Vol%':<8} {'D2887 Input (°C)':<20} {'D86 Calc (°C)':<20} {'Difference (°C)':<20}")
print("-" * 80)

vol_points = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
for vol in vol_points:
    d2887_temp = oil.D2887_interp(vol)
    d86_temp = oil.D86_interp(vol)
    diff = d2887_temp - d86_temp
    print(f"{vol:<8} {d2887_temp:>18.2f}   {d86_temp:>18.2f}   {diff:>18.2f}")

print("\n" + "=" * 80)
print("Analysis:")
print("=" * 80)

# Check the D2887_to_D86 conversion factors
print("\nD2887→D86 correction factors being used:")
print("-" * 80)
correction_factors = {
    0: 0.96,    # D86 is ~4% lower at IBP
    10: 0.98,   # D86 is ~2% lower at 10%
    30: 0.99,   # D86 is ~1% lower at 30%
    50: 1.0,    # Use exact API equation at 50%
    70: 0.99,   # D86 is ~1% lower at 70%
    90: 0.98,   # D86 is ~2% lower at 90%
    100: 0.96   # D86 is ~4% lower at FBP
}

for vol, factor in correction_factors.items():
    d2887_temp = oil.D2887_interp(vol)
    print(f"Vol {vol:3d}%: factor={factor:.2f}, D2887={d2887_temp:6.2f}°C")

# Plot the curves
plt.figure(figsize=(10, 6))
vol_range = list(range(0, 101))

d86_curve = [oil.D86_interp(v) for v in vol_range]
d2887_curve = [oil.D2887_interp(v) for v in vol_range]
tbp_curve = [oil.TBP_interp(v) for v in vol_range]

plt.plot(vol_range, d86_curve, 'b-', linewidth=2, label='D86 (calculated)')
plt.plot(vol_range, d2887_curve, 'r--', linewidth=2, label='D2887 (input)')
plt.plot(vol_range, tbp_curve, 'g-.', linewidth=2, label='TBP (calculated)')

# Mark the input points
input_vols = [p[0] for p in d2887_input]
input_temps = [p[1] for p in d2887_input]
plt.plot(input_vols, input_temps, 'ko', markersize=8, label='Input points')

plt.xlabel('Volume % Distilled', fontsize=12)
plt.ylabel('Temperature (°C)', fontsize=12)
plt.title('D86 Curve Shape Analysis', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('d86_curve_debug.png', dpi=150)
print("\nPlot saved as 'd86_curve_debug.png'")

print("\n" + "=" * 80)
print("Issue Identified:")
print("=" * 80)
print("""
The D2887→D86 conversion is using the API equation with correction factors:
  D86 = 0.77601 × SD^1.0395 × correction_factor

At low volume%:
- The correction factor (0.96 at 0%, 0.98 at 10%) makes D86 LOWER
- Combined with the API equation, this produces D86 values that are too low
- This creates the strange flat/low shape at the beginning of the D86 curve

The API 3A3.2-1 equation: ASTM(50) = 0.77601 × SD(50)^1.0395
was designed for the 50% point, but applying it to all points with simple
correction factors doesn't work well at the extremes (0% and 100%).

Need a better D2887→D86 conversion method!
""")
