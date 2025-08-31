import json
import os

# Load emission factors once
BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "emission_factors.json"), "r") as f:
    EMISSION_FACTORS = json.load(f)

def calculate_emissions(activity: float, fuel_type: str, region: str = None) -> float:
    """
    Calculate CO₂ emissions using IPCC emission factors.

    :param activity: Amount of fuel consumed (e.g., liters, kWh, etc.)
    :param fuel_type: Type of fuel (e.g., 'diesel', 'gasoline', 'electricity')
    :param region: Optional region for electricity factors
    :return: Emissions in kg CO₂
    """
    if fuel_type not in EMISSION_FACTORS:
        raise ValueError(f"Unknown fuel type: {fuel_type}")

    factor = EMISSION_FACTORS[fuel_type]
    if isinstance(factor, dict):  # electricity with regions
        if not region or region not in factor:
            raise ValueError(f"Region required for {fuel_type}, available: {list(factor.keys())}")
        factor = factor[region]

    return activity * factor
