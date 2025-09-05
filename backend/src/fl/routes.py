from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/fl", tags=["federated-learning"])


class ClientUpdate(BaseModel):
    client_id: str
    weights: List[float]
    num_samples: int


@router.post("/submit")
def submit_update(update: ClientUpdate):
    return {"status": "received", "client_id": update.client_id, "num_samples": update.num_samples}


@router.get("/global-model")
def get_global_model():
    return {"weights": [0.1, 0.2, 0.3], "version": 1}

