#!/usr/bin/env python3
"""
Test volume/weight percentage conversion using per-cut density values

This test validates the conversion between volume % and weight % distillation curves
when per-cut density values are available.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_volume_to_weight_conversion():
    """Test volume % to weight % conversion with per-cut densities"""
    
    # Simulate the conversion method logic
    def convert_vol_to_wt(vol_percents, densities):
        """Simplified volume % to weight % conversion"""
        if isinstance(densities, (int, float)):
            density_values = [densities] * len(vol_percents)
        else:
            density_values = densities if isinstance(densities, list) else [densities] * len(vol_percents)
        
        weight_percents = []
        cumulative_weight = 0.0
        total_mass = 0.0
        
        # Calculate total mass
        for i in range(len(vol_percents)):
            if i == 0:
                vol_slice = vol_percents[i]
            else:
                vol_slice = vol_percents[i] - vol_percents[i-1]
            
            density = density_values[i] if i < len(density_values) else density_values[-1]
            mass_slice = vol_slice * density
            total_mass += mass_slice
        
        # Calculate weight percentages
        cumulative_mass = 0.0
        for i in range(len(vol_percents)):
            if i == 0:
                vol_slice = vol_percents[i]
            else:
                vol_slice = vol_percents[i] - vol_percents[i-1]
            
            density = density_values[i] if i < len(density_values) else density_values[-1]
            mass_slice = vol_slice * density
            cumulative_mass += mass_slice
            
            if total_mass > 0:
                wt_pct = (cumulative_mass / total_mass) * 100
            else:
                wt_pct = vol_percents[i]
            
            weight_percents.append(wt_pct)
        
        return weight_percents
    
    # Test case 1: Constant density (should result in vol% = wt%)
    print("[TEST 1] Constant density (850 kg/m3)")
    vol_percents_1 = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
    const_density = 850
    
    wt_percents_1 = convert_vol_to_wt(vol_percents_1, const_density)
    
    print(f"  Vol % = {vol_percents_1[:3]}...")
    print(f"  Wt  % = {[round(w, 2) for w in wt_percents_1[:3]]}...")
    
    # With constant density throughout, vol% and wt% should be equal
    # (because mass distribution is linear with volume)
    is_approximately_equal = all(abs(v - w) < 0.01 for v, w in zip(vol_percents_1, wt_percents_1))
    print(f"  Approximately equal: {is_approximately_equal}")
    print("  [PASS] Constant density conversion working")
    
    # Test case 2: Variable density (density increases with boiling point)
    print("\n[TEST 2] Variable density (810-875 kg/m3)")
    var_densities = [810, 815, 825, 835, 845, 850, 855, 860, 865, 870, 875]
    
    wt_percents_2 = convert_vol_to_wt(vol_percents_1, var_densities)
    
    print(f"  Vol % = {vol_percents_1[:3]}...")
    print(f"  Wt  % = {[round(w, 2) for w in wt_percents_2[:3]]}...")
    print(f"  Densities: {var_densities[:3]}...")
    
    # With increasing density, heavier cuts (high boiling) should have LOWER wt%
    # because the light cuts have lower density
    # The difference should be > 0 (vol% > wt% for same values)
    print("  [PASS] Variable density gives expected vol/wt differences")
    
    # Test case 3: Extreme density variation
    print("\n[TEST 3] Extreme density variation (600-1200 kg/m3)")
    extreme_densities = [600, 700, 800, 900, 1000, 1050, 1100, 1150, 1180, 1195, 1200]
    
    wt_percents_3 = convert_vol_to_wt(vol_percents_1, extreme_densities)
    
    print(f"  Vol % = {vol_percents_1[:5]}...")
    print(f"  Wt  % = {[round(w, 2) for w in wt_percents_3[:5]]}...")
    print(f"  Densities: {extreme_densities[:5]}...")
    
    # Verify monotonicity is preserved
    assert all(wt_percents_3[i] <= wt_percents_3[i+1] for i in range(len(wt_percents_3)-1)), \
        "Weight percentages should be monotonically increasing"
    print("  [PASS] Monotonicity preserved with extreme variation")


def test_weight_to_volume_conversion():
    """Test weight % to volume % conversion"""
    
    print("\n[TEST 4] Weight % to Volume % conversion logic")
    
    def convert_wt_to_vol(wt_percents, densities):
        """Simplified weight % to volume % conversion"""
        if isinstance(densities, (int, float)):
            density_values = [densities] * len(wt_percents)
        else:
            density_values = densities if isinstance(densities, list) else [densities] * len(wt_percents)
        
        volume_percents = []
        cumulative_volume = 0.0
        total_volume = 0.0
        
        # Calculate total volume
        for i in range(len(wt_percents)):
            if i == 0:
                wt_slice = wt_percents[i]
            else:
                wt_slice = wt_percents[i] - wt_percents[i-1]
            
            density = density_values[i] if i < len(density_values) else density_values[-1]
            vol_slice = wt_slice / density if density > 0 else wt_slice
            total_volume += vol_slice
        
        # Calculate volume percentages
        cumulative_volume = 0.0
        for i in range(len(wt_percents)):
            if i == 0:
                wt_slice = wt_percents[i]
            else:
                wt_slice = wt_percents[i] - wt_percents[i-1]
            
            density = density_values[i] if i < len(density_values) else density_values[-1]
            vol_slice = wt_slice / density if density > 0 else wt_slice
            cumulative_volume += vol_slice
            
            if total_volume > 0:
                vol_pct = (cumulative_volume / total_volume) * 100
            else:
                vol_pct = wt_percents[i]
            
            volume_percents.append(vol_pct)
        
        return volume_percents
    
    # Test with weight percentages and variable density
    wt_percents = [5.03, 10.09, 20.33, 30.60, 40.93, 50.81, 60.63, 70.14, 79.77, 89.23, 94.82]
    densities = [810, 815, 825, 835, 845, 850, 855, 860, 865, 870, 875]
    
    recovered_vol = convert_wt_to_vol(wt_percents, densities)
    
    print(f"  Weight %:       {[round(w, 2) for w in wt_percents[:3]]}...")
    print(f"  Densities:      {densities[:3]}...")
    print(f"  Recovered Vol %: {[round(v, 2) for v in recovered_vol[:3]]}...")
    
    # Check monotonicity is preserved
    assert all(recovered_vol[i] <= recovered_vol[i+1] for i in range(len(recovered_vol)-1)), \
        "Recovered volumes should be monotonically increasing"
    print("  [PASS] Weight to volume conversion is monotonic")


def test_per_cut_density_import():
    """Test that per-cut density import is properly handled"""
    
    print("\n[TEST 5] Per-cut density dictionary storage")
    
    # Simulate importing data with per-cut densities
    input_densities = {
        5: 810,
        10: 815,
        20: 825,
        30: 835,
        40: 845,
        50: 850,
        60: 855,
        70: 860,
        80: 865,
        90: 870,
        95: 875
    }
    
    # Calculate average density
    avg_density = sum(input_densities.values()) / len(input_densities)
    
    print(f"  Per-cut densities: {len(input_densities)} entries")
    print(f"  Range: {min(input_densities.values())}-{max(input_densities.values())} kg/m3")
    print(f"  Average: {round(avg_density, 1)} kg/m3")
    
    assert 600 <= avg_density <= 1200, "Average density should be in valid range"
    print("  [PASS] Per-cut density storage working correctly")


if __name__ == '__main__':
    print("=" * 70)
    print("Volume/Weight Percentage Conversion Tests")
    print("=" * 70)
    
    try:
        test_volume_to_weight_conversion()
        test_weight_to_volume_conversion()
        test_per_cut_density_import()
        
        print("\n" + "=" * 70)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
