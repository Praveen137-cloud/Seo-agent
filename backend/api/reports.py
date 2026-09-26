from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import Audit, Page, SEOIssue, Recommendation
from ..reports.pdf import generate_pdf_report

router = APIRouter(prefix="/api", tags=["reports"])

@router.get("/audit/{audit_id}/report")
def download_pdf_report(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    pages = db.query(Page).filter(Page.audit_id == audit_id).all()
    issues = db.query(SEOIssue).filter(SEOIssue.audit_id == audit_id).all()
    recommendations = db.query(Recommendation).filter(Recommendation.audit_id == audit_id).all()

    audit_dict = {
        "target_url": audit.target_url,
        "score": audit.score,
        "pages_crawled": audit.pages_crawled,
        "summary_data": audit.summary_data or {}
    }
    pages_list = [{"url": p.url, "title": p.title, "status_code": p.status_code} for p in pages]
    issues_list = [{
        "severity": i.severity,
        "category": i.category,
        "title": i.title,
        "description": i.description,
        "page_url": i.page_url
    } for i in issues]
    recs_list = [{
        "priority": r.priority,
        "category": r.category,
        "title": r.title,
        "explanation": r.explanation,
        "actionable_steps": r.actionable_steps,
        "suggested_content": r.suggested_content
    } for r in recommendations]

    pdf_bytes = generate_pdf_report(audit_dict, pages_list, issues_list, recs_list)

    safe_url = audit.target_url.replace("https://", "").replace("http://", "").replace("/", "_")
    filename = f"SEO_Report_{safe_url}_{audit_id[:8]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
