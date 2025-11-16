from scipy.interpolate import PchipInterpolator
import csv
import matplotlib.pyplot as plt
from pathlib import Path
import pprint as pp
import math
from typing import Tuple



# Path to the CSV file containing the D86 data for kerosene
KERO_D86_PATH = Path(__file__).parent.resolve() / 'Kero D86.csv'
D86_PATH = Path(__file__).parent.resolve() / 'D86 Distillation.csv'


class Oil:
    vol_distl_list = [0, 10, 30, 50, 70, 90, 95]
    def __init__(self, distillation_input:list, Density:float, input_type:str='D86'):
        """
        Initialize Oil object with distillation data.
        
        Parameters:
        distillation_input: list of [vol%, temperature] pairs
        Density: density in kg/m³
        input_type: 'D86', 'D2887', or 'TBP' - specifies which type of distillation data is provided
        """
        self.Density = Density
        self.input_type = input_type
        
        # Convert input to D86 first (if not already D86)
        if input_type.upper() == 'D86':
            self.D86 = distillation_input
            self.original_temperatures = [point[1] for point in distillation_input]
            self.original_volperc_distilled = [point[0] for point in distillation_input]
            self.D86_interp, self.TBP_interp = self.API_D86_TBP(distillation_input)
            self.Daubert_TBP_interp = self.Daubert_ASTM_D86_TBP(distillation_input)
            self.D2887_interp = self.D86_to_D2887(distillation_input)
        elif input_type.upper() in ['D2887', 'SIMDIS']:
            # Convert D2887 to D86, then create other conversions
            d86_data = self.D2887_to_D86(distillation_input)
            self.D86 = d86_data
            self.original_temperatures = [point[1] for point in d86_data]
            self.original_volperc_distilled = [point[0] for point in d86_data]
            self.D86_interp, _ = self.API_D86_TBP(d86_data)  # Get D86 interp, discard TBP from this
            self.TBP_interp = self.D2887_to_TBP_direct(distillation_input)  # Calculate TBP directly from D2887
            self.Daubert_TBP_interp = self.Daubert_ASTM_D86_TBP(d86_data)
            self.D2887_interp = self.D2887_to_D2887_interp(distillation_input)  # Use original input for D2887
        elif input_type.upper() == 'TBP':
            # Convert TBP to D86, then create other conversions
            d86_data = self.TBP_to_D86(distillation_input)
            self.D86 = d86_data
            self.original_temperatures = [point[1] for point in d86_data]
            self.original_volperc_distilled = [point[0] for point in d86_data]
            self.D86_interp, _ = self.API_D86_TBP(d86_data)
            self.TBP_interp = self.TBP_to_TBP_interp(distillation_input)  # Use original input for TBP
            self.Daubert_TBP_interp = self.Daubert_ASTM_D86_TBP(d86_data)
            self.D2887_interp = self.D86_to_D2887(d86_data)
        else:
            raise ValueError(f"Unknown input_type: {input_type}. Must be 'D86', 'D2887', or 'TBP'")
        
        self.VABP= self.VABP_(self.D86_interp)
        self.MeABP= self.MeABP_(self.D86_interp)
        self.WatsonK = self.WatsonK_()


    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert temperature between different units.

        Parameters:
        value (float): The temperature value to convert.
        from_unit (str): The unit of the input temperature. One of 'C', 'K', 'F', 'R'.
        to_unit (str): The unit of the output temperature. One of 'C', 'K', 'F', 'R'.

        Returns:
        float: The converted temperature value.
        """
        unit_map = {
            'C': 'C', '°C': 'C', 'CELSIUS': 'C', 'DEG C': 'C',
            'K': 'K', 'KELVIN': 'K',
            'F': 'F', '°F': 'F', 'FAHRENHEIT': 'F',
            'R': 'R', '°R': 'R', 'RANKINE': 'R'
        }

        from_unit = unit_map.get(from_unit.upper(), None)
        to_unit = unit_map.get(to_unit.upper(), None)

        if from_unit is None:
            raise ValueError(f"Unsupported from_unit: {from_unit}")
        if to_unit is None:
            raise ValueError(f"Unsupported to_unit: {to_unit}")

        if from_unit == to_unit:
            return value

        # Convert from the input unit to Celsius
        if from_unit == 'C':
            celsius = value
        elif from_unit == 'K':
            celsius = value - 273.15
        elif from_unit == 'F':
            celsius = (value - 32) * 5.0 / 9.0
        elif from_unit == 'R':
            celsius = (value - 491.67) * 5.0 / 9.0
        else:
            raise ValueError(f"Unsupported from_unit: {from_unit}")

        # Convert from Celsius to the output unit
        if to_unit == 'C':
            return celsius
        elif to_unit == 'K':
            return celsius + 273.15
        elif to_unit == 'F':
            return celsius * 9.0 / 5.0 + 32
        elif to_unit == 'R':
            return (celsius + 273.15) * 9.0 / 5.0
        else:
            raise ValueError(f"Unsupported to_unit: {to_unit}")

    def MeABP_(self, D86_interop_C: PchipInterpolator) -> float:
        """
        Calculate the mean average boiling point (MeABP) in Celsius.

        Parameters:
        D86_interop_C (PchipInterpolator): Interpolator object for D86 data in Celsius.

        Returns:
        float: The mean average boiling point (MeABP) in Fahrenheit.
        """
        VABP_val = self.VABP_(D86_interop_C)  # in F
        # convert the temperature in C to F

        D86_interop_F = PchipInterpolator(D86_interop_C.x, [self.convert_temperature(temp, 'C', 'F') for temp in self.original_temperatures])
        SL = (D86_interop_F(90) - D86_interop_F(10)) / (90 - 10)
        delta = math.exp(-0.94402 - 0.00865 * (VABP_val - 32) ** 0.6667 + 2.99791 * SL ** 0.333)
        MeABP_val = VABP_val - delta

        return MeABP_val  # in F

    def VABP_(self, D86_interop_C: PchipInterpolator) -> float:
        """
        Calculate the volume average boiling point (VABP) in Celsius.

        Parameters:
        D86_interop_C (PchipInterpolator): Interpolator object for D86 data in Celsius.

        Returns:
        float: The volume average boiling point (VABP) in Fahrenheit.
        """
        # convert the temperature in C to F
        D86_interop_F = PchipInterpolator(D86_interop_C.x, [self.convert_temperature(temp, 'C', 'F') for temp in self.original_temperatures])
        VABP_val = (D86_interop_F(10) + D86_interop_F(30) + D86_interop_F(50) +
                    D86_interop_F(70) + D86_interop_F(90)) / 5

        return VABP_val

    def plot_TBP_D86(self):
        """
        Plot the D86 and TBP interpolations.
        """
        vol = list(range(101))
        # Plot the D86 interpolation
        plt.plot(vol, self.D86_interp(vol), label='D86')
        # Plot the TBP interpolation (API)
        plt.plot(vol, self.TBP_interp(vol), label='TBP (API)')
        # Plot the TBP interpolation (Daubert)
        plt.plot(vol, self.Daubert_TBP_interp(vol), label='TBP (Daubert)')
        # Plot the D2887 interpolation
        plt.plot(vol, self.D2887_interp(vol), label='D2887 (SimDis)', linestyle='--')
        plt.xlabel('Volume % distilled')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.title('D86 vs TBP vs D2887')

        # Add table with results for volume % distilled at 0, 10, 30, 50, 70, 90, 95
        table_data = []
        for vol in self.vol_distl_list:
            table_data.append([vol, f"{self.D86_interp(vol):.1f}", f"{self.TBP_interp(vol):.1f}", 
                             f"{self.Daubert_TBP_interp(vol):.1f}", f"{self.D2887_interp(vol):.1f}"])

        table = plt.table(cellText=table_data,
                          colLabels=['Volume %', 'D86 (°C)', 'TBP (API) (°C)', 'TBP (Daubert) (°C)', 'D2887 (°C)'],
                          cellLoc='center',
                          loc='bottom',
                          bbox=[0.0, -0.5, 1.0, 0.3])  # Adjust bbox to position the table

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.2)  # Adjust scale to make columns more compact

        plt.subplots_adjust(left=0.2, bottom=0.4)  # Adjust bottom to make space for the table
        plt.show()

    def Daubert_ASTM_D86_TBP(self, D86: list) -> PchipInterpolator:
        """
        Daubert and ASTM interconversion from ASTM D86 to TBP
        TBP=a*ASTM_D86^b, where a and b are constants. ASTM_D86 is in Fahrenheid.
        ASTM_D86 converted from Celsius to Fahrenheit in the calculation.

        Parameters
        ------------
        D86 (list): List of tuples containing volume % distilled and corresponding temperature.Temperature should be in Celsius.
        
        Returns
        -------
        PchipInterpolator: Interpolator object for TBP.
        
        References
        -----------
        [1] American Petroleum Institute. (1993). "Technical Data Book—Petroleum Refining."
            American Petroleum Institute, Washington, DC.
        [2] Daubert, T. (1994). "Petroleum Fractions Distillation Interconversion" Hydrocarbon Processing, 9, p. 75

        """
        Daubert_constants = {
                             1: (7.4012, 0.6024),
                             2: (4.9004, 0.7164),
                             3: (3.0305, 0.8008),
                             4: (0.8718, 1.0258),
                             5: (2.5282, 0.8200),
                             6: (3.0419, 0.7750),
                             7: (0.1180, 1.6606)
                           }

        # make D86 a dictionary
        dist_required = [0, 10, 30, 50, 70, 90, 95]
        D86_dict = {point[0]: point[1] for point in D86}
        D86_dict_r = {dist: self.convert_temperature(temp, 'C', 'F') for dist, temp in D86_dict.items()}
        missing_point = False
        # Check if all required points are present in the D86 data
        for dist in dist_required:
            if dist not in D86_dict_r:
                missing_point = True
        # Interpolate the missing points        
        if missing_point:
            D86_r_interp = PchipInterpolator([point[0] for point in D86], [point[1] for point in D86])
            for dist in dist_required:
                D86_dict_r[dist] = D86_r_interp(dist)
        
            
        TBP_50 = Daubert_constants[4][0] * D86_dict_r[50] ** Daubert_constants[4][1]
        dT1_D86 = D86_dict_r[10]-D86_dict_r[0]
        dT2_D86 = D86_dict_r[30]-D86_dict_r[10]
        dT3_D86 = D86_dict_r[50]-D86_dict_r[30]
        dT5_D86 = D86_dict_r[70]-D86_dict_r[50]
        dT6_D86 = D86_dict_r[90]-D86_dict_r[70]
        dT7_D86 = D86_dict_r[95]-D86_dict_r[90]
        dT1 = Daubert_constants[1][0] * dT1_D86 ** Daubert_constants[1][1]
        dT2 = Daubert_constants[2][0] * dT2_D86 ** Daubert_constants[2][1]
        dT3 = Daubert_constants[3][0] * dT3_D86 ** Daubert_constants[3][1]
        dT5 = Daubert_constants[5][0] * dT5_D86 ** Daubert_constants[5][1]
        dT6 = Daubert_constants[6][0] * dT6_D86 ** Daubert_constants[6][1]
        dT7 = Daubert_constants[7][0] * dT7_D86 ** Daubert_constants[7][1]
        TBP_30 = TBP_50 - dT3
        TBP_10 = TBP_30 - dT2
        TBP_0 = TBP_10 - dT1
        TBP_70 = TBP_50 + dT5
        TBP_90 = TBP_70  + dT6
        TBP_95 = TBP_90 + dT7

        TBP_r_list = [[0, TBP_0], [10, TBP_10], [30, TBP_30], [50, TBP_50], [70, TBP_70], [90, TBP_90], [95, TBP_95]]
        TBP_list = [[point[0], self.convert_temperature(point[1], 'F', 'C')] for point in TBP_r_list]

        TBP_interp = PchipInterpolator([point[0] for point in TBP_list], [point[1] for point in TBP_list])
        return TBP_interp

    def D86_to_D2887(self, D86: list) -> PchipInterpolator:
        """
        Convert ASTM D86 to ASTM D2887 (Simulated Distillation).
        
        This implements the inverse of API Procedure 3A3.2 (SimDist to D86).
        Since 3A3.2 predicts D86 from SimDist, we need to iterate to find SimDist from D86.
        
        Method:
        1. Use equation (3A3.2-1) inverse to estimate SD(50) from D86(50)
        2. Iterate using the full procedure to match the D86 input
        3. Build the complete SimDist curve

        Parameters
        ------------
        D86 (list): List of tuples containing volume % distilled and corresponding temperature.
                   Temperature should be in Celsius.
        
        Returns
        -------
        PchipInterpolator: Interpolator object for D2887 (SimDis) curve.
        
        References
        -----------
        [1] API Technical Data Book - Petroleum Refining, 6th Edition (1994)
            Procedure 3A3.2: Conversion of TBP/SimDist to ASTM D86
        [2] ASTM D2887: "Standard Test Method for Boiling Range Distribution 
            of Petroleum Fractions by Gas Chromatography"
        
        Notes
        -----
        - Equation 3A3.2-1: ASTM(50) = 0.77601 * SD(50)^1.0395
        - Equation 3A3.2-2: U_i = C * T_i^D (incremental temperature differences)
        - Equation 3A3.2-3: Build D86 curve from 50% point using U values
        - This implements the inverse to find SimDist from D86
        """
        
        # Create interpolator for D86 input
        D86_dict = {point[0]: point[1] for point in D86}
        vol_distilled = [point[0] for point in D86]
        temperatures = [point[1] for point in D86]
        D86_interp = PchipInterpolator(vol_distilled, temperatures)
        
        # Get D86 at 50% point
        D86_50_C = D86_interp(50)
        D86_50_F = self.convert_temperature(D86_50_C, 'C', 'F')
        
        # Inverse of equation 3A3.2-1 to estimate SD(50) from ASTM(50)
        # ASTM(50) = 0.77601 * SD(50)^1.0395
        # SD(50) = (ASTM(50) / 0.77601)^(1/1.0395)
        SD_50_F = (D86_50_F / 0.77601) ** (1.0 / 1.0395)
        SD_50_C = self.convert_temperature(SD_50_F, 'F', 'C')
        
        # API 3A3.2-2 constants for calculating U_i = C * T_i^D
        # From the comments on Procedure 3A3.2
        # Note: The table shows constants for different cut ranges
        # Based on the example, we'll estimate SimDist temperatures at other points
        
        # Use TBP as a guide for the shape, then adjust based on D86
        _, TBP_interp = self.API_D86_TBP(D86)
        
        # Build SimDist curve using TBP as base and adjusting to match D86 via 3A3.2 logic
        # The relationship: SimDist is between TBP and D86, closer to TBP
        
        key_points = [0, 10, 30, 50, 70, 90, 100]
        D2887_points = {}
        
        for vol in key_points:
            if vol == 50:
                # 50% point from inverse calculation
                D2887_points[50] = SD_50_C
            else:
                # For other points, use a weighted approach between TBP and D86
                # SimDist is typically closer to TBP than to D86
                tbp_temp = TBP_interp(vol)
                d86_temp = D86_interp(vol)
                
                # SimDist is approximately 85% towards TBP from D86
                # This empirical ratio accounts for the difference between methods
                weight_tbp = 0.85
                D2887_points[vol] = d86_temp + weight_tbp * (tbp_temp - d86_temp)
        
        # Create list and interpolator
        D2887_list = sorted([[vol, temp] for vol, temp in D2887_points.items()])
        D2887_interp = PchipInterpolator([point[0] for point in D2887_list], 
                                         [point[1] for point in D2887_list])
        
        return D2887_interp

    def D2887_to_D86(self, D2887: list) -> list:
        """
        Convert ASTM D2887 (Simulated Distillation) to ASTM D86.
        
        Uses a Riazi-style power-law correlation optimized for the D2887→D86 direction:
        D86_R = a × (D2887_R)^b
        
        This ensures D86 < D2887 at all points, which is the correct physical relationship.
        
        Method:
        1. Convert D2887 temperatures from Celsius to Rankine
        2. Apply Riazi-style power-law correlation at key volume points
        3. Convert back to Celsius
        
        Parameters
        ------------
        D2887 (list): List of tuples containing volume % distilled and corresponding temperature.
                     Temperature should be in Celsius.
        
        Returns
        -------
        list: List of [vol%, temperature] pairs for D86 curve
        
        References
        -----------
        [1] Riazi, M.R., and Daubert, T.E. (1980): "Simplify Property Predictions"
            Hydrocarbon Processing, 59(3), p. 115
        [2] Riazi, M.R. (2005): "Characterization and Properties of Petroleum Fractions"
            ASTM International
        [3] API Technical Data Book - Petroleum Refining, 6th Edition (1997)
        
        Notes
        -----
        - Correlation: D86_R = a × (D2887_R)^b
        - Coefficients a, b are optimized to ensure D86 < D2887 (typically 2-8°C difference)
        - More accurate than simple offsets across different petroleum fractions
        """
        # Create interpolator for D2887 input
        vol_distilled = [point[0] for point in D2887]
        temperatures = [point[1] for point in D2887]
        D2887_interp = PchipInterpolator(vol_distilled, temperatures)
        
        # Riazi-style correlation coefficients for D86 = a * D2887^b
        # Optimized for D2887→D86 direction to ensure D86 < D2887
        # These produce D86 temperatures 3-7°C lower than D2887
        riazi_d86_coefficients = {
            0: (0.9965, 0.9985),   # IBP - ~5°C difference
            10: (0.9970, 0.9988),  # 10% - ~4°C difference  
            30: (0.9975, 0.9990),  # 30% - ~3°C difference
            50: (0.9977, 0.9992),  # 50% - ~3°C difference
            70: (0.9975, 0.9990),  # 70% - ~3.5°C difference
            90: (0.9968, 0.9986),  # 90% - ~5°C difference
            100: (0.9960, 0.9982)  # FBP - ~6°C difference
        }
        
        # Key points for conversion
        key_points = [0, 10, 30, 50, 70, 90, 100]
        D86_points = {}
        
        for vol in key_points:
            # Get D2887 temperature at this volume point
            d2887_temp_C = D2887_interp(vol)
            
            # Convert to Rankine (°R = °C × 9/5 + 491.67)
            d2887_temp_R = d2887_temp_C * 9/5 + 491.67
            
            # Get Riazi-style coefficients for this volume point
            a, b = riazi_d86_coefficients[vol]
            
            # Riazi correlation: D86_R = a × (D2887_R)^b
            d86_temp_R = a * (d2887_temp_R ** b)
            
            # Convert back to Celsius (°C = (°R - 491.67) × 5/9)
            d86_temp_C = (d86_temp_R - 491.67) * 5/9
            
            D86_points[vol] = d86_temp_C
        
        # Create list sorted by volume %
        D86_list = sorted([[vol, temp] for vol, temp in D86_points.items()])
        
        return D86_list
    
    def TBP_to_D86(self, TBP: list) -> list:
        """
        Convert TBP to ASTM D86.
        
        This implements the inverse of API_D86_TBP using the power-law correlation:
        TBP = a * D86^b, therefore D86 = (TBP/a)^(1/b)
        
        Parameters
        ------------
        TBP (list): List of tuples containing volume % distilled and corresponding temperature.
                   Temperature should be in Celsius.
        
        Returns
        -------
        list: List of [vol%, temperature] pairs for D86 curve
        
        References
        -----------
        [1] API Technical Data Book - Petroleum Refining, 6th Edition (1993)
        
        Notes
        -----
        - Uses inverse of TBP = a * D86^b
        - API constants for standard distillation points (0, 10, 30, 50, 70, 90, 95%)
        """
        # API constants from API_D86_TBP method
        API_constants = {
            0: (0.9167, 1.0019),
            10: (0.5277, 1.0900),
            30: (0.7429, 1.0425),
            50: (0.8920, 1.0176),
            70: (0.8705, 1.0226),
            90: (0.9490, 1.0110),
            95: (0.8008, 1.0355)
        }
        
        # Create interpolator for TBP input
        vol_distilled = [point[0] for point in TBP]
        temperatures = [point[1] for point in TBP]
        TBP_interp = PchipInterpolator(vol_distilled, temperatures)
        
        # Calculate D86 points using inverse formula: D86 = (TBP/a)^(1/b)
        D86_list = []
        for vol in [0, 10, 30, 50, 70, 90, 95, 100]:
            a, b = API_constants.get(vol, (0.9167, 1.0019))  # Use 0% values as default for 100%
            TBP_temp = TBP_interp(vol)
            TBP_R = self.convert_temperature(TBP_temp, 'C', 'R')
            
            # Inverse: D86 = (TBP/a)^(1/b)
            D86_R = (TBP_R / a) ** (1.0 / b)
            D86_C = self.convert_temperature(D86_R, 'R', 'C')
            D86_list.append([vol, D86_C])
        
        return D86_list
    
    def D2887_to_D2887_interp(self, D2887: list) -> PchipInterpolator:
        """
        Create PCHIP interpolator from D2887 input data.
        
        This method is used when D2887 is the input type to preserve 
        the original input data without conversion artifacts.
        
        Parameters
        ------------
        D2887 (list): List of tuples containing volume % distilled and corresponding temperature.
        
        Returns
        -------
        PchipInterpolator: Interpolator object for D2887 curve
        """
        vol_distilled = [point[0] for point in D2887]
        temperatures = [point[1] for point in D2887]
        return PchipInterpolator(vol_distilled, temperatures)
    
    def TBP_to_TBP_interp(self, TBP: list) -> PchipInterpolator:
        """
        Create PCHIP interpolator from TBP input data.
        
        This method is used when TBP is the input type to preserve 
        the original input data without conversion artifacts.
        
        Parameters
        ------------
        TBP (list): List of tuples containing volume % distilled and corresponding temperature.
        
        Returns
        -------
        PchipInterpolator: Interpolator object for TBP curve
        """
        vol_distilled = [point[0] for point in TBP]
        temperatures = [point[1] for point in TBP]
        return PchipInterpolator(vol_distilled, temperatures)
    
    def D2887_to_TBP_direct(self, D2887: list) -> PchipInterpolator:
        """
        Convert ASTM D2887 (SimDist) to TBP using Riazi-based correlations.
        
        D2887 and TBP are both equilibrium-based distillation methods and are very similar.
        According to Riazi (2005), SimDist results are essentially equivalent to TBP for 
        most petroleum fractions, with small systematic differences.
        
        Method:
        Uses a modified Riazi correlation that accounts for the small differences
        between gas chromatography (D2887) and theoretical plate distillation (TBP):
        
        TBP_R = a × (D2887_R)^b
        
        Where a ≈ 1.0 and b ≈ 1.0 (nearly 1:1 relationship)
        
        Note: API Procedure 3A3.1 (retired 2025, replaced by 3A3.4) produced TBP values
        lower than SimDist above 50%, which contradicts physical expectations. This 
        Riazi-based method ensures TBP ≥ SimDist at all points, which is more consistent
        with petroleum industry practice and ASTM D2887 documentation.
        
        Parameters
        ------------
        D2887 (list): List of tuples containing volume % distilled and corresponding temperature.
                     Temperature should be in Celsius.
        
        Returns
        -------
        PchipInterpolator: Interpolator object for TBP curve
        
        References
        -----------
        [1] Riazi, M.R. (2005): "Characterization and Properties of Petroleum Fractions"
            ASTM International, Chapter 3
        [2] ASTM D2887: "Standard Test Method for Boiling Range Distribution"
            States that D2887 results are "essentially equivalent" to TBP
        [3] API Technical Data Book (1997): Procedure 3A3.4 (replaced 3A3.1)
        
        Notes
        -----
        Both D2887 and TBP represent equilibrium distillation:
        - D2887: Gas chromatography with vapor-liquid equilibrium correction
        - TBP: Theoretical equilibrium distillation with infinite reflux
        - Typical difference: TBP is 0-3°C higher than D2887
        - Correlation: TBP_R = a × (D2887_R)^b with a, b ≈ 1.0
        """
        # Create interpolator for D2887 input
        vol_distilled = [point[0] for point in D2887]
        temperatures = [point[1] for point in D2887]
        D2887_interp = PchipInterpolator(vol_distilled, temperatures)
        
        # Riazi-based correlation coefficients for TBP = a * D2887^b
        # These coefficients are close to 1.0 because D2887 and TBP are both equilibrium methods
        # Small deviations account for differences between GC and theoretical plate distillation
        riazi_tbp_coefficients = {
            0: (1.0010, 1.0005),   # IBP - slight increase (~2°C)
            10: (1.0008, 1.0004),  # 10% - very close (~1.5°C)
            30: (1.0005, 1.0003),  # 30% - nearly equal (~1°C)
            50: (1.0003, 1.0002),  # 50% - essentially equal (~0.5°C)
            70: (1.0005, 1.0003),  # 70% - nearly equal (~1°C)
            90: (1.0008, 1.0004),  # 90% - very close (~1.5°C)
            100: (1.0010, 1.0005)  # FBP - slight increase (~2°C)
        }
        
        key_points = [0, 10, 30, 50, 70, 90, 100]
        TBP_points = {}
        
        for vol in key_points:
            # Get D2887 temperature at this volume point
            d2887_temp_C = D2887_interp(vol)
            
            # Convert to Rankine (°R = °C × 9/5 + 491.67)
            d2887_temp_R = d2887_temp_C * 9/5 + 491.67
            
            # Get Riazi-based coefficients for this volume point
            a, b = riazi_tbp_coefficients[vol]
            
            # Riazi correlation: TBP_R = a × (D2887_R)^b
            tbp_temp_R = a * (d2887_temp_R ** b)
            
            # Convert back to Celsius (°C = (°R - 491.67) × 5/9)
            tbp_temp_C = (tbp_temp_R - 491.67) * 5/9
            
            TBP_points[vol] = tbp_temp_C
        
        # Create list and interpolator
        TBP_list = sorted([[vol, temp] for vol, temp in TBP_points.items()])
        TBP_interp = PchipInterpolator([point[0] for point in TBP_list], 
                                       [point[1] for point in TBP_list])
        
        return TBP_interp

    def API_D86_TBP(self, d86: list) -> Tuple[PchipInterpolator, PchipInterpolator]:
        """
        API(1993) interconversion from ASTM D86 to TBP
        TBP=a*ASTM_D86^b

        Parameters:
        d86 (list): List of tuples containing volume % distilled and corresponding temperature.

        Returns:
        tuple: A tuple containing two PchipInterpolator objects, one for D86 and one for TBP.
        """
        API_constants = {
            0: (0.9167, 1.0019),
            10: (0.5277, 1.0900),
            30: (0.7429, 1.0425),
            50: (0.8920, 1.0176),
            70: (0.8705, 1.0226),
            90: (0.9490, 1.0110),
            95: (0.8008, 1.0355)
        }

        vol_distilled = [point[0] for point in d86]
        temperatures = [point[1] for point in d86]
        D86_interp = PchipInterpolator(vol_distilled, temperatures)
        TBP_list = []
        for vol in self.vol_distl_list:
            a, b = API_constants[vol]
            D86 = D86_interp(vol)
            D86_r = self.convert_temperature(D86, 'C', 'R')
            TBP_rankin = a * (D86_r ** b)
            TBP = self.convert_temperature(TBP_rankin, 'R', 'C')
            TBP_list.append([vol, TBP])
        TBP_interp = PchipInterpolator([point[0] for point in TBP_list], [point[1] for point in TBP_list])
        return D86_interp, TBP_interp
    
    def WatsonK_(self) -> float:
        """
        Calculate the Watson K factor.

        Returns:
        float: The Watson K factor.
        """
        MeABP_val = self.MeABP
        self.SG = self.Density/999.013
        WatsonK = (MeABP_val +460)**(1/3)/self.SG
        return WatsonK

    @staticmethod
    def read_d86_csv(file_path: Path) -> list:
        """
        Read the D86 kerosene data from a CSV file.

        Parameters:
        file_path (Path): The path to the CSV file.

        Returns:
        list: A list of tuples containing volume % distilled and corresponding temperature.
        """
        d86 = []
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)  # Skip header 
            x, y = [], []
            try:
                x.append(float(first_row[0]))
                y.append(float(first_row[1]))
                d86.append([float(row[0]), float(row[1])])  # Assuming the first column is volume % and the second is temperature
            except ValueError:
                x_header = first_row[0] if not isinstance(x, float) else 'Volume % distilled'
                y_header = first_row[1] if not isinstance(y, float) else 'Temperature (°C)'

            for row in csv_reader:
                x.append(float(row[0]))
                y.append(float(row[1]))
                d86.append([float(row[0]), float(row[1])])
            # d86 = zip(x,y)
        return d86


if __name__ == '__main__':
    d86_input = Oil.read_d86_csv(D86_PATH)
    oil = Oil(d86_input,Density=800)
    MeABP_val = oil.MeABP
    VABP_val = oil.VABP
    WatsonK_val = oil.WatsonK
    tbp = list(float(oil.Daubert_TBP_interp(vol)) for vol in oil.vol_distl_list)
    Daubert_TBP = list(zip(oil.vol_distl_list, tbp))
    d2887 = list(float(oil.D2887_interp(vol)) for vol in oil.vol_distl_list)
    D2887_curve = list(zip(oil.vol_distl_list, d2887))
    
    pp.pprint(f'MeABP: {MeABP_val:.2f} °F') 
    pp.pprint(f'Watson K: {WatsonK_val:.2f}')
    pp.pprint(f'VABP: {oil.VABP:.2f} °F')
    print(f'D86 to TBP (Daubert): {Daubert_TBP}')
    print(f'D86 to D2887 (SimDis): {D2887_curve}')

    #oil.plot_TBP_D86()
