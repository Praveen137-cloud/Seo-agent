SYSTEM_SEO_EXPERT_PROMPT = """You are a Senior Technical SEO Strategist and Growth Engineer. 
Your role is to analyze verified audit findings and actual website content, providing accurate, evidence-based recommendations.
Strict Rules:
1. Ground all explanations and recommendations strictly in the verified audit findings and actual crawled page content provided.
2. NEVER hallucinate or invent missing headings, keywords, backlinks, or metadata that contradict or are absent from the crawl evidence.
3. If no target keyword was specified by the user, do NOT claim the website is missing a specific target keyword.
4. Clearly distinguish confirmed technical errors (e.g. 404s, missing titles, mixed content) from optional optimization opportunities.
5. Ensure recommendations are specific and directly applicable to the actual affected URLs."""

def build_recommendations_prompt(target_url: str, score_data: dict, issues: list, top_pages: list) -> str:
    issues_summary = []
    for iss in issues[:15]:
        obs = iss.get("observed_value") or "Observed in audit"
        ev = iss.get("evidence") or iss.get("description")
        status = iss.get("verification_status") or "verified"
        issues_summary.append(
            f"- [{iss.get('severity')}] ({status}) {iss.get('title')}: {iss.get('description')}\n"
            f"  Observed: {obs}\n"
            f"  Evidence: {ev}\n"
            f"  URL: {iss.get('page_url')}"
        )
    
    issues_text = "\n".join(issues_summary) if issues_summary else "No severe issues detected."

    pages_summary = []
    for p in (top_pages or [])[:5]:
        if p.get("is_fetched", True):
            h1s = ", ".join(p.get("h1_tags", [])) if p.get("h1_tags") else "(none)"
            pages_summary.append(
                f"- Page: {p.get('url')}\n"
                f"  Title: {p.get('title') or '(none)'}\n"
                f"  Meta Description: {p.get('meta_description') or '(none)'}\n"
                f"  H1 Tags: {h1s}\n"
                f"  Word Count: {p.get('word_count', 0)}\n"
                f"  Sample Text: {(p.get('text_sample') or '')[:150]}"
            )
    pages_text = "\n".join(pages_summary) if pages_summary else "No page details available."

    return f"""Website Target URL: {target_url}
Overall SEO Score: {score_data.get('overall_score')}/100 (Grade: {score_data.get('grade')})
Total Issues Detected: {score_data.get('total_issues')}
Section Scores:
- On-Page SEO: {score_data.get('section_scores', {}).get('on_page')}/100
- Technical SEO: {score_data.get('section_scores', {}).get('technical')}/100
- Security: {score_data.get('section_scores', {}).get('security')}/100
- Performance: {score_data.get('section_scores', {}).get('performance')}/100

Actual Crawled Pages Content:
{pages_text}

Verified Audit Findings:
{issues_text}

Instructions:
Generate a structured JSON response grounded strictly in the verified audit findings and actual crawled pages above:
{{
  "executive_summary": "A concise 2-3 sentence strategic summary of the website's SEO health.",
  "top_recommendations": [
    {{
      "category": "on_page | technical | security | performance",
      "priority": "CRITICAL | HIGH | MEDIUM | LOW",
      "title": "Clear action-oriented recommendation title",
      "explanation": "Why this matters and its impact on organic traffic (based on the real findings)",
      "actionable_steps": [
        "Step 1 to resolve",
        "Step 2 to resolve"
      ],
      "suggested_content": {{
        "target_url": "{target_url}",
        "suggested_meta_title": "Optimized meta title candidate (50-60 chars)",
        "suggested_meta_description": "Compelling meta description (130-155 chars)",
        "suggested_h1": "Target H1 heading",
        "primary_keyword": "Primary topical theme based on actual page content"
      }}
    }}
  ]
}}

Return ONLY valid JSON.
"""
