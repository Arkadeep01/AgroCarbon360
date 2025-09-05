from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import math
import os
import joblib
import numpy as np
import pandas as pd
import logging
from pathlib import Path

router = APIRouter(prefix="/ml", tags=["ml"])

# Load trained models
MODEL_BASE_PATH = Path(__file__).parent.parent.parent.parent.parent / "ml_models" / "saved_models"

class CH4EstimateRequest(BaseModel):
    soil_moisture: float
    soil_ph: float
    soil_temp_c: float
    air_temp_c: float
    rain_last_7d_mm: float
    ec: float

class BiomassEstimateRequest(BaseModel):
    dbh: float
    height: float
    species: str
    age: Optional[float] = None
    density: Optional[float] = None

class MLModelManager:
    """Manages loading and prediction of ML models"""
    
    def __init__(self):
        self.ch4_model = None
        self.ch4_scaler = None
        self.biomass_model = None
        self.biomass_scaler = None
        self.feature_names = None
        self.load_models()
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Load CH4 model
            ch4_model_path = MODEL_BASE_PATH / "ch4_baseline.pkl"
            ch4_scaler_path = MODEL_BASE_PATH / "scaler.pkl"
            
            if ch4_model_path.exists():
                self.ch4_model = joblib.load(ch4_model_path)
                logging.info("Loaded CH4 model successfully")
            
            if ch4_scaler_path.exists():
                self.ch4_scaler = joblib.load(ch4_scaler_path)
                logging.info("Loaded CH4 scaler successfully")
            
            # Load feature names
            features_path = MODEL_BASE_PATH / "features.json"
            if features_path.exists():
                import json
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
                logging.info("Loaded feature names successfully")
            
            # Load biomass model (if available)
            biomass_model_path = MODEL_BASE_PATH / "biomass_model.pkl"
            if biomass_model_path.exists():
                self.biomass_model = joblib.load(biomass_model_path)
                logging.info("Loaded biomass model successfully")
            
        except Exception as e:
            logging.error(f"Error loading models: {e}")
    
    def predict_ch4(self, features: dict) -> dict:
        """Predict CH4 emissions using trained model"""
        if not self.ch4_model or not self.ch4_scaler:
            raise HTTPException(status_code=500, detail="CH4 model not loaded")
        
        try:
            # Prepare features in correct order
            feature_values = []
            if self.feature_names:
                for feature in self.feature_names:
                    feature_values.append(features.get(feature, 0.0))
            else:
                # Default feature order
                feature_values = [
                    features.get('soil_moisture', 0.0),
                    features.get('soil_ph', 0.0),
                    features.get('soil_temp_c', 0.0),
                    features.get('air_temp_c', 0.0),
                    features.get('rain_last_7d_mm', 0.0),
                    features.get('ec', 0.0)
                ]
            
            # Convert to numpy array and reshape
            X = np.array(feature_values).reshape(1, -1)
            
            # Scale features
            X_scaled = self.ch4_scaler.transform(X)
            
            # Make prediction
            prediction = self.ch4_model.predict(X_scaled)[0]
            
            # Calculate uncertainty (simplified)
            uncertainty = 0.1 * abs(prediction)  # 10% uncertainty
            
            return {
                "ch4_emissions_kg_ha": float(prediction),
                "uncertainty_kg_ha": float(uncertainty),
                "confidence": 0.85
            }
            
        except Exception as e:
            logging.error(f"Error in CH4 prediction: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    
    def predict_biomass(self, features: dict) -> dict:
        """Predict biomass using trained model"""
        if not self.biomass_model:
            # Fallback to simple estimation
            dbh = features.get('dbh', 0.0)
            height = features.get('height', 0.0)
            species = features.get('species', 'unknown')
            
            # Simple allometric equation
            biomass_kg = 0.0673 * (dbh ** 2.4) * (height ** 0.976)
            
            return {
                "biomass_kg": float(biomass_kg),
                "uncertainty_kg": float(0.15 * biomass_kg),
                "confidence": 0.70,
                "method": "allometric_fallback"
            }
        
        try:
            # Prepare features for biomass model
            feature_values = [
                features.get('dbh', 0.0),
                features.get('height', 0.0),
                features.get('age', 0.0),
                features.get('density', 0.0)
            ]
            
            # Convert to numpy array and reshape
            X = np.array(feature_values).reshape(1, -1)
            
            # Make prediction
            prediction = self.biomass_model.predict(X)[0]
            
            # Calculate uncertainty
            uncertainty = 0.12 * abs(prediction)  # 12% uncertainty
            
            return {
                "biomass_kg": float(prediction),
                "uncertainty_kg": float(uncertainty),
                "confidence": 0.88,
                "method": "ml_model"
            }
            
        except Exception as e:
            logging.error(f"Error in biomass prediction: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Initialize model manager
model_manager = MLModelManager()

@router.post("/estimate/ch4")
def estimate_ch4(body: CH4EstimateRequest):
    """Estimate CH4 emissions using trained ML model"""
    features = {
        'soil_moisture': body.soil_moisture,
        'soil_ph': body.soil_ph,
        'soil_temp_c': body.soil_temp_c,
        'air_temp_c': body.air_temp_c,
        'rain_last_7d_mm': body.rain_last_7d_mm,
        'ec': body.ec
    }
    
    return model_manager.predict_ch4(features)

@router.post("/estimate/biomass")
def estimate_biomass(body: BiomassEstimateRequest):
    """Estimate biomass using trained ML model"""
    features = {
        'dbh': body.dbh,
        'height': body.height,
        'species': body.species,
        'age': body.age or 0.0,
        'density': body.density or 0.0
    }
    
    return model_manager.predict_biomass(features)

@router.get("/models/status")
def get_model_status():
    """Get status of loaded ML models"""
    status = {
        "ch4_model_loaded": model_manager.ch4_model is not None,
        "ch4_scaler_loaded": model_manager.ch4_scaler is not None,
        "biomass_model_loaded": model_manager.biomass_model is not None,
        "feature_names_loaded": model_manager.feature_names is not None,
        "model_path": str(MODEL_BASE_PATH)
    }
    return status

