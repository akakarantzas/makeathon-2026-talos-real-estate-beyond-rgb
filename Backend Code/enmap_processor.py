import os
import glob
import xml.etree.ElementTree as ET
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
import warnings
from config import (
    ENMAP_TARGET_WAVELENGTHS,
    PLOT_SIDE_LENGTH_M,
    CLOUD_COVER_THRESHOLD,
    NDVI_BARE_SOIL_THRESHOLD
)

def apply_quality_masks(base_path, window=None):
    """
    Looks for EnMap quality assurance files in the same directory as the spectral image.
    Combines them to return a strict masked array where (cloud == 0) & (shadow == 0) & (cirrus == 0).
    """
    dir_name = os.path.dirname(base_path)
    
    # Define file patterns
    patterns = {
        'cloud': '*QL_QUALITY_CLOUD.TIF',
        'shadow': '*QL_QUALITY_CLOUDSHADOW.TIF',
        'cirrus': '*QL_QUALITY_CIRRUS.TIF'
    }
    
    masks = {}
    for key, pattern in patterns.items():
        search_path = os.path.join(dir_name, pattern)
        # Using glob to find matching files dynamically
        files = glob.glob(search_path)
        
        if not files:
            warnings.warn(f"Quality mask matching '{pattern}' not found in {dir_name}")
            masks[key] = None
        else:
            # Open the first matching file
            try:
                with rasterio.open(files[0]) as src:
                    if window:
                        masks[key] = src.read(1, window=window)
                    else:
                        masks[key] = src.read(1)
            except Exception as e:
                warnings.warn(f"Error reading quality mask {files[0]}: {e}")
                masks[key] = None
                
    # If all masks are missing, we cannot apply a cloud mask
    if all(v is None for v in masks.values()):
        warnings.warn("No quality masks found. Proceeding without cloud masking.")
        return None
        
    # Combine masks: 0 means clear in these quality products.
    # True in our output mask will mean the pixel is valid (clear).
    combined_valid_mask = None
    for key, data in masks.items():
        if data is not None:
            valid = (data == 0)
            if combined_valid_mask is None:
                combined_valid_mask = valid
            else:
                combined_valid_mask = combined_valid_mask & valid
                
    return combined_valid_mask

def parse_enmap_xml_wavelengths(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        wvs = []
        for elem in root.iter():
            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if 'centerWavelength' in tag_name or 'Center_Wavelength' in tag_name:
                if elem.text:
                    try:
                        wvs.append(float(elem.text.strip()))
                    except ValueError:
                        pass
        wvs.sort()
        return np.array(wvs)
    except Exception:
        return np.array([])


def get_band_index(wavelengths, target_wv):
    """
    Dynamically identifies the band index that closest matches the target wavelength.
    """
    idx = (np.abs(wavelengths - target_wv)).argmin()
    return int(idx + 1)  # rasterio bands are 1-indexed


def extract_spectral_metrics(file_path, target_lat, target_lon):
    """
    Opens the spectral file, applies a 250,000 m2 bounding box around the target,
    calculates NDVI, NDWI, and bare soil SOC / MAI using valid (unclouded) pixels.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"EnMap spectral file not found: {file_path}")
        
    with rasterio.open(file_path) as src:
        # 1. Convert Target Coordinates (WGS84) to the Image CRS
        lon_arr, lat_arr = transform('EPSG:4326', src.crs, [target_lon], [target_lat])
        x_center, y_center = lon_arr[0], lat_arr[0]
        
        # 2. Calculate 250,000 m2 bounding box (approx 500m x 500m)
        half_side = PLOT_SIDE_LENGTH_M / 2.0
        left = x_center - half_side
        right = x_center + half_side
        bottom = y_center - half_side
        top = y_center + half_side
        
        # Get the corresponding rasterio window
        window = from_bounds(left, bottom, right, top, transform=src.transform)
        
        # 3. Identify closest bands based on config wavelengths
        dir_name = os.path.dirname(file_path)
        xml_files = glob.glob(os.path.join(dir_name, '*METADATA.XML')) + glob.glob(os.path.join(dir_name, '*metadata*.xml'))
        
        try:
            if not xml_files:
                raise FileNotFoundError("XML metadata file not found.")
            wavelengths = parse_enmap_xml_wavelengths(xml_files[0])
            if len(wavelengths) == 0:
                raise ValueError("Parsed wavelengths array is empty.")
        except Exception:
            warnings.warn("Wavelength tags missing. Using interpolated band wavelengths as fallback.")
            wavelengths = np.linspace(400, 2500, src.count)
            
        red_idx = get_band_index(wavelengths, ENMAP_TARGET_WAVELENGTHS['Red'])
        nir_idx = get_band_index(wavelengths, ENMAP_TARGET_WAVELENGTHS['NIR'])
        swir_idx = get_band_index(wavelengths, ENMAP_TARGET_WAVELENGTHS['SWIR'])
        
        # Read band data specifically for the window
        red_data = src.read(red_idx, window=window).astype(np.float32)
        nir_data = src.read(nir_idx, window=window).astype(np.float32)
        swir_data = src.read(swir_idx, window=window).astype(np.float32)
        
        # 4. Apply Quality Masks
        quality_mask = apply_quality_masks(file_path, window=window)
        
        if quality_mask is None:
            # Fallback if no mask files are found: treat all pixels as clear
            quality_mask = np.ones(red_data.shape, dtype=bool)
            
        # Calculate cloud cover ratio for the bounding box
        total_pixels = quality_mask.size
        valid_pixels = np.sum(quality_mask)
        cloud_cover_ratio = 1.0 - (valid_pixels / total_pixels) if total_pixels > 0 else 1.0
        
        # If cloud cover is over 90%, flag it and return early
        if cloud_cover_ratio > CLOUD_COVER_THRESHOLD:
            return {
                "cloud_mask_applied": True,
                "heavy_cloud_cover": True,
                "cloud_cover_ratio": cloud_cover_ratio,
                "ndvi_vegetation_vigor": None,
                "ndwi_water_retention": None,
                "bare_soil_soc_index": None,
                "mai_mineral_index": None
            }
            
        # Mask out invalid pixels (clouds, shadows, and true zero 'no-data' values)
        # We suppress division by zero by setting invalid data to NaN
        with np.errstate(divide='ignore', invalid='ignore'):
            valid_data_mask = quality_mask & (red_data > 0) & (nir_data > 0) & (swir_data > 0)
            
            if np.sum(valid_data_mask) == 0:
                # Failsafe if the masking wipes out 100% of the pixels
                return {
                    "cloud_mask_applied": True,
                    "heavy_cloud_cover": True,
                    "cloud_cover_ratio": cloud_cover_ratio,
                    "ndvi_vegetation_vigor": None,
                    "ndwi_water_retention": None,
                    "bare_soil_soc_index": None,
                    "mai_mineral_index": None
                }
                
            red_masked = np.where(valid_data_mask, red_data, np.nan)
            nir_masked = np.where(valid_data_mask, nir_data, np.nan)
            swir_masked = np.where(valid_data_mask, swir_data, np.nan)
            
            # Calculate standard metrics on clear pixels
            ndvi = (nir_masked - red_masked) / (nir_masked + red_masked)
            ndwi = (nir_masked - swir_masked) / (nir_masked + swir_masked)
            
            avg_ndvi = float(np.nanmean(ndvi))
            avg_ndwi = float(np.nanmean(ndwi))
            
            # 5. CREATES A BARE SOIL MASK: Filter array to isolate pixels where NDVI < 0.3
            bare_soil_mask = valid_data_mask & (~np.isnan(ndvi)) & (ndvi < NDVI_BARE_SOIL_THRESHOLD)
            
            if np.sum(bare_soil_mask) > 0:
                swir_bare = np.where(bare_soil_mask, swir_masked, np.nan)
                red_bare = np.where(bare_soil_mask, red_masked, np.nan)
                nir_bare = np.where(bare_soil_mask, nir_masked, np.nan)
                
                # Calculate the SOC Index and MAI strictly on the bare soil mask pixels
                # Proxies used for standard index calculations when specific formulation is dynamic
                soc_index = (swir_bare - red_bare) / (swir_bare + red_bare)
                mai_index = swir_bare / (nir_bare + 1e-8)  # prevent div by zero
                
                avg_soc = float(np.nanmean(soc_index))
                avg_mai = float(np.nanmean(mai_index))
            else:
                avg_soc = None
                avg_mai = None
                
        return {
            "cloud_mask_applied": True,
            "heavy_cloud_cover": False,
            "cloud_cover_ratio": cloud_cover_ratio,
            "ndvi_vegetation_vigor": avg_ndvi if not np.isnan(avg_ndvi) else None,
            "ndwi_water_retention": avg_ndwi if not np.isnan(avg_ndwi) else None,
            "bare_soil_soc_index": avg_soc if avg_soc is not None and not np.isnan(avg_soc) else None,
            "mai_mineral_index": avg_mai if avg_mai is not None and not np.isnan(avg_mai) else None
        }
