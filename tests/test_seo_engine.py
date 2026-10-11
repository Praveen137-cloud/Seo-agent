import unittest
from backend.seo_analyzer.title import analyze_titles
from backend.seo_analyzer.meta import analyze_meta_descriptions
from backend.seo_analyzer.headings import analyze_headings
from backend.seo_analyzer.images import analyze_images
from backend.seo_analyzer.links import analyze_links
from backend.seo_analyzer.indexing import analyze_indexing
from backend.seo_analyzer.content import analyze_content
from backend.technical.canonical import analyze_canonicals
from backend.technical.security import analyze_security
from backend.scoring.scorer import calculate_score
from backend.crawler.crawler import is_valid_public_url

class TestSEOEngine(unittest.TestCase):

    def test_url_validation_blocks_private_and_local(self):
        self.assertTrue(is_valid_public_url("https://example.com"))
        self.assertFalse(is_valid_public_url("http://127.0.0.1"))
        self.assertFalse(is_valid_public_url("http://localhost:8000"))
        self.assertFalse(is_valid_public_url("ftp://example.com"))
        self.assertFalse(is_valid_public_url("javascript:alert(1)"))

    def test_page_with_valid_title(self):
        pages = [{
            "url": "https://example.com/",
            "title": "Comprehensive Real-Time SEO Analyzer Platform",
            "is_fetched": True
        }]
        issues = analyze_titles(pages)
        issue_codes = [i["issue_code"] for i in issues]
        self.assertNotIn("MISSING_TITLE", issue_codes)
        self.assertNotIn("TITLE_TOO_SHORT", issue_codes)
        self.assertNotIn("TITLE_TOO_LONG", issue_codes)

    def test_page_with_missing_title(self):
        pages = [{
            "url": "https://example.com/no-title",
            "title": "",
            "is_fetched": True
        }]
        issues = analyze_titles(pages)
        issue_codes = [i["issue_code"] for i in issues]
        self.assertIn("MISSING_TITLE", issue_codes)
        missing_issue = next(i for i in issues if i["issue_code"] == "MISSING_TITLE")
        self.assertEqual(missing_issue["verification_status"], "verified")
        self.assertTrue(bool(missing_issue.get("evidence")))

    def test_page_with_valid_meta_description(self):
        pages = [{
            "url": "https://example.com/",
            "meta_description": "Analyze and optimize your website rankings in real-time with comprehensive SEO audits and actionable AI growth recommendations.",
            "is_fetched": True
        }]
        issues = analyze_meta_descriptions(pages)
        issue_codes = [i["issue_code"] for i in issues]
        self.assertNotIn("MISSING_META_DESCRIPTION", issue_codes)
        self.assertNotIn("META_DESCRIPTION_TOO_SHORT", issue_codes)

    def test_page_with_missing_meta_description(self):
        pages = [{
            "url": "https://example.com/missing-meta",
            "meta_description": "",
            "is_fetched": True
        }]
        issues = analyze_meta_descriptions(pages)
        issue_codes = [i["issue_code"] for i in issues]
        self.assertIn("MISSING_META_DESCRIPTION", issue_codes)
        meta_issue = next(i for i in issues if i["issue_code"] == "MISSING_META_DESCRIPTION")
        self.assertEqual(meta_issue["verification_status"], "verified")

    def test_page_with_images_missing_alt(self):
        pages = [{
            "url": "https://example.com/gallery",
            "is_fetched": True,
            "images": [
                {"src": "https://example.com/img1.png", "has_alt": True, "alt": "Logo"},
                {"src": "https://example.com/img2.png", "has_alt": False, "alt": ""},
                {"src": "https://example.com/img3.png", "has_alt": False, "alt": ""},
            ]
        }]
        issues = analyze_images(pages)
        issue_codes = [i["issue_code"] for i in issues]
        self.assertIn("IMAGES_MISSING_ALT", issue_codes)
        alt_issue = next(i for i in issues if i["issue_code"] == "IMAGES_MISSING_ALT")
        self.assertTrue("2" in str(alt_issue.get("observed_value")) or "2 out of 3" in alt_issue["description"])
        self.assertEqual(alt_issue["verification_status"], "verified")

    def test_verified_broken_links_and_timeouts(self):
        pages = [{"url": "https://example.com/", "is_fetched": True, "links": []}]
        tested_links = {
            "https://example.com/broken-page": {
                "source_url": "https://example.com/",
                "status_code": 404,
                "is_broken": True,
                "verified": True
            },
            "https://example.com/slow-page": {
                "source_url": "https://example.com/",
                "status_code": 0,
                "is_broken": False,
                "verified": False
            }
        }
        issues = analyze_links(pages, tested_links)
        codes = [i["issue_code"] for i in issues]
        self.assertIn("VERIFIED_BROKEN_LINK", codes)
        self.assertIn("UNVERIFIED_LINK_TIMEOUT", codes)

        broken_iss = next(i for i in issues if i["issue_code"] == "VERIFIED_BROKEN_LINK")
        self.assertEqual(broken_iss["verification_status"], "verified")
        self.assertEqual(broken_iss["severity"], "HIGH")

        timeout_iss = next(i for i in issues if i["issue_code"] == "UNVERIFIED_LINK_TIMEOUT")
        self.assertEqual(timeout_iss["verification_status"], "unverified")
        self.assertEqual(timeout_iss["severity"], "LOW")

    def test_noindex_directives(self):
        pages = [{
            "url": "https://example.com/secret",
            "is_fetched": True,
            "status_code": 200,
            "robots_meta": "noindex, nofollow"
        }]
        issues = analyze_indexing(pages)
        codes = [i["issue_code"] for i in issues]
        self.assertIn("PAGE_BLOCKED_BY_NOINDEX", codes)
        noindex_iss = next(i for i in issues if i["issue_code"] == "PAGE_BLOCKED_BY_NOINDEX")
        self.assertEqual(noindex_iss["severity"], "CRITICAL")

    def test_javascript_rendered_spa_does_not_falsely_flag_thin_content(self):
        pages = [{
            "url": "https://example.com/app",
            "is_fetched": True,
            "word_count": 25,
            "is_spa": True
        }]
        issues = analyze_content(pages)
        codes = [i["issue_code"] for i in issues]
        self.assertNotIn("THIN_CONTENT", codes)

    def test_unsuccessful_fetch_does_not_generate_false_missing_metadata(self):
        failed_page = [{
            "url": "https://example.com/unreachable",
            "is_fetched": False,
            "fetch_error": "Connection timed out",
            "title": "",
            "meta_description": "",
            "h1_tags": [],
            "images": []
        }]
        self.assertEqual(len(analyze_titles(failed_page)), 0)
        self.assertEqual(len(analyze_meta_descriptions(failed_page)), 0)
        self.assertEqual(len(analyze_headings(failed_page)), 0)
        self.assertEqual(len(analyze_images(failed_page)), 0)

    def test_perfect_page_scores_high_grade_a(self):
        perfect_pages = [{
            "url": "https://example.com/",
            "is_fetched": True,
            "status_code": 200,
            "load_time_ms": 250,
            "html_size": 45000,
            "title": "Example Domain - Official High Performance Web Portal",
            "meta_description": "Welcome to the official Example domain providing industry standard web architecture, technical documentation, and best practices.",
            "h1_tags": ["Official Example Domain"],
            "h2_tags": ["Architecture", "Documentation"],
            "word_count": 450,
            "viewport": "width=device-width, initial-scale=1.0",
            "canonical_url": "https://example.com/",
            "images": [{"src": "https://example.com/logo.png", "has_alt": True, "alt": "Logo"}],
            "links": [{"url": "https://example.com/docs", "anchor_text": "Read Documentation"}],
            "discovered_links": [],
            "has_schema": True,
            "robots_meta": ""
        }]
        score_res = calculate_score([], perfect_pages, "https://example.com/")
        self.assertGreaterEqual(score_res["overall_score"], 90)
        self.assertEqual(score_res["grade"], "A")
        self.assertEqual(score_res["section_scores"]["on_page"], 100)
        self.assertEqual(score_res["section_scores"]["security"], 100)

    def test_two_different_websites_diverge_accurately(self):
        site_a = [{
            "url": "https://healthy-site.com/",
            "is_fetched": True,
            "status_code": 200,
            "load_time_ms": 300,
            "html_size": 35000,
            "title": "Healthy Site - Technical SEO Platform",
            "meta_description": "Fast and responsive platform designed for technical SEO and content intelligence with verified standards.",
            "h1_tags": ["Main Heading"],
            "word_count": 500,
            "viewport": "width=device-width, initial-scale=1.0",
            "canonical_url": "https://healthy-site.com/",
            "images": [],
            "links": []
        }]

        site_b = [{
            "url": "http://problematic-site.com/",
            "is_fetched": True,
            "status_code": 200,
            "load_time_ms": 3500,
            "html_size": 1500000,
            "title": "",
            "meta_description": "",
            "h1_tags": [],
            "word_count": 12,
            "viewport": "",
            "canonical_url": "",
            "images": [{"src": "http://problematic-site.com/pic.jpg", "has_alt": False, "alt": ""}],
            "links": []
        }]

        issues_a = analyze_titles(site_a) + analyze_meta_descriptions(site_a) + analyze_headings(site_a) + analyze_security("https://healthy-site.com/", site_a)
        score_a = calculate_score(issues_a, site_a, "https://healthy-site.com/")

        issues_b = analyze_titles(site_b) + analyze_meta_descriptions(site_b) + analyze_headings(site_b) + analyze_content(site_b) + analyze_security("http://problematic-site.com/", site_b)
        score_b = calculate_score(issues_b, site_b, "http://problematic-site.com/")

        self.assertGreater(len(issues_b), len(issues_a))
        self.assertGreater(score_a["overall_score"], score_b["overall_score"])
        self.assertIn(score_b["grade"], ("D", "F"))
        self.assertIn(score_a["grade"], ("A", "B"))

if __name__ == "__main__":
    unittest.main()
