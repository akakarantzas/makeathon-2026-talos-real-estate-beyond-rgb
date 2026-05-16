# PRODUCT REQUIREMENTS DOCUMENT (PRD)
**Project Name:** Beyond RGB - Backend Data Pipeline
**Target Environment:** Python 3.10+ (Local Execution)
**Output:** A single static JSON file (`api_response.json`)

## 1. Executive Summary
The objective of this backend service is to process Level-2A EnMap hyperspectral satellite imagery (`.tif`), fuse it with external macroeconomic and infrastructural parameters, and calculate a dynamic "Investment Viability Score" for four 250,000 m² land plots in Greece. 

**Critical Architecture Directive:** We are utilizing a **"Golden Run"** strategy. This backend will NOT run live during the presentation. It is a pre-computation pipeline designed to be executed via terminal prior to the pitch. It will crunch all data, call all APIs, and output a strict `api_response.json` file. The frontend UI will be completely decoupled and will solely read this generated JSON file.

---

## 2. System Architecture (The 3-File Blueprint)
To prevent code bloat and ensure debugging efficiency, the agent MUST split the codebase into exactly three modular Python files. Do not write a single monolithic script.

1.  **`config.py`**: Contains the hardcoded Weighting Matrix, location coordinates, and global variables.
2.  **`enmap_processor.py`**: Contains all `rasterio`, `numpy`, and `geopandas` logic for parsing `.tif` files, applying cloud masks, and extracting spectral metrics.
3.  **`pipeline.py`**: The main execution script. It orchestrates the API calls, triggers the `enmap_processor`, applies the scoring math from `config.py`, and writes the final `api_response.json`.

---

## 3. Input Data Specifications
The backend will ingest the following data sources:

* **Target Coordinates (WGS84 Format):**
    * Arkadia: 37.651492, 22.366139
    * Magnisia: 39.174176, 22.766325
    * Arkadia 2: 37.324456, 22.143828
    * Veroia: 40.398697, 22.120677
* **EnMap Data:** Hyperspectral `.tif` files (Level-2A).
* **External APIs:** Distance to Sea (Overpass API / OpenStreetMap), Land Surface Temp (Open-Meteo).

---

## 4. Core Processing Pipeline (The "Engine")

### Step 4.1: Geospatial Masking & Filtering (`enmap_processor.py`)
* **Cloud Masking:** Read the EnMap Quality Classification Mask (`QL_CLD`). Exclude all pixels flagged as cloud, cirrus, or shadow before performing any math.
* **Vegetation Masking (For SOC):** To calculate Soil Organic Carbon (SOC), the array must be filtered to isolate bare soil. Only evaluate pixels where NDVI < 0.3.

### Step 4.2: Hyperspectral Metric Extraction (`enmap_processor.py`)
**CRITICAL:** EnMap has over 240 bands. You must dynamically identify the band indices that closest match the following wavelengths:
* **Red:** ~665 nm
* **Near-Infrared (NIR):** ~865 nm
* **Shortwave-Infrared (SWIR):** ~1610 nm

Using these bands, calculate the mean values for the 250,000 m² bounding box (approx. 500m x 500m) for each coordinate:
* **NDVI:** (NIR - Red) / (NIR + Red)
* **NDWI:** (NIR - SWIR) / (NIR + SWIR)
* **SOC Index:** Extracted from SWIR bands strictly on the bare soil mask.

### Step 4.3: Data Fusion & Hardcoded Parameters (`pipeline.py`)
* **LST Fusion:** Call the Open-Meteo API to fetch Land Surface Temperature, as EnMap lacks thermal bands (stops at 2450nm).
* **Legal Risk Injection:** Apply static penalty modifiers based on the specific location (e.g., High Flood Penalty for Magnisia, Ktimatologio clearance risks).

---

## 5. The Dynamic Scoring Matrix (`config.py`)
The backend must use this hardcoded dictionary to define scoring weights. **DO NOT use AI to calculate these weights dynamically.** ```python
WEIGHT_MATRIX = {
    "Precision Agriculture": {"env_weight": 0.60, "log_weight": 0.20, "reg_weight": 0.20},
    "Agrivoltaics": {"env_weight": 0.30, "log_weight": 0.30, "reg_weight": 0.40},
    "Logistics": {"env_weight": 0.10, "log_weight": 0.60, "reg_weight": 0.30},
    "Mineral Extraction": {"env_weight": 0.40, "log_weight": 0.30, "reg_weight": 0.30}
}

Formula: Final_Score = (Env_Score * env_weight) + (Log_Score * log_weight) + (Reg_Score * reg_weight)

6. Strict JSON Output Schema (The API Contract)
The pipeline.py script must output a strictly formatted JSON file mapping to the exact schema below. The backend must never output raw numbers without this structural context.

{
  "project_meta": {
    "last_updated": "ISO-8601 Timestamp",
    "active_use_case": "String (e.g., 'Agrivoltaics')",
    "applied_weights": {
      "environmental_weight": "Float",
      "logistics_weight": "Float",
      "regulatory_weight": "Float"
    }
  },
  "locations": [
    {
      "name": "String (e.g., 'Magnisia')",
      "coordinates": {"lat": "Float", "lon": "Float"},
      "overall_viability_score": "Integer (0-100)",
      "score_breakdown": {
        "environmental_score": "Integer",
        "logistics_score": "Integer",
        "regulatory_score": "Integer"
      },
      "enmap_metrics_fused": {
        "ndvi_vegetation_vigor": "Float",
        "ndwi_water_retention": "Float",
        "bare_soil_soc_index": "Float",
        "fused_lst_celsius": "Float",
        "cloud_mask_applied": "Boolean"
      },
      "macro_infrastructure": {
        "distance_to_sea_km": "Float",
        "distance_to_high_voltage_grid_km": "Float",
        "terrain_slope_degrees": "Float"
      },
      "legal_and_risk_factors": {
        "cadastral_clearance_status": "String ('Clear', 'Disputed')",
        "zoning_restriction": "String",
        "climate_risk_flag": "String",
        "borehole_permit_difficulty": "String ('Easy', 'Moderate', 'Severe')"
      },
      "ai_summary": "String (1-2 sentence automated conclusion)"
    }
  ]
}

7. Error Handling & Execution Strategy
Because this is a Golden Run pipeline, failure must be loud during the build phase, but graceful regarding data exceptions.

API Timeout Protocol (Fail-Fast): If external APIs (Overpass, Open-Meteo) time out or fail, the script should raise an error and halt execution. Do NOT inject mock data. The developer will re-run the pipeline until a successful Golden Run is achieved.

100% Cloud Cover Exception: If the EnMap QL_CLD mask determines that a plot is >90% covered by clouds, it is impossible to calculate NDVI/NDWI.

Handling: The backend must set cloud_mask_applied to true, assign null or 0 to the EnMap metrics, and inject a warning string into the ai_summary stating: "Cannot evaluate spectral metrics due to heavy cloud cover; relying purely on macro/legal metrics."

Bounding Box Overflow: When calculating the 250,000 m² bounding box around the central coordinate, verify the box does not extend into the sea (crucial for Magnisia) to avoid contaminating soil metrics with water pixels.

CLI Execution: The pipeline must be executable via terminal with an argument for the use case: python pipeline.py --use_case "Logistics".