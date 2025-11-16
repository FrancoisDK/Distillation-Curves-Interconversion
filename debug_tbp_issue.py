"""
Debug the TBP calculation to understand why it's lower than D2887 below 50%
"""
from bp_conversions import Oil

# Test data from screenshot
d2887_input = [
    [0, 160.0],
    [10, 176.7],
    [30, 193.3],
    [50, 206.7],
    [70, 222.8],
    [90, 243.9],
    [95, 251.0]
]

density = 800

print("=" * 80)
print("Debugging TBP Calculation from D2887 Input")
print("=" * 80)

oil = Oil(d2887_input, Density=density, input_type='D2887')

# Check the API constants used for D86→TBP conversion
API_constants = {
    0: (0.9167, 1.0019),
    10: (0.5277, 1.0900),
    30: (0.7429, 1.0425),
    50: (0.8920, 1.0176),
    70: (0.8705, 1.0226),
    90: (0.9490, 1.0110),
    95: (0.8008, 1.0355)
}

print("\nStep-by-step conversion at each volume%:")
print("-" * 80)
print(f"{'Vol%':<6} {'D2887→D86':<30} {'D86→TBP (API)':<40}")
print("-" * 80)

for vol in [0, 10, 30, 50, 70, 90]:
    d2887_c = oil.D2887_interp(vol)
    d86_c = oil.D86_interp(vol)
    tbp_c = oil.TBP_interp(vol)
    
    # Show the TBP calculation details
    a, b = API_constants[vol]
    d86_r = oil.convert_temperature(d86_c, 'C', 'R')
    tbp_r_calc = a * (d86_r ** b)
    tbp_c_calc = oil.convert_temperature(tbp_r_calc, 'R', 'C')
    
    print(f"{vol:<6} D2887={d2887_c:6.1f}°C → D86={d86_c:6.1f}°C", end="  ")
    print(f"D86={d86_r:6.1f}°R → TBP={tbp_r_calc:6.1f}°R={tbp_c_calc:6.1f}°C")
    print(f"       Δ(D2887-D86)={d2887_c-d86_c:+6.1f}°C", end="  ")
    print(f"Δ(TBP-D2887)={tbp_c-d2887_c:+6.1f}°C  [a={a:.4f}, b={b:.4f}]")

print("\n" + "=" * 80)
print("Analysis:")
print("=" * 80)
print("""
The problem is clear:
- At low vol% (0%, 10%), the API constant 'a' is very small (0.52-0.91)
- Combined with high exponent 'b' (1.09-1.02), this makes TBP much LOWER than D86!
- This is WRONG: TBP should always be HIGHER than D86

The API correlation TBP = a × D86^b has unusual constants at low vol%:
- At 10%: a=0.5277, b=1.0900  → TBP is 85% of D86 (too low!)
- At 50%: a=0.8920, b=1.0176  → TBP is 100% of D86 (correct)
- At 90%: a=0.9490, b=1.0110  → TBP is 105% of D86 (correct)

The issue is that these constants were developed for D86→TBP conversion,
and they may not work well in reverse (D2887→D86→TBP).

Solution: Need better D2887→D86 conversion that produces realistic D86 values.
""")
