"""
Batch processing module for distillation curve conversions

Provides utilities for processing multiple samples and datasets.

Usage:
    from batch_processor import BatchProcessor
    
    processor = BatchProcessor('data/', 'output/')
    processor.process_all()
    processor.generate_report()
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from bp_conversions import Oil
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Result of processing a single sample"""
    filename: str
    status: str  # 'success' or 'error'
    error_message: Optional[str] = None
    num_points: Optional[int] = None
    density: Optional[float] = None
    vabp: Optional[float] = None
    watson_k: Optional[float] = None
    processed_at: Optional[str] = None


class BatchProcessor:
    """Process distillation data in batch"""
    
    def __init__(
        self, 
        input_dir: str = "data/",
        output_dir: str = "output/",
        input_type: str = "D86",
        density: float = 820,
        verbose: bool = True,
    ):
        """
        Initialize batch processor
        
        Args:
            input_dir: Directory containing CSV files to process
            output_dir: Directory to save results
            input_type: 'D86', 'D2887', or 'TBP'
            density: Default density (kg/m³) if not in file
            verbose: Print progress
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.input_type = input_type
        self.density = density
        self.verbose = verbose
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results: List[BatchResult] = []
        self.conversions_data: List[Dict] = []
        
        logger.info(f"BatchProcessor initialized")
        logger.info(f"  Input directory: {self.input_dir}")
        logger.info(f"  Output directory: {self.output_dir}")
        logger.info(f"  Input type: {self.input_type}")
    
    def find_csv_files(self) -> List[Path]:
        """Find all CSV files in input directory"""
        csv_files = list(self.input_dir.glob("*.csv"))
        logger.info(f"Found {len(csv_files)} CSV files")
        return sorted(csv_files)
    
    def load_csv(self, filepath: Path) -> Tuple[List[List[float]], Optional[float]]:
        """
        Load CSV file with distillation data
        
        Expected format:
        - Column 1: Volume% (or "Vol%", "Volume%")
        - Column 2: Temperature (or "Temp", "Temp_C", "Temperature")
        - Optional Column 3: Density (kg/m³)
        
        Returns:
            (data_list, density)
        """
        try:
            df = pd.read_csv(filepath)
            
            # Auto-detect columns
            vol_col = None
            temp_col = None
            density_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if any(x in col_lower for x in ['vol%', 'volume%', 'volume', 'vol']):
                    vol_col = col
                elif any(x in col_lower for x in ['temp', 'temperature']):
                    temp_col = col
                elif any(x in col_lower for x in ['density', 'dens']):
                    density_col = col
            
            if not vol_col or not temp_col:
                raise ValueError(
                    f"Could not find volume and temperature columns. "
                    f"Found columns: {list(df.columns)}"
                )
            
            # Extract data
            data = [[row[vol_col], row[temp_col]] for _, row in df.iterrows()]
            
            # Extract density (use first non-null value or default)
            density = None
            if density_col and not df[density_col].isna().all():
                density = df[density_col].dropna().iloc[0]
            
            return data, density
            
        except Exception as e:
            logger.error(f"Error loading {filepath.name}: {str(e)}")
            raise
    
    def process_file(self, filepath: Path) -> BatchResult:
        """Process a single CSV file"""
        
        result = BatchResult(
            filename=filepath.name,
            status='success',
            processed_at=datetime.now().isoformat(),
        )
        
        try:
            if self.verbose:
                logger.info(f"Processing: {filepath.name}")
            
            # Load data
            data, file_density = self.load_csv(filepath)
            density = file_density if file_density else self.density
            
            # Validate
            if len(data) < 3:
                raise ValueError(f"Minimum 3 points required, found {len(data)}")
            
            # Create Oil object
            oil = Oil(data, density, self.input_type)
            
            # Store results
            result.num_points = len(data)
            result.density = density
            result.vabp = oil.VABP
            result.watson_k = oil.WatsonK
            
            # Generate output file
            self._save_conversions(filepath, oil)
            
            if self.verbose:
                logger.info(f"  ✓ Success - VABP: {oil.VABP:.1f}°F, K: {oil.WatsonK:.3f}")
            
        except Exception as e:
            result.status = 'error'
            result.error_message = str(e)
            logger.error(f"  ✗ Error: {str(e)}")
        
        self.results.append(result)
        return result
    
    def _save_conversions(self, original_file: Path, oil: Oil) -> None:
        """Save converted data to output file"""
        
        output_file = self.output_dir / original_file.stem / "_converted.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Volume%", 
                "D86_C", 
                "D2887_C", 
                "TBP_C", 
                "TBP_Daubert_C"
            ])
            
            # Data at standard points
            for vol_pct in range(0, 101, 5):
                writer.writerow([
                    vol_pct,
                    round(oil.D86_interp(vol_pct), 1),
                    round(oil.D2887_interp(vol_pct), 1),
                    round(oil.TBP_interp(vol_pct), 1),
                    round(oil.Daubert_TBP_interp(vol_pct), 1),
                ])
            
            # Add properties
            writer.writerow([])
            writer.writerow(["Properties"])
            writer.writerow(["VABP (°F)", round(oil.VABP, 1)])
            writer.writerow(["MeABP (°C)", round(oil.MeABP, 1)])
            writer.writerow(["Watson K", round(oil.WatsonK, 3)])
            writer.writerow(["Density (kg/m³)", oil.Density])
        
        if self.verbose:
            logger.info(f"  → Saved: {output_file.name}")
    
    def process_all(self) -> List[BatchResult]:
        """Process all CSV files in input directory"""
        
        logger.info(f"Starting batch processing...")
        
        csv_files = self.find_csv_files()
        
        if not csv_files:
            logger.warning("No CSV files found!")
            return []
        
        for i, csv_file in enumerate(csv_files, 1):
            logger.info(f"[{i}/{len(csv_files)}] {csv_file.name}")
            self.process_file(csv_file)
        
        return self.results
    
    def generate_report(self) -> Dict:
        """Generate processing report"""
        
        successful = [r for r in self.results if r.status == 'success']
        failed = [r for r in self.results if r.status == 'error']
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "summary": {
                "success_rate": f"{100*len(successful)/len(self.results):.1f}%" if self.results else "N/A",
                "average_watson_k": (
                    sum(r.watson_k for r in successful if r.watson_k) / len(successful)
                    if successful else None
                ),
                "average_vabp": (
                    sum(r.vabp for r in successful if r.vabp) / len(successful)
                    if successful else None
                ),
            },
            "successful_files": [
                {
                    "filename": r.filename,
                    "points": r.num_points,
                    "density": r.density,
                    "vabp": r.vabp,
                    "watson_k": r.watson_k,
                }
                for r in successful
            ],
            "failed_files": [
                {
                    "filename": r.filename,
                    "error": r.error_message,
                }
                for r in failed
            ],
        }
        
        return report
    
    def save_report(self, filename: str = "batch_report.json") -> Path:
        """Save report to JSON file"""
        
        report = self.generate_report()
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved: {report_path}")
        
        return report_path
    
    def print_report(self) -> None:
        """Print summary report"""
        
        report = self.generate_report()
        
        print(f"\n{'='*60}")
        print("BATCH PROCESSING REPORT")
        print(f"{'='*60}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total files: {report['total_files']}")
        print(f"Successful: {report['successful']}")
        print(f"Failed: {report['failed']}")
        print(f"Success rate: {report['summary']['success_rate']}")
        
        if report['summary']['average_watson_k']:
            print(f"\nAverage Watson K: {report['summary']['average_watson_k']:.3f}")
        if report['summary']['average_vabp']:
            print(f"Average VABP: {report['summary']['average_vabp']:.1f}°F")
        
        if report['failed_files']:
            print(f"\n⚠️ Failed Files:")
            for f in report['failed_files']:
                print(f"  - {f['filename']}: {f['error']}")
        
        print(f"\n✓ Results saved to: {self.output_dir}")
        print(f"{'='*60}\n")


def batch_process_directory(
    input_dir: str = "data/",
    output_dir: str = "output/",
    input_type: str = "D86",
    density: float = 820,
) -> Dict:
    """
    Convenience function for batch processing
    
    Usage:
        report = batch_process_directory('data/', 'output/')
    """
    processor = BatchProcessor(input_dir, output_dir, input_type, density)
    processor.process_all()
    processor.print_report()
    processor.save_report()
    
    return processor.generate_report()


if __name__ == "__main__":
    # Example usage
    print("""
    Batch Processor Example
    
    Create a 'data/' directory with CSV files like:
    
    Vol%,Temp_C
    0,160
    50,225
    100,290
    
    Then run:
        processor = BatchProcessor('data/', 'output/')
        processor.process_all()
        processor.print_report()
    """)
    
    # Try to process if data directory exists
    if Path("data/").exists():
        batch_process_directory()
    else:
        print("\nCreate a 'data/' directory with CSV files to begin.")
