from typing import List, Dict, Any

SEVERITY_WEIGHTS = {
    "CRITICAL": 15,
    "HIGH": 10,
    "MEDIUM": 5,
    "LOW": 2
}

def calculate_score(issues: List[Dict[str, Any]], pages_crawled: int) -> Dict[str, Any]:
    total_penalty = 0
    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }
    
    category_penalties = {
        "on_page": 0,
        "technical": 0,
        "security": 0,
        "performance": 0
    }

    for issue in issues:
        severity = issue.get("severity", "LOW").upper()
        category = issue.get("category", "on_page").lower()

        penalty = SEVERITY_WEIGHTS.get(severity, 2)
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Unique issues per URL penalty calculation
        total_penalty += penalty

        if category in category_penalties:
            category_penalties[category] += penalty
        else:
            category_penalties["on_page"] += penalty

    # Compute overall score starting from 100
    # Normalize penalty by scaling for site size if pages > 1
    page_scale_factor = 1.0 if pages_crawled <= 1 else max(0.5, 1.0 - (pages_crawled * 0.01))
    scaled_penalty = total_penalty * page_scale_factor
    
    raw_score = max(0, min(100, round(100 - scaled_penalty)))

    # Compute individual section scores out of 100
    on_page_score = max(0, min(100, round(100 - (category_penalties["on_page"] * page_scale_factor * 1.2))))
    technical_score = max(0, min(100, round(100 - (category_penalties["technical"] * page_scale_factor * 1.5))))
    security_score = max(0, min(100, round(100 - (category_penalties["security"] * page_scale_factor * 2.0))))
    performance_score = max(0, min(100, round(100 - (category_penalties["performance"] * page_scale_factor * 1.5))))

    # Rating tier
    if raw_score >= 90:
        grade = "A+"
        status_label = "Excellent"
    elif raw_score >= 75:
        grade = "B"
        status_label = "Good"
    elif raw_score >= 50:
        grade = "C"
        status_label = "Fair"
    else:
        grade = "F"
        status_label = "Needs Urgent Improvement"

    return {
        "overall_score": raw_score,
        "grade": grade,
        "status_label": status_label,
        "total_issues": len(issues),
        "severity_counts": severity_counts,
        "section_scores": {
            "on_page": on_page_score,
            "technical": technical_score,
            "security": security_score,
            "performance": performance_score
        }
    }
