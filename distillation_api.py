"""
REST API for Distillation Curve Interconversion

Provides HTTP endpoints for converting between distillation standards.

Run: python -m uvicorn distillation_api:app --reload
Then: http://localhost:8000/docs for interactive API docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
import json
from pathlib import Path
import io
import csv

from bp_conversions import Oil

# Initialize FastAPI app
app = FastAPI(
    title="Distillation Curve Interconversion API",
    description="Convert between D86, D2887, and TBP distillation curves",
    version="0.2.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Enable CORS for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class DistillationPoint(BaseModel):
    """A single distillation data point"""
    volume_percent: float = Field(..., ge=0, le=100, description="Volume percent (0-100)")
    temperature_c: float = Field(..., description="Temperature in Celsius")


class ConversionRequest(BaseModel):
    """Request for distillation curve conversion"""
    distillation_data: List[DistillationPoint] = Field(
        ..., 
        min_items=3,
        description="Minimum 3 points required"
    )
    density_kg_m3: float = Field(
        ..., 
        ge=600, 
        le=1200,
        description="Density in kg/m³ (typical: 600-1200)"
    )
    input_type: str = Field(
        default="D86",
        description="Input distillation type: D86, D2887, or TBP"
    )
    output_types: List[str] = Field(
        default=["D86", "D2887", "TBP"],
        description="Desired output types"
    )


class ConversionPoint(BaseModel):
    """A converted distillation point"""
    volume_percent: float
    d86_c: Optional[float] = None
    d2887_c: Optional[float] = None
    tbp_c: Optional[float] = None
    tbp_daubert_c: Optional[float] = None


class PropertyResult(BaseModel):
    """Petroleum properties"""
    vabp_fahrenheit: float = Field(..., description="Volume Average Boiling Point")
    meabp_celsius: float = Field(..., description="Mean Average Boiling Point")
    watson_k: float = Field(..., description="Watson K characterization factor")
    density_kg_m3: float


class ConversionResponse(BaseModel):
    """Response with converted curves and properties"""
    conversions: List[ConversionPoint]
    properties: PropertyResult
    metadata: dict


# Helper functions
def validate_input_data(data: List[DistillationPoint]) -> bool:
    """Validate that distillation data is physically reasonable"""
    temps = [p.temperature_c for p in data]
    
    # Check monotonicity
    if not all(temps[i] < temps[i+1] for i in range(len(temps)-1)):
        raise ValueError("Temperatures must be strictly increasing")
    
    # Check reasonable range
    if any(t < -50 or t > 400 for t in temps):
        raise ValueError("Temperature range outside typical bounds (-50 to 400°C)")
    
    return True


# Routes
@app.get("/", tags=["Health"])
async def root():
    """API health check and information"""
    return {
        "name": "Distillation Curve Interconversion API",
        "version": "0.2.0",
        "description": "Convert between D86, D2887, and TBP distillation curves",
        "endpoints": {
            "health": "GET /",
            "convert": "POST /convert",
            "properties": "POST /properties",
            "batch": "POST /batch",
            "docs": "GET /docs",
        }
    }


@app.post("/convert", response_model=ConversionResponse, tags=["Conversions"])
async def convert_curves(request: ConversionRequest):
    """
    Convert distillation curves between standards
    
    **Input Types:** D86, D2887, TBP
    
    **Output Types:** D86, D2887, TBP, TBP_DAUBERT
    
    **Example:**
    ```json
    {
      "distillation_data": [
        {"volume_percent": 0, "temperature_c": 160},
        {"volume_percent": 50, "temperature_c": 225},
        {"volume_percent": 100, "temperature_c": 290}
      ],
      "density_kg_m3": 820,
      "input_type": "D86",
      "output_types": ["D86", "D2887", "TBP"]
    }
    ```
    """
    try:
        # Validate input
        validate_input_data(request.distillation_data)
        
        # Convert Pydantic model to raw list
        raw_data = [
            [p.volume_percent, p.temperature_c] 
            for p in request.distillation_data
        ]
        
        # Validate input type
        if request.input_type.upper() not in ['D86', 'D2887', 'TBP']:
            raise ValueError(f"Invalid input_type: {request.input_type}")
        
        # Create Oil object
        oil = Oil(raw_data, request.density_kg_m3, request.input_type)
        
        # Generate conversions at standard points
        vol_percents = [0, 10, 30, 50, 70, 90, 100]
        conversions = []
        
        for vol_pct in vol_percents:
            point = ConversionPoint(volume_percent=vol_pct)
            
            if "D86" in request.output_types or "D86" in request.output_types:
                point.d86_c = round(oil.D86_interp(vol_pct), 1)
            if "D2887" in request.output_types:
                point.d2887_c = round(oil.D2887_interp(vol_pct), 1)
            if "TBP" in request.output_types:
                point.tbp_c = round(oil.TBP_interp(vol_pct), 1)
            if "TBP_DAUBERT" in request.output_types:
                point.tbp_daubert_c = round(oil.Daubert_TBP_interp(vol_pct), 1)
            
            conversions.append(point)
        
        # Properties
        properties = PropertyResult(
            vabp_fahrenheit=round(oil.VABP, 1),
            meabp_celsius=round(oil.MeABP, 1),
            watson_k=round(oil.WatsonK, 3),
            density_kg_m3=oil.Density,
        )
        
        # Metadata
        metadata = {
            "input_type": request.input_type,
            "num_input_points": len(request.distillation_data),
            "output_types": request.output_types,
        }
        
        return ConversionResponse(
            conversions=conversions,
            properties=properties,
            metadata=metadata,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@app.post("/properties", tags=["Properties"])
async def get_properties(request: ConversionRequest):
    """
    Calculate petroleum properties from distillation data
    
    Returns VABP, MeABP, and Watson K characterization factor
    """
    try:
        validate_input_data(request.distillation_data)
        
        raw_data = [[p.volume_percent, p.temperature_c] for p in request.distillation_data]
        oil = Oil(raw_data, request.density_kg_m3, request.input_type)
        
        return {
            "vabp_fahrenheit": round(oil.VABP, 1),
            "meabp_celsius": round(oil.MeABP, 1),
            "watson_k": round(oil.WatsonK, 3),
            "density_kg_m3": oil.Density,
            "characterization": (
                "Naphthenic (aromatic)" if oil.WatsonK < 11.5 else
                "Mixed" if oil.WatsonK < 12.5 else
                "Paraffinic (alkane)" 
            )
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/batch", tags=["Batch Operations"])
async def batch_convert(
    requests_json: str = Query(..., description="JSON array of conversion requests")
):
    """
    Process multiple conversion requests in batch
    
    Useful for processing many samples at once.
    
    **Request format:**
    ```json
    [
      {
        "distillation_data": [...],
        "density_kg_m3": 820,
        "input_type": "D86"
      },
      ...
    ]
    ```
    """
    try:
        batch_requests = json.loads(requests_json)
        
        if not isinstance(batch_requests, list):
            raise ValueError("Input must be a JSON array")
        
        results = []
        
        for i, req_dict in enumerate(batch_requests):
            try:
                # Convert dict to ConversionRequest
                distillation_data = [
                    DistillationPoint(**p) 
                    for p in req_dict['distillation_data']
                ]
                
                request = ConversionRequest(
                    distillation_data=distillation_data,
                    density_kg_m3=req_dict['density_kg_m3'],
                    input_type=req_dict.get('input_type', 'D86'),
                    output_types=req_dict.get('output_types', ['D86', 'D2887', 'TBP']),
                )
                
                # Process
                response = await convert_curves(request)
                results.append({
                    "index": i,
                    "status": "success",
                    "data": response.dict(),
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "status": "error",
                    "error": str(e),
                })
        
        return {
            "total": len(batch_requests),
            "successful": sum(1 for r in results if r['status'] == 'success'),
            "failed": sum(1 for r in results if r['status'] == 'error'),
            "results": results,
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch error: {str(e)}")


@app.post("/export-csv", tags=["Export"])
async def export_csv(request: ConversionRequest):
    """
    Export conversion results as CSV file
    """
    try:
        validate_input_data(request.distillation_data)
        
        raw_data = [[p.volume_percent, p.temperature_c] for p in request.distillation_data]
        oil = Oil(raw_data, request.density_kg_m3, request.input_type)
        
        # Create CSV data
        vol_percents = list(range(0, 101, 5))  # Every 5%
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Header
        header = ["Volume%", "D86_C", "D2887_C", "TBP_C"]
        writer.writerow(header)
        
        # Data rows
        for vol_pct in vol_percents:
            writer.writerow([
                vol_pct,
                round(oil.D86_interp(vol_pct), 1),
                round(oil.D2887_interp(vol_pct), 1),
                round(oil.TBP_interp(vol_pct), 1),
            ])
        
        # Add properties
        writer.writerow([])
        writer.writerow(["Properties"])
        writer.writerow(["VABP (°F)", round(oil.VABP, 1)])
        writer.writerow(["MeABP (°C)", round(oil.MeABP, 1)])
        writer.writerow(["Watson K", round(oil.WatsonK, 3)])
        writer.writerow(["Density (kg/m³)", oil.Density])
        
        # Return as file download
        csv_content = csv_buffer.getvalue()
        
        return JSONResponse(
            content={
                "csv_data": csv_content,
                "filename": "distillation_conversions.csv",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.2.0",
    }


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     Distillation Curve Interconversion REST API                ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Starting API server...
    
    📍 API Docs: http://localhost:8000/docs
    📍 API URL: http://localhost:8000
    
    Try these example requests:
    
    1. Convert D86 to D2887 & TBP:
       POST http://localhost:8000/convert
       
    2. Get properties:
       POST http://localhost:8000/properties
       
    3. Batch process:
       POST http://localhost:8000/batch
       
    4. Export as CSV:
       POST http://localhost:8000/export-csv
    
    Press Ctrl+C to stop the server.
    """)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
