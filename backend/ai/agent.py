import json
import logging
from typing import List, Dict, Any
from urllib.parse import urlparse
from .providers.llm_provider import LLMProvider
from .prompts import SYSTEM_SEO_EXPERT_PROMPT, build_recommendations_prompt

logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.provider = LLMProvider()

    async def generate_seo_recommendations(
        self,
        target_url: str,
        score_data: Dict[str, Any],
        issues: List[Dict[str, Any]],
        pages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        
        prompt = build_recommendations_prompt(target_url, score_data, issues, pages)
        response_raw = await self.provider.generate_completion(prompt, SYSTEM_SEO_EXPERT_PROMPT)

        try:
            # Parse JSON response from LLM if valid
            cleaned_json = response_raw.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]
            cleaned_json = cleaned_json.strip()

            parsed = json.loads(cleaned_json)
            recommendations = parsed.get("top_recommendations", [])
            if recommendations:
                return recommendations
        except Exception as e:
            logger.warning(f"Could not parse LLM JSON output, constructing fallback recommendations: {e}")

        # Construct high-quality rule-based recommendations if LLM JSON parsing fails or mock response
        domain = urlparse(target_url).netloc or target_url
        domain_name = domain.replace("www.", "").split(".")[0].capitalize()

        recs = []

        # High priority recommendations derived from factual audit findings
        critical_high_issues = [i for i in issues if i.get("severity") in ("CRITICAL", "HIGH")]

        if any(i.get("issue_code") == "NO_HTTPS" for i in issues):
            recs.append({
                "category": "security",
                "priority": "CRITICAL",
                "title": "Migrate Website from HTTP to HTTPS",
                "explanation": "Google treats HTTPS as a core security signal. Pages served over HTTP suffer ranking penalties and display 'Not Secure' warnings to visitors.",
                "actionable_steps": [
                    "Obtain a valid SSL/TLS certificate from Let's Encrypt or your hosting provider.",
                    "Configure 301 redirects from HTTP to HTTPS across all web server rules.",
                    "Update internal link paths and canonical tags to point to https:// protocol URLs."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{domain_name} | Official Secure Site",
                    "suggested_meta_description": f"Welcome to {domain_name}. Discover our services securely online with encrypted HTTPS connection.",
                    "suggested_h1": f"Welcome to {domain_name}",
                    "primary_keyword": f"{domain_name} official"
                }
            })

        if any("TITLE" in i.get("issue_code", "") for i in issues):
            recs.append({
                "category": "on_page",
                "priority": "HIGH",
                "title": "Optimize Missing and Duplicate Page Titles",
                "explanation": "Title tags are the single most important on-page SEO element. Missing or duplicate titles prevent search engines from ranking target pages effectively.",
                "actionable_steps": [
                    "Audit all pages missing titles and write unique, descriptive titles between 50-60 characters.",
                    "Ensure primary target keyword is placed near the beginning of each title tag.",
                    "Append brand name at the end separated by a pipe (|) or dash (-)."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{domain_name} - Premier Solutions & Services",
                    "suggested_meta_description": f"Explore {domain_name} for leading solutions. Get expert insights, high-quality services, and industry guidance.",
                    "suggested_h1": f"Transform Your Growth with {domain_name}",
                    "primary_keyword": f"{domain_name} services"
                }
            })

        if any("META" in i.get("issue_code", "") for i in issues):
            recs.append({
                "category": "on_page",
                "priority": "HIGH",
                "title": "Craft Compelling Meta Descriptions for Search Snippets",
                "explanation": "Meta descriptions provide the summary text in search engine results. Crafting compelling descriptions directly boosts user Click-Through Rates (CTR).",
                "actionable_steps": [
                    "Write unique meta descriptions (130-155 characters) for all audited pages.",
                    "Include a clear value proposition and call-to-action (e.g. 'Learn more', 'Get started today').",
                    "Incorporate secondary target keywords naturally."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{domain_name} | Expert Guidance & Features",
                    "suggested_meta_description": f"Discover top features and solutions on {domain_name}. Fast, secure, and user-friendly experience built for your needs.",
                    "suggested_h1": f"Everything You Need to Know About {domain_name}",
                    "primary_keyword": f"{domain_name} features"
                }
            })

        if any("H1" in i.get("issue_code", "") for i in issues):
            recs.append({
                "category": "on_page",
                "priority": "HIGH",
                "title": "Establish Structured Heading Hierarchy (H1 & H2)",
                "explanation": "Heading tags define the semantic structure of your content for screen readers and search engines.",
                "actionable_steps": [
                    "Ensure exactly one <h1> heading is present per page matching the page's core topic.",
                    "Use <h2> subheadings to logically structure secondary content sections.",
                    "Avoid using heading tags solely for font styling."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"Complete Guide to {domain_name}",
                    "suggested_meta_description": f"Learn how {domain_name} delivers industry-leading performance and features in our comprehensive guide.",
                    "suggested_h1": f"Empower Your Digital Presence with {domain_name}",
                    "primary_keyword": f"{domain_name} guide"
                }
            })

        if any("ALT" in i.get("issue_code", "") for i in issues):
            recs.append({
                "category": "on_page",
                "priority": "MEDIUM",
                "title": "Add Descriptive Alt Text to All Product & Article Images",
                "explanation": "Image alt text allows search engines to index images in Google Images search and provides accessibility for screen readers.",
                "actionable_steps": [
                    "Review all images flagged without alt attributes.",
                    "Add concise, descriptive alt text explaining image context in 3-8 words.",
                    "Avoid keyword stuffing in alt attributes."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"Visual Highlights | {domain_name}",
                    "suggested_meta_description": f"Browse key visuals, illustrations, and feature walkthroughs from {domain_name}.",
                    "suggested_h1": f"Visual Overview of {domain_name}",
                    "primary_keyword": f"{domain_name} visuals"
                }
            })

        if any(i.get("issue_code") in ("MISSING_SITEMAP", "MISSING_CANONICAL") for i in issues):
            recs.append({
                "category": "technical",
                "priority": "MEDIUM",
                "title": "Deploy XML Sitemap & Standardize Canonical URLs",
                "explanation": "Technical indexing directives ensure search engine web crawlers navigate and index your site without duplicate content penalties.",
                "actionable_steps": [
                    "Generate an automated XML sitemap at /sitemap.xml.",
                    "Add `<link rel='canonical' href='...' />` tags to every page header.",
                    "Submit sitemap.xml to Google Search Console and Bing Webmaster Tools."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"Site Directory & Resource Hub | {domain_name}",
                    "suggested_meta_description": f"Access all pages, official documentation, and updates from {domain_name}.",
                    "suggested_h1": f"Official Resource Directory for {domain_name}",
                    "primary_keyword": f"{domain_name} index"
                }
            })

        # General baseline recommendation if site is clean
        if not recs:
            recs.append({
                "category": "on_page",
                "priority": "LOW",
                "title": "Expand Content Coverage & Internal Link Building",
                "explanation": "Your technical baseline is solid. Focus on expanding thematic authority through topic clusters.",
                "actionable_steps": [
                    "Publish long-form guides covering long-tail keywords in your niche.",
                    "Build internal contextual links from high-performing pages to new articles.",
                    "Monitor Google Search Console for impressions and emerging query trends."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"Ultimate Resource Hub | {domain_name}",
                    "suggested_meta_description": f"Stay ahead with the latest industry insights and comprehensive tutorials from {domain_name}.",
                    "suggested_h1": f"Knowledge Base & Insights - {domain_name}",
                    "primary_keyword": f"{domain_name} knowledge base"
                }
            })

        return recs
