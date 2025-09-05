"""
Data Pipeline Orchestration for AgroCarbon360
Manages data flows from IoT, satellite, and external sources
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

@dataclass
class DataSource:
    """Configuration for a data source"""
    name: str
    source_type: str  # 'iot', 'satellite', 'external_api', 'manual'
    endpoint: Optional[str] = None
    credentials: Optional[Dict] = None
    schedule: Optional[str] = None  # cron expression
    enabled: bool = True

class DataPipelineOrchestrator:
    """Orchestrates data collection from multiple sources"""
    
    def __init__(self, config_path: str = "config/pipeline_config.json"):
        self.config = self._load_config(config_path)
        self.data_sources = self._load_data_sources()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load pipeline configuration"""
        default_config = {
            "backend_url": "http://localhost:8000",
            "data_storage": {
                "base_path": "data",
                "iot_data": "data/iot",
                "satellite_data": "data/satellite",
                "processed_data": "data/processed"
            },
            "processing": {
                "batch_size": 1000,
                "retry_attempts": 3,
                "timeout_seconds": 30
            },
            "scheduling": {
                "iot_collection_interval": 300,  # 5 minutes
                "satellite_collection_interval": 86400,  # 24 hours
                "processing_interval": 3600  # 1 hour
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _load_data_sources(self) -> List[DataSource]:
        """Load configured data sources"""
        sources = [
            DataSource(
                name="iot_devices",
                source_type="iot",
                endpoint=f"{self.config['backend_url']}/api/iot/readings",
                schedule="*/5 * * * *"  # Every 5 minutes
            ),
            DataSource(
                name="sentinel2",
                source_type="satellite",
                schedule="0 2 * * *"  # Daily at 2 AM
            ),
            DataSource(
                name="weather_api",
                source_type="external_api",
                endpoint="https://api.openweathermap.org/data/2.5/weather",
                schedule="0 */6 * * *"  # Every 6 hours
            )
        ]
        return sources
    
    async def collect_iot_data(self) -> List[Dict]:
        """Collect IoT sensor data from backend"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config['backend_url']}/api/iot/readings") as response:
                    if response.status == 200:
                        data = await response.json()
                        logging.info(f"Collected {len(data)} IoT readings")
                        return data
                    else:
                        logging.error(f"Failed to collect IoT data: {response.status}")
                        return []
        except Exception as e:
            logging.error(f"Error collecting IoT data: {e}")
            return []
    
    async def collect_satellite_data(self) -> List[Dict]:
        """Collect satellite data using remote sensing pipeline"""
        try:
            # Import remote sensing pipeline
            from remote_sensing import RemoteSensingPipeline
            
            pipeline = RemoteSensingPipeline()
            
            # Get data for configured areas
            areas = self.config.get("satellite_areas", [
                {"name": "default", "bounds": [77.0, 28.0, 77.1, 28.1]}
            ])
            
            all_images = []
            for area in areas:
                bounds = tuple(area["bounds"])
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)  # Last week
                
                # Get Sentinel-2 data
                sentinel_images = pipeline.get_sentinel2_data(bounds, start_date, end_date)
                all_images.extend(sentinel_images)
                
                # Get Landsat-8 data
                landsat_images = pipeline.get_landsat8_data(bounds, start_date, end_date)
                all_images.extend(landsat_images)
            
            # Process and save
            ml_df = pipeline.process_for_ml(all_images)
            saved_files = pipeline.download_and_save(all_images)
            
            logging.info(f"Collected {len(all_images)} satellite images")
            return [{"images": len(all_images), "files": saved_files}]
            
        except Exception as e:
            logging.error(f"Error collecting satellite data: {e}")
            return []
    
    async def collect_weather_data(self) -> List[Dict]:
        """Collect weather data from external API"""
        try:
            weather_api_key = self.config.get("weather_api_key")
            if not weather_api_key:
                logging.warning("Weather API key not configured")
                return []
            
            # Get weather for configured locations
            locations = self.config.get("weather_locations", [
                {"name": "Delhi", "lat": 28.6139, "lon": 77.2090}
            ])
            
            weather_data = []
            async with aiohttp.ClientSession() as session:
                for location in locations:
                    url = f"{self.config['backend_url']}/api/weather"
                    params = {
                        "lat": location["lat"],
                        "lon": location["lon"],
                        "appid": weather_api_key
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            weather_data.append({
                                "location": location["name"],
                                "timestamp": datetime.now().isoformat(),
                                "data": data
                            })
            
            logging.info(f"Collected weather data for {len(weather_data)} locations")
            return weather_data
            
        except Exception as e:
            logging.error(f"Error collecting weather data: {e}")
            return []
    
    def process_iot_data(self, iot_data: List[Dict]) -> pd.DataFrame:
        """Process IoT data for ML models"""
        if not iot_data:
            return pd.DataFrame()
        
        processed_data = []
        for reading in iot_data:
            processed_reading = {
                "device_id": reading.get("device_id"),
                "timestamp": reading.get("timestamp"),
                "soil_moisture": reading.get("soil_moisture"),
                "soil_ph": reading.get("soil_ph"),
                "soil_temp_c": reading.get("soil_temp_c"),
                "air_temp_c": reading.get("air_temp_c"),
                "humidity": reading.get("humidity"),
                "rainfall_mm": reading.get("rainfall_mm"),
                "ec": reading.get("ec")
            }
            processed_data.append(processed_reading)
        
        df = pd.DataFrame(processed_data)
        
        # Add derived features
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_year'] = df['timestamp'].dt.dayofyear
            
            # Calculate rolling averages
            df = df.sort_values('timestamp')
            df['soil_moisture_7d_avg'] = df.groupby('device_id')['soil_moisture'].rolling(7).mean().values
            df['air_temp_7d_avg'] = df.groupby('device_id')['air_temp_c'].rolling(7).mean().values
        
        return df
    
    def process_satellite_data(self, satellite_data: List[Dict]) -> pd.DataFrame:
        """Process satellite data for ML models"""
        if not satellite_data:
            return pd.DataFrame()
        
        processed_data = []
        for data in satellite_data:
            processed_data.append({
                "timestamp": datetime.now().isoformat(),
                "source": "satellite",
                "images_count": data.get("images", 0),
                "files_saved": len(data.get("files", []))
            })
        
        return pd.DataFrame(processed_data)
    
    def merge_data_sources(self, iot_df: pd.DataFrame, satellite_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
        """Merge data from different sources"""
        merged_df = pd.DataFrame()
        
        if not iot_df.empty:
            merged_df = iot_df.copy()
        
        if not satellite_df.empty:
            if merged_df.empty:
                merged_df = satellite_df.copy()
            else:
                # Merge on timestamp
                merged_df = pd.merge(merged_df, satellite_df, on='timestamp', how='outer')
        
        if not weather_df.empty:
            if merged_df.empty:
                merged_df = weather_df.copy()
            else:
                merged_df = pd.merge(merged_df, weather_df, on='timestamp', how='outer')
        
        return merged_df
    
    async def run_data_collection(self):
        """Run data collection from all sources"""
        logging.info("Starting data collection...")
        
        # Collect data from all sources
        iot_data = await self.collect_iot_data()
        satellite_data = await self.collect_satellite_data()
        weather_data = await self.collect_weather_data()
        
        # Process data
        iot_df = self.process_iot_data(iot_data)
        satellite_df = self.process_satellite_data(satellite_data)
        weather_df = pd.DataFrame(weather_data)
        
        # Merge data
        merged_df = self.merge_data_sources(iot_df, satellite_df, weather_df)
        
        # Save processed data
        if not merged_df.empty:
            output_path = os.path.join(self.config["data_storage"]["processed_data"], 
                                     f"merged_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            merged_df.to_csv(output_path, index=False)
            logging.info(f"Saved merged data to {output_path}")
        
        return merged_df
    
    async def schedule_data_collection(self):
        """Schedule data collection tasks"""
        while True:
            try:
                await self.run_data_collection()
                
                # Wait for next collection interval
                await asyncio.sleep(self.config["scheduling"]["processing_interval"])
                
            except Exception as e:
                logging.error(f"Error in scheduled data collection: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

def main():
    """Main function to run the data pipeline"""
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = DataPipelineOrchestrator()
    
    # Run data collection once
    asyncio.run(orchestrator.run_data_collection())
    
    # Or run continuously
    # asyncio.run(orchestrator.schedule_data_collection())

if __name__ == "__main__":
    main()
