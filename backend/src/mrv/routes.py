from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.auth.permissions import require_role
from src.db.dependency import get_db
from . import models, schemas
from src.blockchain.ledger_client import CarbonCreditsClient
import os

router = APIRouter(prefix="/mrv", tags=["mrv"])


@router.post("/reports", response_model=schemas.MRVReportOut)
def create_mrv_report(body: schemas.MRVReportCreate, current_user = Depends(require_role("auditor")), db: Session = Depends(get_db)):
    record = models.MRVReport(**body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/credits/mint")
def mint_credits(project_id: str, amount: int, to_address: str, methodology: str = "IPCC-2006", location: str = "", vintage_year: int = 2024, verification_id: str = "", current_user = Depends(require_role("auditor"))):
    contract_address = os.getenv("CARBON_CREDITS_CONTRACT_ADDRESS")
    rpc_url = os.getenv("BLOCKCHAIN_RPC_URL", "https://polygon-rpc.com")
    private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
    if not contract_address or not private_key:
        return {"status": "skipped", "reason": "Blockchain env not configured"}
    try:
        client = CarbonCreditsClient(rpc_url=rpc_url, contract_address=contract_address, private_key=private_key)
        tx = client.mint_carbon_credits(
            to_address=to_address,
            amount=amount,
            project_id=project_id,
            verification_id=verification_id or f"verif-{project_id}",
            methodology=methodology,
            location=location,
            vintage_year=vintage_year,
        )
        return {"status": "submitted", "tx_hash": tx}
    except Exception as e:
        return {"status": "error", "message": str(e)}

