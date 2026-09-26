SYSTEM_SEO_EXPERT_PROMPT = """You are a Senior Technical SEO Strategist and Growth Engineer. 
Your goal is to evaluate structured website crawl data, explain complex technical and on-page SEO issues in simple terms, 
and generate prioritized, actionable step-by-step recommendations and ready-to-use SEO content suggestions."""

def build_recommendations_prompt(target_url: str, score_data: dict, issues: list, top_pages: list) -> str:
    issues_summary = []
    for iss in issues[:15]:
        issues_summary.append(f"- [{iss.get('severity')}] {iss.get('title')}: {iss.get('description')} (URL: {iss.get('page_url')})")
    
    issues_text = "\n".join(issues_summary) if issues_summary else "No severe issues detected."

    return f"""Website Target URL: {target_url}
Overall SEO Score: {score_data.get('overall_score')}/100 (Grade: {score_data.get('grade')})
Total Issues Detected: {score_data.get('total_issues')}
Section Scores:
- On-Page SEO: {score_data.get('section_scores', {}).get('on_page')}/100
- Technical SEO: {score_data.get('section_scores', {}).get('technical')}/100
- Security: {score_data.get('section_scores', {}).get('security')}/100
- Performance: {score_data.get('section_scores', {}).get('performance')}/100

Top Audit Findings:
{issues_text}

Instructions:
Generate a structured JSON response with the following keys:
{{
  "executive_summary": "A concise 2-3 sentence strategic summary of the website's SEO health.",
  "top_recommendations": [
    {{
      "category": "on_page | technical | security | performance",
      "priority": "CRITICAL | HIGH | MEDIUM | LOW",
      "title": "Clear action-oriented recommendation title",
      "explanation": "Why this matters and its impact on organic traffic",
      "actionable_steps": [
        "Step 1 to resolve",
        "Step 2 to resolve"
      ],
      "suggested_content": {{
        "target_url": "{target_url}",
        "suggested_meta_title": "Optimized meta title candidate (50-60 chars)",
        "suggested_meta_description": "Compelling meta description with target keywords (130-150 chars)",
        "suggested_h1": "Target H1 heading",
        "primary_keyword": "Primary focus keyword"
      }}
    }}
  ]
}}

Return ONLY valid JSON.
"""
