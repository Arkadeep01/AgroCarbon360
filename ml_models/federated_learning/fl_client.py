"""
Federated Learning Client for AgroCarbon360
Participates in decentralized model training
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass
import asyncio
import aiohttp
import pickle
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

@dataclass
class TrainingData:
    """Container for training data"""
    features: np.ndarray
    targets: np.ndarray
    data_size: int

class FederatedLearningClient:
    """Client for participating in federated learning"""
    
    def __init__(self, client_id: str, config_path: str = "config/fl_client_config.json"):
        self.client_id = client_id
        self.config = self._load_config(config_path)
        self.local_model = None
        self.global_model = None
        self.training_data = None
        self.server_url = self.config["server"]["url"]
        self.model_type = self.config["model"]["type"]
        
    def _load_config(self, config_path: str) -> Dict:
        """Load client configuration"""
        default_config = {
            "client": {
                "name": "Farmer Client",
                "location": "Unknown",
                "data_path": "data/local_training_data.csv"
            },
            "server": {
                "url": "http://localhost:8080",
                "timeout": 30
            },
            "model": {
                "type": "ch4_model",  # or 'biomass_model'
                "features": ["soil_moisture", "soil_ph", "soil_temp_c", "air_temp_c", "rain_last_7d_mm", "ec"],
                "target": "ch4_emissions"
            },
            "training": {
                "local_epochs": 5,
                "batch_size": 32,
                "learning_rate": 0.01
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def load_local_data(self) -> bool:
        """Load local training data"""
        try:
            data_path = self.config["client"]["data_path"]
            if not os.path.exists(data_path):
                logging.error(f"Training data not found at {data_path}")
                return False
            
            # Load data
            df = pd.read_csv(data_path)
            
            # Extract features and targets
            features = df[self.config["model"]["features"]].values
            targets = df[self.config["model"]["target"]].values
            
            # Handle missing values
            features = np.nan_to_num(features, nan=0.0)
            targets = np.nan_to_num(targets, nan=0.0)
            
            self.training_data = TrainingData(
                features=features,
                targets=targets,
                data_size=len(features)
            )
            
            logging.info(f"Loaded {self.training_data.data_size} training samples")
            return True
            
        except Exception as e:
            logging.error(f"Error loading local data: {e}")
            return False
    
    def initialize_model(self):
        """Initialize local model"""
        if self.model_type == "ch4_model":
            self.local_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif self.model_type == "biomass_model":
            self.local_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        logging.info(f"Initialized {self.model_type} model")
    
    def train_local_model(self) -> Dict:
        """Train local model on local data"""
        if not self.training_data:
            logging.error("No training data available")
            return None
        
        try:
            # Train model
            self.local_model.fit(self.training_data.features, self.training_data.targets)
            
            # Evaluate model
            predictions = self.local_model.predict(self.training_data.features)
            mse = np.mean((predictions - self.training_data.targets) ** 2)
            r2 = self.local_model.score(self.training_data.features, self.training_data.targets)
            
            # Extract model parameters (simplified for RandomForest)
            model_params = {
                "feature_importances": self.local_model.feature_importances_.tolist(),
                "n_estimators": self.local_model.n_estimators,
                "max_depth": self.local_model.max_depth
            }
            
            training_result = {
                "model": model_params,
                "data_size": self.training_data.data_size,
                "performance": {
                    "mse": float(mse),
                    "r2": float(r2)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Trained local model - MSE: {mse:.4f}, R2: {r2:.4f}")
            return training_result
            
        except Exception as e:
            logging.error(f"Error training local model: {e}")
            return None
    
    def update_global_model(self, global_model: Dict):
        """Update local model with global model parameters"""
        try:
            # For RandomForest, we'll update feature importances and hyperparameters
            if "feature_importances" in global_model:
                # Create new model with updated parameters
                self.local_model = RandomForestRegressor(
                    n_estimators=global_model.get("n_estimators", 100),
                    max_depth=global_model.get("max_depth", 10),
                    random_state=42
                )
                
                # Retrain with local data
                self.local_model.fit(self.training_data.features, self.training_data.targets)
                
                logging.info("Updated local model with global parameters")
                return True
            else:
                logging.warning("Global model format not recognized")
                return False
                
        except Exception as e:
            logging.error(f"Error updating global model: {e}")
            return False
    
    async def register_with_server(self) -> bool:
        """Register client with federated learning server"""
        try:
            registration_data = {
                "client_id": self.client_id,
                "name": self.config["client"]["name"],
                "location": self.config["client"]["location"],
                "data_size": self.training_data.data_size if self.training_data else 0,
                "model_type": self.model_type
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.server_url}/register", json=registration_data) as response:
                    if response.status == 200:
                        logging.info(f"Successfully registered with server as {self.client_id}")
                        return True
                    else:
                        logging.error(f"Failed to register with server: {response.status}")
                        return False
                        
        except Exception as e:
            logging.error(f"Error registering with server: {e}")
            return False
    
    async def participate_in_training_round(self, round_id: int) -> bool:
        """Participate in a training round"""
        try:
            # Train local model
            training_result = self.train_local_model()
            if not training_result:
                return False
            
            # Send training result to server
            training_result["round_id"] = round_id
            training_result["client_id"] = self.client_id
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.server_url}/submit_model", json=training_result) as response:
                    if response.status == 200:
                        logging.info(f"Successfully submitted model for round {round_id}")
                        return True
                    else:
                        logging.error(f"Failed to submit model: {response.status}")
                        return False
                        
        except Exception as e:
            logging.error(f"Error participating in training round: {e}")
            return False
    
    async def get_global_model(self) -> Optional[Dict]:
        """Get latest global model from server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/global_model") as response:
                    if response.status == 200:
                        global_model = await response.json()
                        return global_model
                    else:
                        logging.error(f"Failed to get global model: {response.status}")
                        return None
                        
        except Exception as e:
            logging.error(f"Error getting global model: {e}")
            return None
    
    async def check_training_status(self) -> Optional[Dict]:
        """Check current training status from server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/status") as response:
                    if response.status == 200:
                        status = await response.json()
                        return status
                    else:
                        logging.error(f"Failed to get training status: {response.status}")
                        return None
                        
        except Exception as e:
            logging.error(f"Error getting training status: {e}")
            return None
    
    async def run_client(self):
        """Run the federated learning client"""
        logging.info(f"Starting federated learning client {self.client_id}")
        
        # Load local data
        if not self.load_local_data():
            logging.error("Failed to load local data. Exiting.")
            return
        
        # Initialize model
        self.initialize_model()
        
        # Register with server
        if not await self.register_with_server():
            logging.error("Failed to register with server. Exiting.")
            return
        
        # Main client loop
        while True:
            try:
                # Check training status
                status = await self.check_training_status()
                if not status:
                    await asyncio.sleep(60)
                    continue
                
                # Check if there's an active training round
                if status.get("current_round"):
                    round_id = status["current_round"]
                    
                    # Check if we're participating in this round
                    if self.client_id in status.get("participants", []):
                        # Participate in training
                        await self.participate_in_training_round(round_id)
                
                # Get latest global model
                global_model = await self.get_global_model()
                if global_model:
                    self.update_global_model(global_model)
                
                # Wait before next iteration
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logging.error(f"Error in client loop: {e}")
                await asyncio.sleep(60)

def main():
    """Main function to run the federated learning client"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fl_client.py <client_id>")
        sys.exit(1)
    
    client_id = sys.argv[1]
    
    logging.basicConfig(level=logging.INFO)
    
    client = FederatedLearningClient(client_id)
    
    # Run client
    asyncio.run(client.run_client())

if __name__ == "__main__":
    main()
