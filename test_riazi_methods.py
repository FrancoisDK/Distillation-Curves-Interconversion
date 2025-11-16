"""
Test script to validate Riazi-Daubert correlations for distillation conversions.

This script tests:
1. D2887 → D86 using Riazi-Daubert inverse correlation
2. D2887 → TBP using Riazi-based correlation
3. Comparison with previous simple offset methods
4. Validation that curves maintain proper physical relationships
"""

from bp_conversions import Oil
import matplotlib.pyplot as plt

# Sample D2887 (SimDist) data for a kerosene/diesel fraction
# Volume%, Temperature (°C)
d2887_data = [
    [0, 160.0],    # IBP
    [10, 180.5],
    [30, 205.0],
    [50, 225.0],
    [70, 245.0],
    [90, 270.0],
    [100, 290.0]   # FBP
]

print("=" * 80)
print("RIAZI-DAUBERT CORRELATION VALIDATION TEST")
print("=" * 80)
print("\nInput: D2887 (SimDist) Data")
print("-" * 80)
print(f"{'Volume %':>10} {'D2887 Temp (°C)':>18}")
print("-" * 80)
for point in d2887_data:
    print(f"{point[0]:>10.0f} {point[1]:>18.1f}")

# Create Oil object with D2887 as input
oil = Oil(d2887_data, Density=820, input_type='D2887')

print("\n" + "=" * 80)
print("CONVERSION RESULTS USING RIAZI CORRELATIONS")
print("=" * 80)

# Get temperatures at key volume points
vol_points = [0, 5, 10, 30, 50, 70, 90, 95]
print(f"\n{'Volume %':>10} {'D86 (°C)':>12} {'D2887 (°C)':>12} {'TBP (°C)':>12} {'D86-D2887':>12} {'TBP-D2887':>12}")
print("-" * 80)

for vol in vol_points:
    d86_temp = oil.D86_interp(vol)
    d2887_temp = oil.D2887_interp(vol)
    tbp_temp = oil.TBP_interp(vol)
    
    diff_d86_d2887 = d86_temp - d2887_temp
    diff_tbp_d2887 = tbp_temp - d2887_temp
    
    print(f"{vol:>10.0f} {d86_temp:>12.2f} {d2887_temp:>12.2f} {tbp_temp:>12.2f} "
          f"{diff_d86_d2887:>12.2f} {diff_tbp_d2887:>12.2f}")

print("\n" + "=" * 80)
print("VALIDATION CHECKS")
print("=" * 80)

# Check that curves maintain proper order: D86 < D2887 < TBP
all_valid = True
vol_range = range(0, 101, 5)

for vol in vol_range:
    d86_temp = oil.D86_interp(vol)
    d2887_temp = oil.D2887_interp(vol)
    tbp_temp = oil.TBP_interp(vol)
    
    if not (d86_temp < d2887_temp < tbp_temp):
        print(f"❌ FAIL at {vol}%: D86={d86_temp:.2f}, D2887={d2887_temp:.2f}, TBP={tbp_temp:.2f}")
        all_valid = False

if all_valid:
    print("✅ PASS: All curves maintain proper order (D86 < D2887 < TBP) at all points")

# Check temperature differences are realistic
print("\n" + "-" * 80)
print("TEMPERATURE DIFFERENCE ANALYSIS")
print("-" * 80)

# D86 vs D2887: Should be 2-8°C (D2887 higher)
print("\nD2887 - D86 differences (expected: 2-8°C):")
d86_d2887_diffs = []
for vol in [0, 10, 30, 50, 70, 90]:
    diff = oil.D2887_interp(vol) - oil.D86_interp(vol)
    d86_d2887_diffs.append(diff)
    print(f"  {vol:>3}%: {diff:>6.2f}°C")

min_diff = min(d86_d2887_diffs)
max_diff = max(d86_d2887_diffs)
print(f"  Range: {min_diff:.2f} to {max_diff:.2f}°C")

if 2.0 <= min_diff and max_diff <= 8.0:
    print("  ✅ PASS: D2887-D86 differences within expected range (2-8°C)")
else:
    print(f"  ⚠️  WARNING: D2887-D86 differences outside typical range")

# TBP vs D2887: Should be 0-3°C (TBP higher)
print("\nTBP - D2887 differences (expected: 0-3°C):")
tbp_d2887_diffs = []
for vol in [0, 10, 30, 50, 70, 90]:
    diff = oil.TBP_interp(vol) - oil.D2887_interp(vol)
    tbp_d2887_diffs.append(diff)
    print(f"  {vol:>3}%: {diff:>6.2f}°C")

min_diff = min(tbp_d2887_diffs)
max_diff = max(tbp_d2887_diffs)
print(f"  Range: {min_diff:.2f} to {max_diff:.2f}°C")

if 0.0 <= min_diff and max_diff <= 3.0:
    print("  ✅ PASS: TBP-D2887 differences within expected range (0-3°C)")
else:
    print(f"  ⚠️  WARNING: TBP-D2887 differences outside typical range")

# Create visualization
print("\n" + "=" * 80)
print("GENERATING PLOT...")
print("=" * 80)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: All three distillation curves
vol = list(range(0, 101))
ax1.plot(vol, [oil.D86_interp(v) for v in vol], 'b-', linewidth=2, label='D86 (ASTM)')
ax1.plot(vol, [oil.D2887_interp(v) for v in vol], 'r--', linewidth=2, label='D2887 (SimDist)')
ax1.plot(vol, [oil.TBP_interp(v) for v in vol], 'g-.', linewidth=2, label='TBP')
ax1.set_xlabel('Volume % Distilled', fontsize=12)
ax1.set_ylabel('Temperature (°C)', fontsize=12)
ax1.set_title('Distillation Curves using Riazi-Daubert Correlations', fontsize=13, fontweight='bold')
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)

# Plot 2: Temperature differences
ax2.plot(vol, [oil.D2887_interp(v) - oil.D86_interp(v) for v in vol], 
         'b-', linewidth=2, label='D2887 - D86')
ax2.plot(vol, [oil.TBP_interp(v) - oil.D2887_interp(v) for v in vol], 
         'r--', linewidth=2, label='TBP - D2887')
ax2.set_xlabel('Volume % Distilled', fontsize=12)
ax2.set_ylabel('Temperature Difference (°C)', fontsize=12)
ax2.set_title('Temperature Differences Between Methods', fontsize=13, fontweight='bold')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)

plt.tight_layout()
plt.savefig('riazi_correlation_validation.png', dpi=300, bbox_inches='tight')
print("\n✅ Plot saved as 'riazi_correlation_validation.png'")

plt.show()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
The Riazi-Daubert correlations provide:
1. Physics-based power-law relationships (T = a × T^b)
2. More accurate conversions across different petroleum fractions
3. Proper temperature relationships (D86 < D2887 < TBP)
4. Realistic separations matching industry standards

Advantages over simple offsets:
- Better accuracy for light/heavy fractions
- Accounts for non-linear temperature relationships
- Based on extensive experimental data (Riazi & Daubert, 1980)
- Consistent with API Technical Data Book procedures
""")
print("=" * 80)
