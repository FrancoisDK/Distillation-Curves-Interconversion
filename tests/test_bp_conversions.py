"""
Unit tests for bp_conversions.py - Distillation Curve Conversions

Tests cover:
- All conversion paths (D86, D2887, TBP)
- Edge cases and bounds
- Round-trip accuracy
- Property calculations
- Temperature unit conversions
"""

import pytest
from bp_conversions import Oil
import math


class TestOilInitialization:
    """Test Oil class initialization with different input types"""
    
    def test_init_with_d86(self):
        """Test Oil initialization with D86 input"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        assert oil.input_type == 'D86'
        assert oil.Density == 820
        assert len(oil.D86) == 3
    
    def test_init_with_d2887(self):
        """Test Oil initialization with D2887 input"""
        data = [[0, 165], [50, 230], [100, 295]]
        oil = Oil(data, 820, 'D2887')
        
        assert oil.input_type == 'D2887'
        assert oil.Density == 820
        assert oil.D86 is not None  # Should be converted to D86
    
    def test_init_with_tbp(self):
        """Test Oil initialization with TBP input"""
        data = [[0, 165], [50, 235], [100, 300]]
        oil = Oil(data, 820, 'TBP')
        
        assert oil.input_type == 'TBP'
        assert oil.Density == 820
        assert oil.D86 is not None  # Should be converted to D86
    
    def test_init_with_invalid_type(self):
        """Test Oil initialization with invalid input type raises error"""
        data = [[0, 160], [50, 225], [100, 290]]
        
        with pytest.raises(ValueError):
            Oil(data, 820, 'INVALID')
    
    def test_init_creates_interpolators(self):
        """Test that Oil initialization creates all interpolators"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        assert oil.D86_interp is not None
        assert oil.D2887_interp is not None
        assert oil.TBP_interp is not None
        assert oil.Daubert_TBP_interp is not None


class TestTemperatureConversions:
    """Test temperature unit conversion functionality"""
    
    def test_celsius_to_fahrenheit(self):
        """Test C to F conversion"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        result = oil.convert_temperature(0, 'C', 'F')
        assert abs(result - 32) < 0.01
        
        result = oil.convert_temperature(100, 'C', 'F')
        assert abs(result - 212) < 0.01
    
    def test_fahrenheit_to_celsius(self):
        """Test F to C conversion"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        result = oil.convert_temperature(32, 'F', 'C')
        assert abs(result - 0) < 0.01
        
        result = oil.convert_temperature(212, 'F', 'C')
        assert abs(result - 100) < 0.01
    
    def test_celsius_to_kelvin(self):
        """Test C to K conversion"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        result = oil.convert_temperature(0, 'C', 'K')
        assert abs(result - 273.15) < 0.01
        
        result = oil.convert_temperature(100, 'C', 'K')
        assert abs(result - 373.15) < 0.01
    
    def test_case_insensitive_units(self):
        """Test that temperature conversion is case-insensitive"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        result1 = oil.convert_temperature(100, 'C', 'F')
        result2 = oil.convert_temperature(100, 'celsius', 'fahrenheit')
        assert abs(result1 - result2) < 0.01


class TestInterpolation:
    """Test interpolation accuracy at standard points"""
    
    def test_d86_interpolation_at_input_points(self):
        """Test D86 interpolation returns input values at input points"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # At input points, should return (approximately) the input values
        assert abs(oil.D86_interp(0) - 160) < 0.1
        assert abs(oil.D86_interp(50) - 225) < 0.1
        assert abs(oil.D86_interp(100) - 290) < 0.1
    
    def test_d86_interpolation_between_points(self):
        """Test D86 interpolation between points is monotonic"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # Check several points between 0 and 50
        temps = [oil.D86_interp(v) for v in range(0, 51, 10)]
        
        # Should be strictly increasing
        for i in range(len(temps) - 1):
            assert temps[i] < temps[i+1]
    
    def test_interpolation_bounds(self):
        """Test interpolation at curve boundaries"""
        data = [[0, 160], [30, 190], [60, 240], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # IBP (0%) should be close to input
        assert abs(oil.D86_interp(0) - 160) < 1
        
        # FBP (100%) should be close to input
        assert abs(oil.D86_interp(100) - 290) < 1


class TestConversionPhysics:
    """Test that conversions follow expected physical relationships"""
    
    def test_d86_less_than_d2887(self):
        """Test that D86 < D2887 at all points (D86 has heat loss)"""
        data = [[0, 160], [10, 170], [30, 190], [50, 225], [70, 260], [90, 280], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        for vol_pct in range(0, 101, 10):
            d86_temp = oil.D86_interp(vol_pct)
            d2887_temp = oil.D2887_interp(vol_pct)
            assert d86_temp < d2887_temp, f"At {vol_pct}%: D86 ({d86_temp}) should be < D2887 ({d2887_temp})"
    
    def test_d2887_less_than_tbp(self):
        """Test that D2887 < TBP at all points (TBP is theoretical)"""
        data = [[0, 160], [10, 170], [30, 190], [50, 225], [70, 260], [90, 280], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        for vol_pct in range(0, 101, 10):
            d2887_temp = oil.D2887_interp(vol_pct)
            tbp_temp = oil.TBP_interp(vol_pct)
            assert d2887_temp < tbp_temp, f"At {vol_pct}%: D2887 ({d2887_temp}) should be < TBP ({tbp_temp})"
    
    def test_d86_less_than_tbp(self):
        """Test that D86 < TBP at all points (combined effect)"""
        data = [[0, 160], [10, 170], [30, 190], [50, 225], [70, 260], [90, 280], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        for vol_pct in range(0, 101, 10):
            d86_temp = oil.D86_interp(vol_pct)
            tbp_temp = oil.TBP_interp(vol_pct)
            assert d86_temp < tbp_temp, f"At {vol_pct}%: D86 ({d86_temp}) should be < TBP ({tbp_temp})"
    
    def test_temperature_differences_realistic(self):
        """Test that temperature differences are physically realistic"""
        data = [[0, 160], [10, 170], [30, 190], [50, 225], [70, 260], [90, 280], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        for vol_pct in range(10, 100, 10):
            d86_temp = oil.D86_interp(vol_pct)
            d2887_temp = oil.D2887_interp(vol_pct)
            tbp_temp = oil.TBP_interp(vol_pct)
            
            # Typical differences
            d86_d2887_diff = d2887_temp - d86_temp
            d2887_tbp_diff = tbp_temp - d2887_temp
            
            # D86 is typically 3-7°C lower than D2887
            assert 0 < d86_d2887_diff < 15, f"At {vol_pct}%: D86-D2887 diff ({d86_d2887_diff}°C) seems unrealistic"
            
            # TBP is typically 0.5-2°C higher than D2887
            assert 0 < d2887_tbp_diff < 10, f"At {vol_pct}%: D2887-TBP diff ({d2887_tbp_diff}°C) seems unrealistic"


class TestPropertyCalculations:
    """Test petroleum property calculations"""
    
    def test_vabp_calculation(self):
        """Test VABP (Volume Average Boiling Point) calculation"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # VABP should be reasonable
        assert 160 < oil.VABP < 600  # In Fahrenheit
        assert oil.VABP > 0
    
    def test_meabp_calculation(self):
        """Test MeABP (Mean Average Boiling Point) calculation"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # MeABP should be reasonable
        assert 160 < oil.MeABP < 290  # In Celsius
        assert oil.MeABP > 0
    
    def test_watson_k_calculation(self):
        """Test Watson K characterization factor"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # Watson K typical range for oils: 11-14
        assert 10 < oil.WatsonK < 15
    
    def test_properties_change_with_density(self):
        """Test that properties vary with density (as expected)"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil_light = Oil(data, 750, 'D86')
        oil_heavy = Oil(data, 850, 'D86')
        
        # Watson K should be different for different densities
        assert oil_light.WatsonK != oil_heavy.WatsonK


class TestRoundTripConversions:
    """Test round-trip conversions (D86 -> X -> D86)"""
    
    def test_d86_to_d2887_to_d86(self):
        """Test D86 -> D2887 -> D86 round trip accuracy"""
        original_data = [[0, 160], [10, 170], [30, 190], [50, 225], [70, 260], [90, 280], [100, 290]]
        oil_d86 = Oil(original_data, 820, 'D86')
        
        # Extract D2887 at same % points
        d2887_data = [[p[0], oil_d86.D2887_interp(p[0])] for p in original_data]
        
        # Convert back to D86
        oil_back = Oil(d2887_data, 820, 'D2887')
        
        # Check that we're close to original (within ~1-2°C due to interpolation)
        for vol_pct in [0, 50, 100]:
            original_temp = oil_d86.D86_interp(vol_pct)
            roundtrip_temp = oil_back.D86_interp(vol_pct)
            diff = abs(original_temp - roundtrip_temp)
            assert diff < 3, f"At {vol_pct}%: Round-trip error ({diff}°C) too large"
    
    def test_d86_to_tbp_to_d86(self):
        """Test D86 -> TBP -> D86 round trip accuracy"""
        original_data = [[0, 160], [10, 170], [30, 190], [50, 225], [70, 260], [90, 280], [100, 290]]
        oil_d86 = Oil(original_data, 820, 'D86')
        
        # Extract TBP at same % points
        tbp_data = [[p[0], oil_d86.TBP_interp(p[0])] for p in original_data]
        
        # Convert back to D86
        oil_back = Oil(tbp_data, 820, 'TBP')
        
        # Check that we're close to original (within ~2-3°C due to interpolation)
        for vol_pct in [0, 50, 100]:
            original_temp = oil_d86.D86_interp(vol_pct)
            roundtrip_temp = oil_back.D86_interp(vol_pct)
            diff = abs(original_temp - roundtrip_temp)
            assert diff < 4, f"At {vol_pct}%: Round-trip error ({diff}°C) too large"


class TestDensityBounds:
    """Test behavior at density limits"""
    
    def test_light_oil_density(self):
        """Test with light oil (low density)"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 600, 'D86')  # Light oil
        
        assert oil.Density == 600
        assert oil.WatsonK > 0
    
    def test_heavy_oil_density(self):
        """Test with heavy oil (high density)"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 1200, 'D86')  # Heavy oil
        
        assert oil.Density == 1200
        assert oil.WatsonK > 0
    
    def test_typical_crude_density(self):
        """Test with typical crude oil density"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')  # Typical
        
        assert oil.Density == 820
        assert 11 < oil.WatsonK < 14


class TestMinimalDataSets:
    """Test with minimal (3 point) data"""
    
    def test_three_point_conversion(self):
        """Test conversion with minimum 3 data points"""
        data = [[0, 160], [50, 225], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # Should work with just 3 points
        assert oil.D86_interp(25) > 160
        assert oil.D86_interp(25) < 225
        assert oil.D86_interp(75) > 225
        assert oil.D86_interp(75) < 290


class TestDifferentConversionMethods:
    """Test different conversion method options"""
    
    def test_api_vs_daubert_tbp(self):
        """Test that API and Daubert TBP methods give different results"""
        data = [[0, 160], [10, 170], [30, 190], [50, 225], [70, 260], [90, 280], [100, 290]]
        oil = Oil(data, 820, 'D86')
        
        # API and Daubert TBP should be different
        api_tbp = oil.TBP_interp(50)
        daubert_tbp = oil.Daubert_TBP_interp(50)
        
        # They should be close but not identical
        assert abs(api_tbp - daubert_tbp) > 0.1
        assert abs(api_tbp - daubert_tbp) < 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
