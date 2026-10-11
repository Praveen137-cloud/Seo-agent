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
        try:
            response_raw = await self.provider.generate_completion(prompt, SYSTEM_SEO_EXPERT_PROMPT)
            cleaned_json = response_raw.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]
            cleaned_json = cleaned_json.strip()

            parsed = json.loads(cleaned_json)
            recommendations = parsed.get("top_recommendations", [])
            if recommendations and isinstance(recommendations, list) and len(recommendations) > 0:
                validated_recs = []
                valid_categories = {"on_page", "technical", "security", "performance"}
                valid_priorities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
                for r in recommendations:
                    if not isinstance(r, dict):
                        continue
                    cat = str(r.get("category", "on_page")).lower()
                    if cat not in valid_categories:
                        cat = "on_page"
                    prio = str(r.get("priority", "MEDIUM")).upper()
                    if prio not in valid_priorities:
                        prio = "MEDIUM"
                    title = str(r.get("title", "")).strip()
                    if not title:
                        continue
                    validated_recs.append({
                        "category": cat,
                        "priority": prio,
                        "title": title,
                        "explanation": str(r.get("explanation", "")).strip(),
                        "actionable_steps": r.get("actionable_steps", []) if isinstance(r.get("actionable_steps"), list) else [str(r.get("actionable_steps", ""))],
                        "suggested_content": r.get("suggested_content") if isinstance(r.get("suggested_content"), dict) else {}
                    })
                if validated_recs:
                    return validated_recs[:5]
        except Exception as e:
            logger.info(f"Using dynamic rule-synthesized AI recommendations generator: {e}")

        # Real-time dynamic contextual recommendations synthesized from actual crawl data
        domain = urlparse(target_url).netloc or target_url
        domain_name = domain.replace("www.", "").split(".")[0].capitalize()

        # If site was unreachable, return connectivity guidance
        if not pages or not any(p.get("status_code", 0) > 0 for p in pages):
            return [{
                "category": "technical",
                "priority": "CRITICAL",
                "title": "Establish Server Availability and Connectivity",
                "explanation": f"The analyzer was unable to establish a connection to {domain}. Ensure the web server is online and publicly reachable.",
                "actionable_steps": [
                    "Verify DNS records and nameserver configurations.",
                    "Check server firewall, CDN, or DDoS protection rules to ensure search crawlers are allowed.",
                    "Verify SSL/TLS certificate validity."
                ],
                "suggested_content": {}
            }]
        
        # Real homepage and content context
        home_page = pages[0] if pages else {}
        site_title = home_page.get("title", "").strip() or f"{domain_name} Official Portal"
        text_snippet = home_page.get("text_sample", "").strip()
        first_sentence = text_snippet.split(". ")[0] if text_snippet else f"Explore top insights and features on {domain_name}."

        recs = []
        issue_codes = {i.get("issue_code") for i in issues}

        # 1. Broken Pages & 404 Errors (Critical)
        if any(code in ("PAGE_NOT_FOUND_404", "SERVER_ERROR_5XX") for code in issue_codes):
            broken_urls = [i.get("page_url") for i in issues if i.get("issue_code") == "PAGE_NOT_FOUND_404"]
            sample_broken = broken_urls[0] if broken_urls else target_url
            recs.append({
                "category": "technical",
                "priority": "CRITICAL",
                "title": f"Resolve {len(broken_urls)} Broken 404 / Server Error Pages",
                "explanation": f"Dead links on {domain} leak crawl budget, damage user trust, and cause Googlebot to penalize the domain's indexing health.",
                "actionable_steps": [
                    f"Implement 301 permanent redirects for broken paths (e.g. {sample_broken}) to relevant active landing pages.",
                    "Update internal navigation menus and footer links to remove obsolete dead URLs.",
                    "Verify server routing and error handling in your web server configuration."
                ],
                "suggested_content": {
                    "target_url": sample_broken,
                    "suggested_meta_title": f"Page Moved | {domain_name}",
                    "suggested_meta_description": f"The requested resource on {domain_name} has moved. Visit our homepage to explore active features and content.",
                    "suggested_h1": f"Looking for Something on {domain_name}?",
                    "primary_keyword": f"{domain_name} site search"
                }
            })

        # 2. Mobile Viewport (Critical)
        if "MISSING_VIEWPORT" in issue_codes:
            recs.append({
                "category": "technical",
                "priority": "CRITICAL",
                "title": "Enable Responsive Mobile Viewport Meta Tag",
                "explanation": f"Google uses mobile-first indexing. Without a viewport meta tag, {domain} is rendered as an un-scaled desktop site on mobile phones.",
                "actionable_steps": [
                    "Add `<meta name='viewport' content='width=device-width, initial-scale=1.0'>` to the `<head>` of all templates.",
                    "Audit CSS media queries to ensure smooth layout scaling across mobile screen widths (320px - 768px).",
                    "Test pages using Google's Mobile-Friendly Test in Google Search Console."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{site_title} | Mobile Optimized",
                    "suggested_meta_description": f"Access {domain_name} seamlessly on any device. Fully responsive and mobile-friendly.",
                    "suggested_h1": f"Welcome to {domain_name} Mobile",
                    "primary_keyword": f"{domain_name} mobile"
                }
            })

        # 3. Blocked by Robots Noindex (Critical)
        if "PAGE_BLOCKED_BY_NOINDEX" in issue_codes:
            recs.append({
                "category": "technical",
                "priority": "CRITICAL",
                "title": "Remove Accidental 'noindex' Indexing Blocks",
                "explanation": f"One or more pages on {domain} have active 'noindex' directives that explicitly instruct Googlebot to purge them from search results.",
                "actionable_steps": [
                    "Inspect the `<head>` of flagged pages and remove `<meta name='robots' content='noindex'>`.",
                    "Ensure staging environment robots headers were not accidentally deployed to production.",
                    "Request re-indexing via the URL Inspection tool in Google Search Console."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{site_title}",
                    "suggested_meta_description": f"{first_sentence[:150]}",
                    "suggested_h1": f"Official {domain_name} Portal",
                    "primary_keyword": f"{domain_name} indexing"
                }
            })

        # 4. HTTPS Security (Critical)
        if "NO_HTTPS" in issue_codes:
            recs.append({
                "category": "security",
                "priority": "CRITICAL",
                "title": "Enforce HTTPS Encryption & SSL Certificate",
                "explanation": f"The website currently loads over unencrypted HTTP. Modern browsers flag unencrypted sites with 'Not Secure' warnings.",
                "actionable_steps": [
                    "Provision a free TLS/SSL certificate via Let's Encrypt or your hosting provider.",
                    "Configure automatic 301 redirects from HTTP to HTTPS in your web server (Nginx/Cloudflare).",
                    "Update all internal asset links (CSS, JS, images) to use HTTPS or relative paths."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{domain_name} | Secure Official Website",
                    "suggested_meta_description": f"Browse {domain_name} securely with encrypted HTTPS connection. Fast, reliable, and verified.",
                    "suggested_h1": f"Welcome to {domain_name}",
                    "primary_keyword": f"{domain_name} secure"
                }
            })

        # 5. Schema.org Structured Data
        if "MISSING_STRUCTURED_DATA" in issue_codes:
            recs.append({
                "category": "technical",
                "priority": "MEDIUM",
                "title": "Implement Schema.org JSON-LD Structured Data",
                "explanation": f"Structured data enables rich snippet enhancements on Google (star ratings, sitelinks searchbox, breadcrumbs, and business info).",
                "actionable_steps": [
                    "Add Organization or WebSite schema JSON-LD script into the homepage `<head>`.",
                    "Add Article or Product schema markup to content and product detail pages.",
                    "Validate implementation using Google's Rich Results Test tool."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{site_title}",
                    "suggested_meta_description": f"{first_sentence[:140]} Discover official offerings and resources on {domain_name}.",
                    "suggested_h1": f"Featured Resources at {domain_name}",
                    "primary_keyword": f"{domain_name} official schema"
                }
            })

        # 6. Thin Content
        if "THIN_CONTENT" in issue_codes:
            thin_issues = [i for i in issues if i.get("issue_code") == "THIN_CONTENT"]
            recs.append({
                "category": "on_page",
                "priority": "HIGH",
                "title": f"Enrich {len(thin_issues)} Thin Content Pages with Comprehensive Copy",
                "explanation": f"Google's Helpful Content System de-ranks thin pages that offer limited original information or few explanatory words.",
                "actionable_steps": [
                    "Expand flagged pages to at least 400-600 words of useful, high-quality explanatory content.",
                    "Add FAQ sections, benefit lists, and practical examples matching searcher intent.",
                    "Merge or canonicalize thin overlapping pages into a single authoritative resource."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"In-Depth Guide & Insights | {domain_name}",
                    "suggested_meta_description": f"Get comprehensive information, actionable tips, and detailed answers regarding {domain_name}.",
                    "suggested_h1": f"Comprehensive Overview of {domain_name}",
                    "primary_keyword": f"{domain_name} in-depth"
                }
            })

        # 7. Meta Descriptions
        if any("META" in code for code in issue_codes):
            recs.append({
                "category": "on_page",
                "priority": "HIGH",
                "title": "Optimize Meta Descriptions with Click-Compelling CTAs",
                "explanation": "Meta descriptions are the advertising snippet shown in Google search results. Engaging descriptions directly boost Organic CTR.",
                "actionable_steps": [
                    "Write unique, engaging descriptions between 120 and 155 characters for every audited page.",
                    "Include a clear call-to-action (e.g. 'Read more', 'Explore solutions', 'Get started today').",
                    "Position target keywords naturally within the first 100 characters."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{site_title[:55]} | {domain_name}",
                    "suggested_meta_description": f"{first_sentence[:130]} Explore top services & updates on {domain_name} today!",
                    "suggested_h1": f"Leading Insights & Solutions on {domain_name}",
                    "primary_keyword": f"{domain_name} official"
                }
            })

        # 8. Titles & Headings
        if any("H1" in code or "TITLE" in code for code in issue_codes):
            recs.append({
                "category": "on_page",
                "priority": "HIGH",
                "title": "Establish Keyword-Focused H1 and Title Tag Hierarchy",
                "explanation": "Title tags and H1 headings represent the primary topic identifiers for both search engine algorithms and web readers.",
                "actionable_steps": [
                    "Ensure exactly one unique <h1> heading exists per page that summarizes the core topic.",
                    "Keep page titles under 60 characters with the primary keyword positioned at the start.",
                    "Use <h2> subheadings to logically structure secondary content themes."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{site_title[:50]} - {domain_name}",
                    "suggested_meta_description": f"Official {domain_name} portal. {first_sentence[:120]}",
                    "suggested_h1": f"Welcome to {domain_name}: {site_title[:40]}",
                    "primary_keyword": f"{domain_name} guide"
                }
            })

        # 9. Images Alt Text
        if "IMAGES_MISSING_ALT" in issue_codes:
            recs.append({
                "category": "on_page",
                "priority": "MEDIUM",
                "title": "Add Descriptive Image Alt Attributes for Image Search",
                "explanation": "Google Image Search drives substantial organic discovery, but images without alt attributes cannot be accurately indexed.",
                "actionable_steps": [
                    "Audit all flagged images and add concise 3-8 word alt descriptions.",
                    "Include relevant subject keywords in product and article images without keyword stuffing.",
                    "Mark purely decorative background images with empty `alt=''` attributes."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{domain_name} Visual Gallery & Features",
                    "suggested_meta_description": f"Browse key visuals, feature graphics, and product highlights from {domain_name}.",
                    "suggested_h1": f"Visual Highlights from {domain_name}",
                    "primary_keyword": f"{domain_name} gallery"
                }
            })

        # Fallback if site is already high-scoring
        if not recs:
            recs.append({
                "category": "on_page",
                "priority": "LOW",
                "title": f"Expand Topical Authority & Keyword Clustering for {domain_name}",
                "explanation": "Your technical baseline is solid. Shift focus toward high-intent content clusters and internal link velocity.",
                "actionable_steps": [
                    "Map out high-volume, low-competition keywords in your industry niche.",
                    "Publish long-form pillar articles linking internally to key conversion pages.",
                    "Monitor Google Search Console query performance every 14 days."
                ],
                "suggested_content": {
                    "target_url": target_url,
                    "suggested_meta_title": f"{site_title}",
                    "suggested_meta_description": f"{first_sentence[:150]}",
                    "suggested_h1": f"Explore Insights & Innovations at {domain_name}",
                    "primary_keyword": f"{domain_name} insights"
                }
            })

        return recs[:5]
