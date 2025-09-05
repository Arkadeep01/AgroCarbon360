import sys
import json
from pathlib import Path

# Ensure backend root is on path
backend_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_root))

import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def run():
    client = TestClient(main.app)

    results = {}
    # Health and root
    results["health"] = client.get("/health").json()
    results["root"] = client.get("/").json()

    # Ingestion
    results["ingestion_task_status"] = client.get("/ingestion/satellite/tasks/sat-xyz").json()

    # ML
    ch4_req = {"rice_area_ha": 1.2, "flooding_days": 45, "water_depth_cm": 10, "practice": "AWD"}
    results["ml_ch4"] = client.post("/ml/estimate/ch4", json=ch4_req).json()
    biomass_req = {"canopy_cover": 0.6, "ndvi_mean": 0.7, "lidar_height_m": 5.0}
    results["ml_biomass"] = client.post("/ml/estimate/biomass", json=biomass_req).json()

    # Federated Learning
    results["fl_global_model"] = client.get("/fl/global-model").json()

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run()


