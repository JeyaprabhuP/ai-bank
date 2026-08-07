from fastapi import APIRouter, Depends, HTTPException
from models.schemas import FraudAlertActionRequest, FraudAlertInitiateChatRequest
from utils.security import get_current_user
from services.fraud_service import FraudService

router = APIRouter(tags=["Fraud"])


@router.get("/fraud-alerts")
def list_fraud_alerts(
    priority: str = None,
    status: str = None,
    alert_id: str = None,
    customer_id: str = None,
    customer_name: str = None,
    resolved_by: str = None,
    recommended_action: str = None,
    source: str = None,
    chat_initiated: bool = None,
    min_risk_score: int = None,
    max_risk_score: int = None,
    limit: int = 200,
    user=Depends(get_current_user),
):
    return FraudService.list_alerts(
        priority=priority,
        status=status,
        alert_id=alert_id,
        customer_id=customer_id,
        customer_name=customer_name,
        resolved_by=resolved_by,
        recommended_action=recommended_action,
        source=source,
        chat_initiated=chat_initiated,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
        limit=limit,
    )


@router.get("/fraud-alerts/{alert_id}")
def get_fraud_alert(alert_id: str, user=Depends(get_current_user)):
    details = FraudService.get_alert_details(alert_id)
    if not details:
        raise HTTPException(status_code=404, detail="Fraud alert not found")
    return details


@router.post("/fraud-alerts/{alert_id}/action")
def apply_fraud_alert_action(alert_id: str, payload: FraudAlertActionRequest, user=Depends(get_current_user)):
    return FraudService.apply_supervisor_action(
        alert_id=alert_id,
        action=payload.action,
        mark_resolved=payload.mark_resolved,
        note=payload.note,
    )


@router.post("/fraud-alerts/{alert_id}/initiate-chat")
def initiate_fraud_alert_chat(alert_id: str, payload: FraudAlertInitiateChatRequest, user=Depends(get_current_user)):
    try:
        updated = FraudService.initiate_chat(
            alert_id=alert_id,
            initiated_by=payload.initiated_by or user.get("username"),
            note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=404, detail="Fraud alert not found")

    return updated
