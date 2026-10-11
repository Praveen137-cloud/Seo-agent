from typing import List, Dict, Any
from urllib.parse import urlparse

def calculate_score(issues: List[Dict[str, Any]], pages: List[Dict[str, Any]], target_url: str = "") -> Dict[str, Any]:
    """
    Calculates an accurate, transparent, and bounded SEO score (0-100) using a
    documented 4-category weighted model:
    - On-Page Content & Metadata: 35 points max
    - Technical SEO & Crawlability: 30 points max
    - Security & HTTPS Protocol:   15 points max
    - Performance & Latency:       20 points max

    Avoids penalty multiplication death spirals and double-counting.
    Calculates health compliance ratios across crawled pages.
    """
    total_pages = len(pages)
    fetched_pages = [p for p in pages if p.get("is_fetched", True)]
    num_fetched = len(fetched_pages)

    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }
    for iss in issues:
        sev = iss.get("severity", "LOW").upper()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["LOW"] += 1

    # If 0 pages were successfully fetched, return transparent provisional zero score
    if num_fetched == 0:
        return {
            "overall_score": 0,
            "grade": "F",
            "status_label": "Audit Incomplete / Unreachable",
            "total_issues": len(issues),
            "severity_counts": severity_counts,
            "section_scores": {
                "on_page": 0,
                "technical": 0,
                "security": 0,
                "performance": 0
            },
            "audit_coverage": 0.0,
            "is_provisional": True,
            "scoring_methodology": "Weighted 4-category model (On-Page 35%, Technical 30%, Security 15%, Performance 20%)"
        }

    # =========================================================================
    # 1. ON-PAGE SEO (35 Points Max)
    # =========================================================================
    # A. Title Tag Health (10 pts)
    pages_with_title = len([p for p in fetched_pages if (p.get("title") or "").strip()])
    title_ratio = pages_with_title / num_fetched
    on_page_title = title_ratio * 10.0

    # B. Meta Description Health (8 pts)
    pages_with_meta = len([p for p in fetched_pages if (p.get("meta_description") or "").strip()])
    meta_ratio = pages_with_meta / num_fetched
    on_page_meta = meta_ratio * 8.0

    # C. Heading Hierarchy H1 (7 pts)
    pages_with_h1 = len([p for p in fetched_pages if p.get("h1_tags") and len(p.get("h1_tags")) > 0])
    h1_ratio = pages_with_h1 / num_fetched
    on_page_h1 = h1_ratio * 7.0

    # D. Image Alt Coverage (5 pts)
    total_images = sum(len(p.get("images", [])) for p in fetched_pages)
    images_with_alt = sum(len([img for img in p.get("images", []) if img.get("has_alt")]) for p in fetched_pages)
    if total_images == 0:
        on_page_images = 5.0
    else:
        on_page_images = (images_with_alt / total_images) * 5.0

    # E. Content Quality (5 pts)
    pages_with_good_content = len([p for p in fetched_pages if p.get("word_count", 0) >= 100])
    content_ratio = pages_with_good_content / num_fetched
    on_page_content = content_ratio * 5.0

    on_page_pts = max(0.0, min(35.0, on_page_title + on_page_meta + on_page_h1 + on_page_images + on_page_content))
    on_page_score_100 = round((on_page_pts / 35.0) * 100)

    # =========================================================================
    # 2. TECHNICAL SEO (30 Points Max)
    # =========================================================================
    # A. HTTP Status Health (10 pts)
    pages_200 = len([p for p in pages if p.get("status_code") == 200])
    status_ratio = pages_200 / total_pages if total_pages > 0 else 1.0
    tech_status = status_ratio * 10.0

    # B. Mobile Viewport (8 pts)
    pages_with_viewport = len([p for p in fetched_pages if (p.get("viewport") or "").strip()])
    viewport_ratio = pages_with_viewport / num_fetched
    tech_viewport = viewport_ratio * 8.0

    # C. Canonical Tags (6 pts)
    pages_with_canonical = len([p for p in fetched_pages if (p.get("canonical_url") or "").strip()])
    canonical_ratio = pages_with_canonical / num_fetched
    tech_canonical = canonical_ratio * 6.0

    # D. Structured Data & Sitemap (6 pts)
    has_sitemap_issue = any(i.get("issue_code") == "MISSING_SITEMAP" for i in issues)
    has_noindex_issue = any(i.get("issue_code") == "PAGE_BLOCKED_BY_NOINDEX" for i in issues)
    tech_indexing = 6.0
    if has_sitemap_issue:
        tech_indexing -= 2.0
    if has_noindex_issue:
        tech_indexing -= 3.0
    tech_indexing = max(1.0, tech_indexing)

    tech_pts = max(0.0, min(30.0, tech_status + tech_viewport + tech_canonical + tech_indexing))
    technical_score_100 = round((tech_pts / 30.0) * 100)

    # =========================================================================
    # 3. SECURITY (15 Points Max)
    # =========================================================================
    parsed_target = urlparse(target_url) if target_url else urlparse(pages[0].get("url", ""))
    is_https = parsed_target.scheme.lower() == "https"
    sec_https = 10.0 if is_https else 0.0

    # Mixed Content / Insecure Links (5 pts)
    has_mixed = any(i.get("issue_code") == "MIXED_CONTENT_PAGES" for i in issues)
    sec_mixed = 2.0 if has_mixed else 5.0

    security_pts = max(0.0, min(15.0, sec_https + sec_mixed))
    security_score_100 = round((security_pts / 15.0) * 100)

    # =========================================================================
    # 4. PERFORMANCE (20 Points Max)
    # =========================================================================
    # A. Server Latency TTFB (12 pts)
    latencies = [p.get("load_time_ms", 0) for p in fetched_pages if p.get("load_time_ms", 0) > 0]
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 500.0
    if avg_latency < 800:
        perf_latency = 12.0
    elif avg_latency < 1500:
        perf_latency = 9.0
    elif avg_latency < 2500:
        perf_latency = 6.0
    else:
        perf_latency = 3.0

    # B. HTML Payload Size (8 pts)
    sizes = [p.get("html_size", 0) for p in fetched_pages if p.get("html_size", 0) > 0]
    avg_size_kb = (sum(sizes) / len(sizes) / 1024.0) if sizes else 50.0
    if avg_size_kb < 150:
        perf_size = 8.0
    elif avg_size_kb < 400:
        perf_size = 6.0
    else:
        perf_size = 3.0

    perf_pts = max(0.0, min(20.0, perf_latency + perf_size))
    performance_score_100 = round((perf_pts / 20.0) * 100)

    # =========================================================================
    # OVERALL SCORE CALCULATION (0 - 100)
    # =========================================================================
    raw_overall = on_page_pts + tech_pts + security_pts + perf_pts
    overall_score = max(0, min(100, round(raw_overall)))

    # Grade Tier
    if overall_score >= 90:
        grade = "A"
        status_label = "Excellent"
    elif overall_score >= 80:
        grade = "B"
        status_label = "Good"
    elif overall_score >= 65:
        grade = "C"
        status_label = "Fair"
    elif overall_score >= 50:
        grade = "D"
        status_label = "Needs Work"
    else:
        grade = "F"
        status_label = "Critical Needs Improvement"

    audit_coverage = round((num_fetched / total_pages) * 100, 1) if total_pages > 0 else 100.0
    is_provisional = audit_coverage < 50.0

    return {
        "overall_score": overall_score,
        "grade": grade,
        "status_label": status_label,
        "total_issues": len(issues),
        "severity_counts": severity_counts,
        "section_scores": {
            "on_page": on_page_score_100,
            "technical": technical_score_100,
            "security": security_score_100,
            "performance": performance_score_100
        },
        "audit_coverage": audit_coverage,
        "is_provisional": is_provisional,
        "scoring_methodology": "Documented 4-category weighted model: On-Page (35%), Technical (30%), Security (15%), Performance (20%)"
    }
