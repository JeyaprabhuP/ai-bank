from fastapi import APIRouter, Depends, HTTPException
from utils.security import get_current_user
from services.customer_service import CustomerService

router = APIRouter(tags=["Customers"])


@router.get("/customers")
def list_customers(limit: int = 50, user=Depends(get_current_user)):
    return CustomerService.list_customers(limit)


@router.get("/customer/{customer_id}")
def get_customer(customer_id: str, user=Depends(get_current_user)):
    customer = CustomerService.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    accounts = CustomerService.get_accounts_for_customer(customer_id)
    return {**customer, "accounts": accounts}
