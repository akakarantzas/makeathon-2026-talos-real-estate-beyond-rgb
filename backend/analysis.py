from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import rasterio
from rasterio.enums import Resampling


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

PLOTS = {
    "Arkadia": DATA_DIR / "arkadia_20241024_mosaic",
    "Arkadia 2": DATA_DIR / "arkadia2" / "arkadia2_20240531_mosaic",
    "Magnisia": DATA_DIR / "magnisia_20241024_mosaic",
    "Veroia": DATA_DIR / "Veroia-Veroia_20250821_mosaic",
}

TARGET_WAVELENGTHS_NM = {"green": 560, "red": 665, "nir": 842}


def safe_index(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, np.nan, dtype=np.float32),
        where=np.abs(denominator) > 1e-6,
    )


@lru_cache(maxsize=None)
def load_wavelengths(metadata_path: str) -> np.ndarray:
    root = ET.parse(metadata_path).getroot()
    wavelengths = [
        float(node.text)
        for node in root.findall(".//bandCharacterisation/bandID/wavelengthCenterOfBand")
    ]
    if not wavelengths:
        raise ValueError(f"No wavelength metadata found in {metadata_path}")
    return np.array(wavelengths, dtype=np.float32)


def nearest_band_index(wavelengths: np.ndarray, target_nm: float) -> int:
    return int(np.argmin(np.abs(wavelengths - target_nm))) + 1


def investment_recommendation(ndvi: float, ndwi: float) -> tuple[int, str]:
    normalized_ndvi = np.clip((ndvi + 1) / 2, 0, 1)
    normalized_ndwi = np.clip((ndwi + 1) / 2, 0, 1)
    score = round(100 * (0.7 * normalized_ndvi + 0.3 * normalized_ndwi))

    if score >= 70:
        recommendation = "Strong candidate"
    elif score >= 55:
        recommendation = "Promising, but verify with ground data"
    else:
        recommendation = "Lower-priority candidate"
    return score, recommendation


@lru_cache(maxsize=None)
def load_scene(plot_name: str) -> dict:
    scene_path = PLOTS[plot_name]
    image_path = scene_path / "SPECTRAL_IMAGE.TIF"
    metadata_path = scene_path / "METADATA.XML"
    wavelengths = load_wavelengths(str(metadata_path))

    with rasterio.open(image_path) as src:
        max_dimension = max(src.height, src.width)
        scale = min(1.0, 320 / max_dimension)
        out_height = max(1, int(src.height * scale))
        out_width = max(1, int(src.width * scale))
        cube = src.read(
            out_shape=(src.count, out_height, out_width),
            resampling=Resampling.average,
            masked=True,
        ).astype(np.float32)

    cube = np.ma.filled(cube, np.nan)
    band_numbers = {
        name: nearest_band_index(wavelengths, wavelength)
        for name, wavelength in TARGET_WAVELENGTHS_NM.items()
    }

    green = cube[band_numbers["green"] - 1]
    red = cube[band_numbers["red"] - 1]
    nir = cube[band_numbers["nir"] - 1]
    ndvi = safe_index(nir - red, nir + red)
    ndwi = safe_index(green - nir, green + nir)
    mean_spectrum = np.nanmean(cube, axis=(1, 2))
    score, recommendation = investment_recommendation(
        float(np.nanmean(ndvi)),
        float(np.nanmean(ndwi)),
    )

    return {
        "name": plot_name,
        "wavelengths": wavelengths.tolist(),
        "band_numbers": band_numbers,
        "mean_spectrum": np.nan_to_num(mean_spectrum, nan=0.0).tolist(),
        "ndvi": float(np.nanmean(ndvi)),
        "ndwi": float(np.nanmean(ndwi)),
        "score": score,
        "recommendation": recommendation,
    }


def list_plots() -> list[dict]:
    return [load_scene(name) for name in PLOTS]

