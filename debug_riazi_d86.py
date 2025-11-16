"""Quick debug to see D86 data from Riazi conversion"""
from bp_conversions import Oil

d2887_data = [
    [0, 160.0],
    [10, 180.5],
    [30, 205.0],
    [50, 225.0],
    [70, 245.0],
    [90, 270.0],
    [100, 290.0]
]

# Just do the D2887_to_D86 conversion
oil_obj = Oil.__new__(Oil)  # Create without __init__
from scipy.interpolate import PchipInterpolator

vol_distilled = [point[0] for point in d2887_data]
temperatures = [point[1] for point in d2887_data]
D2887_interp = PchipInterpolator(vol_distilled, temperatures)

riazi_coefficients = {
    0: (0.9800, 0.9960),
    10: (0.9200, 1.0050),
    30: (0.9000, 1.0100),
    50: (0.9050, 1.0150),
    70: (0.8900, 1.0190),
    90: (0.9650, 1.0080),
    100: (0.9800, 1.0000)
}

key_points = [0, 10, 30, 50, 70, 90, 100]
D86_points = {}

print("D2887 → D86 Conversion using Riazi-Daubert:")
print(f"{'Vol%':>6} {'D2887°C':>10} {'D2887°R':>12} {'a':>8} {'b':>8} {'D86°R':>12} {'D86°C':>10}")
print("-" * 80)

for vol in key_points:
    d2887_temp_C = D2887_interp(vol)
    d2887_temp_R = d2887_temp_C * 9/5 + 491.67
    
    a, b = riazi_coefficients[vol]
    d86_temp_R = (d2887_temp_R / a) ** (1/b)
    d86_temp_C = (d86_temp_R - 491.67) * 5/9
    
    D86_points[vol] = d86_temp_C
    print(f"{vol:>6} {d2887_temp_C:>10.2f} {d2887_temp_R:>12.2f} {a:>8.4f} {b:>8.4f} {d86_temp_R:>12.2f} {d86_temp_C:>10.2f}")

print("\nD86 Temperature Differences:")
print(f"{'From':>6} {'To':>6} {'ΔT':>10}")
print("-" * 30)
vol_list = sorted(D86_points.keys())
for i in range(len(vol_list)-1):
    v1, v2 = vol_list[i], vol_list[i+1]
    dt = D86_points[v2] - D86_points[v1]
    print(f"{v1:>6} {v2:>6} {dt:>10.2f}")
