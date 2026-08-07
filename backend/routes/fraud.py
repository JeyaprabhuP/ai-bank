from fastapi import APIRouter, Depends
from utils.security import get_current_user
from services.fraud_service import FraudService

router = APIRouter(tags=["Fraud"])


@router.get("/fraud-alerts")
def list_fraud_alerts(priority: str = None, status: str = None, limit: int = 200, user=Depends(get_current_user)):
    return FraudService.list_alerts(priority=priority, status=status, limit=limit)
