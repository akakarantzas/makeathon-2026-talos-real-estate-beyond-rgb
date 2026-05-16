from Backend_code.paths import DATA_DIR

# 1. Dynamic Scoring Matrix
WEIGHT_MATRIX = {
    # Original Scenarios
    "Precision Agriculture": {"env_weight": 0.60, "log_weight": 0.20, "reg_weight": 0.20},
    "Agrivoltaics": {"env_weight": 0.30, "log_weight": 0.30, "reg_weight": 0.40},
    "Logistics": {"env_weight": 0.10, "log_weight": 0.60, "reg_weight": 0.30},
    "Mineral Extraction": {"env_weight": 0.40, "log_weight": 0.30, "reg_weight": 0.30},

    # New High-Value Scenarios (MCDA Normalized)
    "Industrial Greenhouses": {"env_weight": 0.50, "log_weight": 0.30, "reg_weight": 0.20},
    "Data Center": {"env_weight": 0.10, "log_weight": 0.70, "reg_weight": 0.20},
    "Utility Battery Storage": {"env_weight": 0.20, "log_weight": 0.50, "reg_weight": 0.30},
    "Carbon Farming": {"env_weight": 0.70, "log_weight": 0.10, "reg_weight": 0.20}
}

# 2. Target Coordinates (WGS84 Format)
TARGET_COORDINATES = {
    "Arkadia": {"lat": 37.651492, "lon": 22.366139},
    "Magnisia": {"lat": 39.174176, "lon": 22.766325},
    "Arkadia 2": {"lat": 37.324456, "lon": 22.143828},
    "Veroia": {"lat": 40.398697, "lon": 22.120677}
}

# 3. EnMap Target Wavelengths (nm)
ENMAP_TARGET_WAVELENGTHS = {
    "Red": 665,
    "NIR": 865,
    "SWIR": 1610
}

# 4. Other Static Global Variables

# Default Paths
OUTPUT_JSON_FILENAME = "api_response.json"
ENMAP_DATA_DIR = DATA_DIR  # Canonical path for EnMap .tif files

# API Base URLs
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"

# Bounding Box & Geo Constants
PLOT_AREA_SQM = 250000  # 250,000 m²
PLOT_SIDE_LENGTH_M = 500  # approx 500m x 500m
CLOUD_COVER_THRESHOLD = 0.90  # 90% cloud cover limit

# Filtering Thresholds
NDVI_BARE_SOIL_THRESHOLD = 0.3  # Pixels with NDVI < 0.3 are considered bare soil
