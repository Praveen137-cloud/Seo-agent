from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import Audit, Recommendation

router = APIRouter(prefix="/api", tags=["recommendations"])

@router.get("/audit/{audit_id}/recommendations")
def get_audit_recommendations(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    recs = db.query(Recommendation).filter(Recommendation.audit_id == audit_id).all()
    return [{
        "id": r.id,
        "category": r.category,
        "priority": r.priority,
        "title": r.title,
        "explanation": r.explanation,
        "actionable_steps": r.actionable_steps,
        "suggested_content": r.suggested_content
    } for r in recs]
