from fastapi import APIRouter, Depends
from utils.security import get_current_user
from services.transaction_service import TransactionService

router = APIRouter(tags=["Transactions"])


@router.get("/transactions")
def list_transactions(customer_id: str = None, limit: int = 100, user=Depends(get_current_user)):
    return TransactionService.list_transactions(customer_id=customer_id, limit=limit)
