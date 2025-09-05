"""
Remote Sensing Data Pipeline for AgroCarbon360
Integrates Google Earth Engine, Sentinel Hub, and Planet Labs for satellite data
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass

# Google Earth Engine
try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False
    logging.warning("Google Earth Engine not available. Install with: pip install earthengine-api")

# Sentinel Hub
try:
    from sentinelhub import SentinelHubRequest, DataCollection, MimeType, CRS, BBox, bbox_to_dimensions
    SH_AVAILABLE = True
except ImportError:
    SH_AVAILABLE = False
    logging.warning("Sentinel Hub not available. Install with: pip install sentinelhub")

# Planet Labs
try:
    from planet import api
    PLANET_AVAILABLE = True
except ImportError:
    PLANET_AVAILABLE = False
    logging.warning("Planet Labs API not available. Install with: pip install planet")

@dataclass
class SatelliteImage:
    """Container for satellite image data"""
    image_id: str
    source: str  # 'GEE', 'SENTINEL', 'PLANET'
    timestamp: datetime
    bounds: Tuple[float, float, float, float]  # min_lon, min_lat, max_lon, max_lat
    bands: Dict[str, np.ndarray]
    metadata: Dict

class RemoteSensingPipeline:
    """Main pipeline for remote sensing data acquisition and processing"""
    
    def __init__(self, config_path: str = "config/rs_config.json"):
        self.config = self._load_config(config_path)
        self._initialize_apis()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration for different satellite data sources"""
        default_config = {
            "gee": {
                "service_account": None,
                "project": "agrocarbon360",
                "assets": {
                    "sentinel2": "COPERNICUS/S2_SR",
                    "landsat8": "LANDSAT/LC08/C01/T1_SR",
                    "modis": "MODIS/006/MOD13Q1"
                }
            },
            "sentinel_hub": {
                "client_id": None,
                "client_secret": None,
                "base_url": "https://services.sentinel-hub.com"
            },
            "planet": {
                "api_key": None,
                "base_url": "https://api.planet.com"
            },
            "processing": {
                "cloud_cover_threshold": 20,
                "resolution": 10,  # meters
                "max_images_per_request": 50
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _initialize_apis(self):
        """Initialize satellite data APIs"""
        if EE_AVAILABLE and self.config["gee"]["service_account"]:
            try:
                credentials = ee.ServiceAccountCredentials(
                    self.config["gee"]["service_account"]["email"],
                    self.config["gee"]["service_account"]["key_file"]
                )
                ee.Initialize(credentials, project=self.config["gee"]["project"])
                logging.info("Google Earth Engine initialized")
            except Exception as e:
                logging.error(f"Failed to initialize GEE: {e}")
        
        if SH_AVAILABLE and self.config["sentinel_hub"]["client_id"]:
            try:
                os.environ["SH_CLIENT_ID"] = self.config["sentinel_hub"]["client_id"]
                os.environ["SH_CLIENT_SECRET"] = self.config["sentinel_hub"]["client_secret"]
                logging.info("Sentinel Hub configured")
            except Exception as e:
                logging.error(f"Failed to configure Sentinel Hub: {e}")
    
    def get_sentinel2_data(self, 
                          bounds: Tuple[float, float, float, float],
                          start_date: datetime,
                          end_date: datetime,
                          bands: List[str] = None) -> List[SatelliteImage]:
        """Get Sentinel-2 data from Google Earth Engine"""
        if not EE_AVAILABLE:
            raise RuntimeError("Google Earth Engine not available")
        
        if bands is None:
            bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']  # Blue, Green, Red, NIR, SWIR1, SWIR2
        
        # Define area of interest
        aoi = ee.Geometry.Rectangle(bounds)
        
        # Get Sentinel-2 collection
        collection = (ee.ImageCollection(self.config["gee"]["assets"]["sentinel2"])
                     .filterBounds(aoi)
                     .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.config["processing"]["cloud_cover_threshold"])))
        
        images = []
        for i, image in enumerate(collection.toList(self.config["processing"]["max_images_per_request"]).getInfo()):
            try:
                img = ee.Image(image['id'])
                
                # Select bands
                img_selected = img.select(bands)
                
                # Get image properties
                properties = img.getInfo()['properties']
                
                # Calculate NDVI
                ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
                
                # Calculate other indices
                evi = img.expression(
                    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                    {'NIR': img.select('B8'), 'RED': img.select('B4'), 'BLUE': img.select('B2')}
                ).rename('EVI')
                
                # Combine all bands
                img_with_indices = img_selected.addBands([ndvi, evi])
                
                # Get image bounds
                img_bounds = img.geometry().bounds().getInfo()['coordinates'][0]
                min_lon = min([coord[0] for coord in img_bounds])
                min_lat = min([coord[1] for coord in img_bounds])
                max_lon = max([coord[0] for coord in img_bounds])
                max_lat = max([coord[1] for coord in img_bounds])
                
                satellite_image = SatelliteImage(
                    image_id=image['id'],
                    source='GEE',
                    timestamp=datetime.fromisoformat(properties['system:time_start'][:-1]),
                    bounds=(min_lon, min_lat, max_lon, max_lat),
                    bands={},  # Will be populated when downloaded
                    metadata={
                        'cloud_cover': properties.get('CLOUDY_PIXEL_PERCENTAGE', 0),
                        'sun_azimuth': properties.get('MEAN_SOLAR_AZIMUTH_ANGLE', 0),
                        'sun_elevation': properties.get('MEAN_SOLAR_ZENITH_ANGLE', 0),
                        'bands': bands + ['NDVI', 'EVI']
                    }
                )
                
                images.append(satellite_image)
                
            except Exception as e:
                logging.error(f"Error processing image {i}: {e}")
                continue
        
        return images
    
    def get_landsat8_data(self,
                         bounds: Tuple[float, float, float, float],
                         start_date: datetime,
                         end_date: datetime,
                         bands: List[str] = None) -> List[SatelliteImage]:
        """Get Landsat-8 data from Google Earth Engine"""
        if not EE_AVAILABLE:
            raise RuntimeError("Google Earth Engine not available")
        
        if bands is None:
            bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']  # Blue, Green, Red, NIR, SWIR1, SWIR2
        
        aoi = ee.Geometry.Rectangle(bounds)
        
        collection = (ee.ImageCollection(self.config["gee"]["assets"]["landsat8"])
                     .filterBounds(aoi)
                     .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                     .filter(ee.Filter.lt('CLOUD_COVER', self.config["processing"]["cloud_cover_threshold"])))
        
        images = []
        for i, image in enumerate(collection.toList(self.config["processing"]["max_images_per_request"]).getInfo()):
            try:
                img = ee.Image(image['id'])
                img_selected = img.select(bands)
                
                # Calculate NDVI
                ndvi = img.normalizedDifference(['B5', 'B4']).rename('NDVI')
                
                # Calculate other vegetation indices
                savi = img.expression(
                    '((NIR - RED) / (NIR + RED + 0.5)) * 1.5',
                    {'NIR': img.select('B5'), 'RED': img.select('B4')}
                ).rename('SAVI')
                
                img_with_indices = img_selected.addBands([ndvi, savi])
                
                properties = img.getInfo()['properties']
                
                img_bounds = img.geometry().bounds().getInfo()['coordinates'][0]
                min_lon = min([coord[0] for coord in img_bounds])
                min_lat = min([coord[1] for coord in img_bounds])
                max_lon = max([coord[0] for coord in img_bounds])
                max_lat = max([coord[1] for coord in img_bounds])
                
                satellite_image = SatelliteImage(
                    image_id=image['id'],
                    source='GEE',
                    timestamp=datetime.fromisoformat(properties['system:time_start'][:-1]),
                    bounds=(min_lon, min_lat, max_lon, max_lat),
                    bands={},
                    metadata={
                        'cloud_cover': properties.get('CLOUD_COVER', 0),
                        'sun_azimuth': properties.get('SUN_AZIMUTH', 0),
                        'sun_elevation': properties.get('SUN_ELEVATION', 0),
                        'bands': bands + ['NDVI', 'SAVI']
                    }
                )
                
                images.append(satellite_image)
                
            except Exception as e:
                logging.error(f"Error processing Landsat image {i}: {e}")
                continue
        
        return images
    
    def calculate_vegetation_indices(self, image: SatelliteImage) -> Dict[str, float]:
        """Calculate vegetation indices from satellite image"""
        indices = {}
        
        if 'NDVI' in image.metadata['bands']:
            # NDVI calculation would be done here with actual band data
            indices['ndvi_mean'] = 0.5  # Placeholder
            indices['ndvi_std'] = 0.1
        
        if 'EVI' in image.metadata['bands']:
            indices['evi_mean'] = 0.3  # Placeholder
            indices['evi_std'] = 0.05
        
        return indices
    
    def process_for_ml(self, images: List[SatelliteImage]) -> pd.DataFrame:
        """Process satellite images for ML model input"""
        ml_data = []
        
        for image in images:
            # Calculate vegetation indices
            indices = self.calculate_vegetation_indices(image)
            
            # Extract features for ML
            features = {
                'image_id': image.image_id,
                'timestamp': image.timestamp,
                'source': image.source,
                'cloud_cover': image.metadata.get('cloud_cover', 0),
                **indices
            }
            
            ml_data.append(features)
        
        return pd.DataFrame(ml_data)
    
    def download_and_save(self, 
                         images: List[SatelliteImage], 
                         output_dir: str = "data/satellite") -> List[str]:
        """Download satellite images and save to disk"""
        os.makedirs(output_dir, exist_ok=True)
        saved_files = []
        
        for image in images:
            try:
                # This would contain actual download logic
                # For now, save metadata
                filename = f"{image.image_id}_{image.timestamp.strftime('%Y%m%d')}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w') as f:
                    json.dump({
                        'image_id': image.image_id,
                        'source': image.source,
                        'timestamp': image.timestamp.isoformat(),
                        'bounds': image.bounds,
                        'metadata': image.metadata
                    }, f, indent=2)
                
                saved_files.append(filepath)
                
            except Exception as e:
                logging.error(f"Error saving image {image.image_id}: {e}")
                continue
        
        return saved_files

def main():
    """Example usage of the remote sensing pipeline"""
    pipeline = RemoteSensingPipeline()
    
    # Define area of interest (example: a field in India)
    bounds = (77.0, 28.0, 77.1, 28.1)  # Delhi area
    
    # Get data for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        # Get Sentinel-2 data
        sentinel_images = pipeline.get_sentinel2_data(bounds, start_date, end_date)
        print(f"Found {len(sentinel_images)} Sentinel-2 images")
        
        # Get Landsat-8 data
        landsat_images = pipeline.get_landsat8_data(bounds, start_date, end_date)
        print(f"Found {len(landsat_images)} Landsat-8 images")
        
        # Process for ML
        all_images = sentinel_images + landsat_images
        ml_df = pipeline.process_for_ml(all_images)
        print(f"Processed {len(ml_df)} images for ML")
        
        # Save data
        saved_files = pipeline.download_and_save(all_images)
        print(f"Saved {len(saved_files)} image metadata files")
        
    except Exception as e:
        logging.error(f"Pipeline error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
