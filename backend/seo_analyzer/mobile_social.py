from typing import List, Dict, Any

def analyze_mobile_social(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []

    for page in pages:
        url = page["url"]
        viewport = page.get("viewport", "")
        og_tags = page.get("og_tags", {}) or {}
        has_favicon = page.get("has_favicon", False)

        # 1. Viewport / Mobile Responsiveness
        if not viewport:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "CRITICAL",
                "issue_code": "MISSING_VIEWPORT",
                "title": "Missing Mobile Viewport Meta Tag",
                "description": f"The page {url} does not have a `<meta name='viewport'>` tag, which breaks mobile responsiveness on smartphones and tablets.",
                "recommendation_summary": "Add `<meta name='viewport' content='width=device-width, initial-scale=1.0'>` to the `<head>`.",
                "impact": "Google prioritizes mobile-first indexing; pages without a responsive viewport suffer severe mobile ranking penalties."
            })
        elif "width=device-width" not in viewport:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "MEDIUM",
                "issue_code": "INVALID_VIEWPORT",
                "title": "Suboptimal Viewport Configuration",
                "description": f"Viewport tag is set to '{viewport}' instead of the recommended 'width=device-width, initial-scale=1.0'.",
                "recommendation_summary": "Configure viewport to 'width=device-width, initial-scale=1.0' for standard mobile rendering.",
                "impact": "Incomplete viewport settings can cause unexpected horizontal scrolling and zoom glitches on mobile devices."
            })

        # 2. Social Media & Open Graph Tags
        missing_social = []
        if not og_tags.get("og_title"):
            missing_social.append("og:title")
        if not og_tags.get("og_image"):
            missing_social.append("og:image")
        if not og_tags.get("og_desc"):
            missing_social.append("og:description")

        if len(missing_social) >= 2:
            issues.append({
                "page_url": url,
                "category": "on_page",
                "severity": "LOW",
                "issue_code": "MISSING_OPEN_GRAPH",
                "title": "Missing Open Graph Social Metadata",
                "description": f"The page lacks essential Open Graph social sharing tags: {', '.join(missing_social)}.",
                "recommendation_summary": "Add Open Graph meta tags (og:title, og:description, og:image) so links share with rich previews on LinkedIn, Twitter, and WhatsApp.",
                "impact": "Social media shares will display plain generic text links instead of engaging visual cards, lowering viral traffic."
            })

        # 3. Favicon
        if not has_favicon and page.get("depth", 0) == 0:
            issues.append({
                "page_url": url,
                "category": "technical",
                "severity": "LOW",
                "issue_code": "MISSING_FAVICON",
                "title": "Missing Site Favicon Icon",
                "description": f"No `<link rel='icon'>` favicon tag found on the homepage.",
                "recommendation_summary": "Add a modern SVG or 32x32 PNG favicon to enhance brand recognition in browser tabs and Google mobile search results.",
                "impact": "Google mobile search displays favicons next to domain names; missing favicons look unprofessional and decrease CTR."
            })

    return issues
