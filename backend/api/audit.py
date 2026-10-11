import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl

from ..database.database import get_db
from ..database.models import Audit, Page, SEOIssue, Recommendation
from ..crawler.crawler import WebCrawler, is_valid_public_url
from ..seo_analyzer.title import analyze_titles
from ..seo_analyzer.meta import analyze_meta_descriptions
from ..seo_analyzer.headings import analyze_headings
from ..seo_analyzer.images import analyze_images
from ..seo_analyzer.links import analyze_links
from ..seo_analyzer.mobile_social import analyze_mobile_social
from ..seo_analyzer.indexing import analyze_indexing
from ..seo_analyzer.content import analyze_content
from ..seo_analyzer.url_structure import analyze_url_structure
from ..technical.security import analyze_security
from ..technical.sitemap import analyze_sitemap
from ..technical.canonical import analyze_canonicals
from ..technical.performance import analyze_performance
from ..scoring.scorer import calculate_score
from ..ai.agent import AIAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["audits"])

class AuditCreateRequest(BaseModel):
    url: str
    max_pages: Optional[int] = 50

def run_background_audit(audit_id: str, target_url: str, max_pages: int, db: Session):
    try:
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            return

        audit.status = "crawling"
        db.commit()

        # Real-time crawl progress callback
        def on_crawl_progress(current, total, current_url):
            try:
                audit.pages_crawled = current
                db.commit()
            except Exception:
                pass

        # 1. Crawl Target Domain with live progress
        crawler = WebCrawler(target_url=target_url, max_pages=max_pages, max_depth=3)
        crawled_pages = crawler.crawl(progress_callback=on_crawl_progress)

        # Check if website was actually fetched (at least one page was successfully fetched)
        fetched_pages = [p for p in crawled_pages if p.get("is_fetched", False)]
        if not fetched_pages:
            first_err = crawled_pages[0].get("fetch_error") if crawled_pages else "Connection failed"
            audit.status = "failed"
            audit.error_message = f"Unable to analyze {target_url} ({first_err}). The target web server returned an access error or bot challenge and could not be crawled."
            db.commit()
            return

        audit.status = "analyzing"
        audit.pages_crawled = len(fetched_pages)
        db.commit()

        # Save pages to DB
        db_pages = []
        for p in crawled_pages:
            db_page = Page(
                audit_id=audit_id,
                url=p["url"],
                title=p.get("title"),
                status_code=p.get("status_code"),
                load_time_ms=p.get("load_time_ms"),
                html_size=p.get("html_size"),
                word_count=p.get("word_count", 0),
                h1_tags=p.get("h1_tags", []),
                h2_tags=p.get("h2_tags", []),
                meta_description=p.get("meta_description"),
                canonical_url=p.get("canonical_url"),
                depth=p.get("depth", 0)
            )
            db.add(db_page)
            db_pages.append(db_page)
        db.commit()

        # 2. Run Comprehensive Real-Time Analyzers
        all_issues = []
        all_issues.extend(analyze_titles(crawled_pages))
        all_issues.extend(analyze_meta_descriptions(crawled_pages))
        all_issues.extend(analyze_headings(crawled_pages))
        all_issues.extend(analyze_images(crawled_pages))
        all_issues.extend(analyze_links(crawled_pages, crawler.tested_links))

        # Real-time mobile, social, content, and indexing analyzers
        all_issues.extend(analyze_mobile_social(crawled_pages))
        all_issues.extend(analyze_indexing(crawled_pages))
        all_issues.extend(analyze_content(crawled_pages))
        all_issues.extend(analyze_url_structure(crawled_pages))

        # Technical SEO
        all_issues.extend(analyze_security(target_url, crawled_pages))
        all_issues.extend(analyze_sitemap(target_url, crawler.robots.sitemaps))
        all_issues.extend(analyze_canonicals(crawled_pages))
        all_issues.extend(analyze_performance(crawled_pages))

        # Save issues to DB with verified evidence
        for iss in all_issues:
            db_iss = SEOIssue(
                audit_id=audit_id,
                page_url=iss.get("page_url"),
                category=iss.get("category", "on_page"),
                severity=iss.get("severity", "LOW"),
                issue_code=iss.get("issue_code"),
                title=iss.get("title"),
                description=iss.get("description"),
                recommendation_summary=iss.get("recommendation_summary"),
                impact=iss.get("impact"),
                observed_value=iss.get("observed_value"),
                evidence=iss.get("evidence"),
                verification_status=iss.get("verification_status", "verified")
            )
            db.add(db_iss)
        db.commit()

        # 3. Calculate Score
        audit.status = "scoring"
        db.commit()

        score_res = calculate_score(all_issues, crawled_pages, target_url)
        audit.score = score_res["overall_score"]
        audit.summary_data = score_res
        db.commit()

        # 4. Run AI Agent for Recommendations
        audit.status = "ai_processing"
        db.commit()

        ai_agent = AIAgent()
        # In background worker thread, run sync wrapper for async call
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        recommendations = loop.run_until_complete(
            ai_agent.generate_seo_recommendations(target_url, score_res, all_issues, crawled_pages)
        )
        loop.close()

        # Save recommendations to DB
        for rec in recommendations:
            db_rec = Recommendation(
                audit_id=audit_id,
                category=rec.get("category", "on_page"),
                priority=rec.get("priority", "MEDIUM"),
                title=rec.get("title"),
                explanation=rec.get("explanation"),
                actionable_steps=rec.get("actionable_steps", []),
                suggested_content=rec.get("suggested_content")
            )
            db.add(db_rec)

        audit.status = "completed"
        audit.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        logger.error(f"Audit task failed for {audit_id}: {e}", exc_info=True)
        if audit:
            audit.status = "failed"
            audit.error_message = str(e)
            db.commit()

@router.post("/audit")
def create_audit(req: AuditCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    url = req.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if not is_valid_public_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL: Please enter a valid, public HTTP or HTTPS web address."
        )

    new_audit = Audit(
        target_url=url,
        max_pages=req.max_pages or 50,
        status="pending"
    )
    db.add(new_audit)
    db.commit()
    db.refresh(new_audit)

    background_tasks.add_task(run_background_audit, new_audit.id, new_audit.target_url, new_audit.max_pages, db)

    return {
        "audit_id": new_audit.id,
        "target_url": new_audit.target_url,
        "status": new_audit.status,
        "created_at": new_audit.created_at
    }

@router.get("/audit/{audit_id}")
def get_audit_summary(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    return {
        "id": audit.id,
        "target_url": audit.target_url,
        "status": audit.status,
        "score": audit.score,
        "pages_crawled": audit.pages_crawled,
        "max_pages": audit.max_pages,
        "created_at": audit.created_at,
        "completed_at": audit.completed_at,
        "error_message": audit.error_message,
        "summary_data": audit.summary_data
    }

@router.get("/audit/{audit_id}/issues")
def get_audit_issues(
    audit_id: str,
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(SEOIssue).filter(SEOIssue.audit_id == audit_id)
    if severity:
        query = query.filter(SEOIssue.severity == severity.upper())
    if category:
        query = query.filter(SEOIssue.category == category.lower())

    issues = query.all()
    return [{
        "id": i.id,
        "page_url": i.page_url,
        "category": i.category,
        "severity": i.severity,
        "issue_code": i.issue_code,
        "title": i.title,
        "description": i.description,
        "recommendation_summary": i.recommendation_summary,
        "impact": i.impact,
        "observed_value": i.observed_value,
        "evidence": i.evidence,
        "verification_status": i.verification_status or "verified"
    } for i in issues]

@router.get("/audits")
def list_audits(limit: int = 20, db: Session = Depends(get_db)):
    audits = db.query(Audit).order_by(Audit.created_at.desc()).limit(limit).all()
    return [{
        "id": a.id,
        "target_url": a.target_url,
        "status": a.status,
        "score": a.score,
        "pages_crawled": a.pages_crawled,
        "created_at": a.created_at
    } for a in audits]
