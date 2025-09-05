"""
Federated Learning Server for AgroCarbon360
Manages decentralized model training across multiple farmers/FPOs
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
from concurrent.futures import ThreadPoolExecutor
import pickle
import joblib

@dataclass
class ClientInfo:
    """Information about a federated learning client"""
    client_id: str
    name: str
    location: str
    data_size: int
    last_seen: datetime
    status: str  # 'active', 'inactive', 'training'
    model_version: str

@dataclass
class TrainingRound:
    """Information about a training round"""
    round_id: int
    start_time: datetime
    end_time: Optional[datetime]
    participants: List[str]
    global_model_version: str
    status: str  # 'active', 'completed', 'failed'

class FederatedLearningServer:
    """Server for managing federated learning across multiple clients"""
    
    def __init__(self, config_path: str = "config/fl_config.json"):
        self.config = self._load_config(config_path)
        self.clients: Dict[str, ClientInfo] = {}
        self.training_rounds: List[TrainingRound] = []
        self.current_round: Optional[TrainingRound] = None
        self.global_model = None
        self.model_history: List[Dict] = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load federated learning configuration"""
        default_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "max_clients": 100
            },
            "training": {
                "rounds_per_epoch": 10,
                "min_clients_per_round": 3,
                "max_clients_per_round": 20,
                "training_timeout": 3600,  # 1 hour
                "model_aggregation": "fedavg"  # or 'fedprox', 'fednova'
            },
            "models": {
                "ch4_model": {
                    "type": "regression",
                    "features": ["soil_moisture", "soil_ph", "soil_temp_c", "air_temp_c", "rain_last_7d_mm", "ec"],
                    "target": "ch4_emissions"
                },
                "biomass_model": {
                    "type": "regression", 
                    "features": ["dbh", "height", "species_encoded", "age", "density"],
                    "target": "biomass_kg"
                }
            },
            "backend_url": "http://localhost:8000"
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def register_client(self, client_id: str, name: str, location: str, data_size: int) -> bool:
        """Register a new client for federated learning"""
        if len(self.clients) >= self.config["server"]["max_clients"]:
            logging.warning(f"Maximum clients reached. Cannot register {client_id}")
            return False
        
        client_info = ClientInfo(
            client_id=client_id,
            name=name,
            location=location,
            data_size=data_size,
            last_seen=datetime.now(),
            status='active',
            model_version='initial'
        )
        
        self.clients[client_id] = client_info
        logging.info(f"Registered client {client_id} ({name}) from {location}")
        return True
    
    def update_client_status(self, client_id: str, status: str, model_version: str = None):
        """Update client status and model version"""
        if client_id in self.clients:
            self.clients[client_id].status = status
            self.clients[client_id].last_seen = datetime.now()
            if model_version:
                self.clients[client_id].model_version = model_version
    
    def get_active_clients(self) -> List[ClientInfo]:
        """Get list of active clients"""
        active_clients = []
        for client in self.clients.values():
            if client.status == 'active':
                # Check if client was seen recently (within last hour)
                if (datetime.now() - client.last_seen).seconds < 3600:
                    active_clients.append(client)
        return active_clients
    
    def start_training_round(self) -> Optional[TrainingRound]:
        """Start a new training round"""
        active_clients = self.get_active_clients()
        
        if len(active_clients) < self.config["training"]["min_clients_per_round"]:
            logging.warning(f"Not enough active clients for training round. Need {self.config['training']['min_clients_per_round']}, have {len(active_clients)}")
            return None
        
        # Select clients for this round
        max_clients = min(len(active_clients), self.config["training"]["max_clients_per_round"])
        selected_clients = np.random.choice(active_clients, size=max_clients, replace=False)
        
        round_id = len(self.training_rounds) + 1
        training_round = TrainingRound(
            round_id=round_id,
            start_time=datetime.now(),
            end_time=None,
            participants=[client.client_id for client in selected_clients],
            global_model_version=f"round_{round_id}",
            status='active'
        )
        
        self.training_rounds.append(training_round)
        self.current_round = training_round
        
        # Update client statuses
        for client in selected_clients:
            self.update_client_status(client.client_id, 'training')
        
        logging.info(f"Started training round {round_id} with {len(selected_clients)} clients")
        return training_round
    
    def aggregate_models(self, client_models: List[Dict]) -> Dict:
        """Aggregate client models using FedAvg"""
        if not client_models:
            return None
        
        # Simple FedAvg implementation
        aggregated_model = {}
        
        # Get model keys from first client
        model_keys = list(client_models[0]['model'].keys())
        
        for key in model_keys:
            # Calculate weighted average of model parameters
            weighted_sum = np.zeros_like(client_models[0]['model'][key])
            total_weight = 0
            
            for client_model in client_models:
                weight = client_model['data_size']
                weighted_sum += client_model['model'][key] * weight
                total_weight += weight
            
            aggregated_model[key] = weighted_sum / total_weight
        
        return aggregated_model
    
    def complete_training_round(self, round_id: int, client_models: List[Dict]) -> bool:
        """Complete a training round and update global model"""
        if not self.current_round or self.current_round.round_id != round_id:
            logging.error(f"No active training round with ID {round_id}")
            return False
        
        try:
            # Aggregate models
            aggregated_model = self.aggregate_models(client_models)
            if aggregated_model is None:
                logging.error("Failed to aggregate models")
                return False
            
            # Update global model
            self.global_model = aggregated_model
            
            # Save model
            model_path = f"models/global_model_round_{round_id}.pkl"
            os.makedirs("models", exist_ok=True)
            with open(model_path, 'wb') as f:
                pickle.dump(aggregated_model, f)
            
            # Update training round
            self.current_round.end_time = datetime.now()
            self.current_round.status = 'completed'
            
            # Update client statuses
            for client_id in self.current_round.participants:
                self.update_client_status(client_id, 'active', f"round_{round_id}")
            
            # Log model performance
            model_info = {
                "round_id": round_id,
                "timestamp": datetime.now().isoformat(),
                "participants": len(client_models),
                "model_path": model_path,
                "performance": self._evaluate_global_model()
            }
            self.model_history.append(model_info)
            
            logging.info(f"Completed training round {round_id} with {len(client_models)} participants")
            
            # Clear current round
            self.current_round = None
            
            return True
            
        except Exception as e:
            logging.error(f"Error completing training round {round_id}: {e}")
            return False
    
    def _evaluate_global_model(self) -> Dict:
        """Evaluate global model performance"""
        # This would contain actual model evaluation logic
        return {
            "accuracy": 0.85,
            "loss": 0.15,
            "f1_score": 0.82
        }
    
    def get_global_model(self) -> Optional[Dict]:
        """Get current global model"""
        return self.global_model
    
    def get_training_status(self) -> Dict:
        """Get current training status"""
        active_clients = self.get_active_clients()
        
        status = {
            "total_clients": len(self.clients),
            "active_clients": len(active_clients),
            "current_round": self.current_round.round_id if self.current_round else None,
            "total_rounds": len(self.training_rounds),
            "global_model_version": self.glients[list(self.clients.keys())[0]].model_version if self.clients else "none"
        }
        
        return status
    
    async def sync_with_backend(self):
        """Sync federated learning data with backend"""
        try:
            async with aiohttp.ClientSession() as session:
                # Send training status to backend
                status = self.get_training_status()
                async with session.post(f"{self.config['backend_url']}/api/fl/status", json=status) as response:
                    if response.status == 200:
                        logging.info("Synced training status with backend")
                    else:
                        logging.error(f"Failed to sync status: {response.status}")
                
                # Send model updates to backend
                if self.global_model:
                    model_data = {
                        "model": self.global_model,
                        "version": f"round_{len(self.training_rounds)}",
                        "timestamp": datetime.now().isoformat()
                    }
                    async with session.post(f"{self.config['backend_url']}/api/fl/model", json=model_data) as response:
                        if response.status == 200:
                            logging.info("Synced global model with backend")
                        else:
                            logging.error(f"Failed to sync model: {response.status}")
                            
        except Exception as e:
            logging.error(f"Error syncing with backend: {e}")
    
    async def run_server(self):
        """Run the federated learning server"""
        logging.info("Starting federated learning server...")
        
        while True:
            try:
                # Check if we should start a new training round
                if not self.current_round:
                    active_clients = self.get_active_clients()
                    if len(active_clients) >= self.config["training"]["min_clients_per_round"]:
                        self.start_training_round()
                
                # Sync with backend
                await self.sync_with_backend()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error in server loop: {e}")
                await asyncio.sleep(60)

def main():
    """Main function to run the federated learning server"""
    logging.basicConfig(level=logging.INFO)
    
    server = FederatedLearningServer()
    
    # Run server
    asyncio.run(server.run_server())

if __name__ == "__main__":
    main()
