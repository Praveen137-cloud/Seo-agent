import time
import logging
import ipaddress
import socket
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from .url_queue import URLQueue
from .robots import RobotsChecker

logger = logging.getLogger(__name__)

def is_valid_public_url(url: str) -> bool:
    """
    Validates that the submitted URL uses http/https and does not resolve to
    localhost or a private RFC1918 / loopback / link-local IP address.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return False
        # Try to resolve hostname to check if private
        try:
            ip_str = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False
        except Exception:
            # If DNS resolution fails, allow requests to handle and report genuine network failure
            pass
        return True
    except Exception:
        return False

class WebCrawler:
    def __init__(self, target_url: str, max_pages: int = 50, max_depth: int = 3, timeout: int = 10):
        self.target_url = target_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Connection": "keep-alive"
        }
        self.queue = URLQueue(target_url, max_depth=max_depth)
        self.robots = RobotsChecker(target_url)
        self.tested_links: Dict[str, Dict[str, Any]] = {}

    def crawl(self, progress_callback=None) -> List[Dict[str, Any]]:
        crawled_pages = []
        crawled_count = 0

        while not self.queue.is_empty() and crawled_count < self.max_pages:
            url, depth = self.queue.pop()
            if not url:
                break

            if not self.robots.is_allowed(url):
                logger.info(f"Skipping {url}: Disallowed by robots.txt")
                continue

            page_data = self._fetch_and_parse(url, depth)
            if page_data:
                crawled_pages.append(page_data)
                crawled_count += 1
                
                # Discover internal links to queue
                for link in page_data.get("discovered_links", []):
                    self.queue.add(link, depth + 1)

                if progress_callback:
                    progress_callback(crawled_count, self.max_pages, url)

            time.sleep(0.05)  # Polite crawling interval

        # Sample and verify discovered internal links for genuine 404 detection
        self._verify_sample_links(crawled_pages)

        return crawled_pages

    def _fetch_and_parse(self, url: str, depth: int) -> Dict[str, Any]:
        start_time = time.time()
        try:
            resp = self.session.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            load_time_ms = round((time.time() - start_time) * 1000, 2)
            status_code = resp.status_code
            content_type = resp.headers.get("Content-Type", "")
            final_url = resp.url
            redirect_count = len(resp.history)
            redirect_chain = [r.url for r in resp.history]

            # If Cloudflare or WAF challenges the crawler with 403 or managed challenge page
            is_waf_challenge = (
                status_code in (403, 503, 429) or
                "challenge" in str(resp.headers.get("Cf-Mitigated", "")).lower() or
                "<title>Just a moment...</title>" in resp.text
            )
            if is_waf_challenge:
                logger.info(f"Cloudflare/WAF challenge detected for {url} (HTTP {status_code}). Attempting fallback extraction...")
                try:
                    fallback_resp = requests.get(
                        f"https://r.jina.ai/{url}",
                        headers={"X-Return-Format": "html"},
                        timeout=15
                    )
                    if fallback_resp.status_code == 200 and len(fallback_resp.text) > 200 and "<title>Just a moment...</title>" not in fallback_resp.text:
                        resp = fallback_resp
                        status_code = 200
                        content_type = "text/html"
                        load_time_ms = round((time.time() - start_time) * 1000, 2)
                except Exception as ex:
                    logger.warning(f"Fallback extraction failed for {url}: {ex}")

            # If page returned 4xx or 5xx, accurately record it without fabricating missing metadata
            if status_code >= 400:
                return {
                    "url": url,
                    "final_url": final_url,
                    "depth": depth,
                    "status_code": status_code,
                    "load_time_ms": load_time_ms,
                    "html_size": len(resp.content),
                    "is_fetched": False,
                    "fetch_error": f"HTTP {status_code}",
                    "redirect_count": redirect_count,
                    "redirect_chain": redirect_chain,
                    "title": "",
                    "meta_description": "",
                    "h1_tags": [],
                    "h2_tags": [],
                    "h3_tags": [],
                    "images": [],
                    "links": [],
                    "discovered_links": [],
                    "canonical_url": "",
                    "word_count": 0,
                    "viewport": "",
                    "robots_meta": "",
                    "has_schema": False,
                    "schema_count": 0,
                    "og_tags": {},
                    "html_lang": "",
                    "has_charset": True,
                    "has_favicon": False,
                    "text_sample": ""
                }

            if "text/html" not in content_type:
                return {
                    "url": url,
                    "final_url": final_url,
                    "depth": depth,
                    "status_code": status_code,
                    "load_time_ms": load_time_ms,
                    "html_size": len(resp.content),
                    "is_fetched": True,
                    "fetch_error": None,
                    "redirect_count": redirect_count,
                    "redirect_chain": redirect_chain,
                    "title": "",
                    "meta_description": "",
                    "h1_tags": [],
                    "h2_tags": [],
                    "h3_tags": [],
                    "images": [],
                    "links": [],
                    "discovered_links": [],
                    "canonical_url": "",
                    "word_count": 0,
                    "viewport": "",
                    "robots_meta": "",
                    "has_schema": False,
                    "schema_count": 0,
                    "og_tags": {},
                    "html_lang": "",
                    "has_charset": True,
                    "has_favicon": False,
                    "text_sample": ""
                }

            soup = BeautifulSoup(resp.text, "lxml")
            
            # Title
            title_tag = soup.find("title")
            title = title_tag.string.strip() if title_tag and title_tag.string else ""

            # Meta Description
            meta_desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""

            # Headings
            h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all("h1") if h1.get_text(strip=True)]
            h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all("h2") if h2.get_text(strip=True)]
            h3_tags = [h3.get_text(strip=True) for h3 in soup.find_all("h3") if h3.get_text(strip=True)]

            # Images
            images = []
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src") or ""
                alt = img.get("alt", None)
                if src:
                    images.append({
                        "src": urljoin(url, src),
                        "alt": alt,
                        "has_alt": bool(alt is not None and alt.strip())
                    })

            # Links
            discovered_links = []
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                full_url = urljoin(url, href)
                is_internal = self.queue.is_same_domain(full_url)
                rel = a.get("rel", [])
                rel_str = " ".join(rel) if isinstance(rel, list) else str(rel)
                
                link_obj = {
                    "url": full_url,
                    "anchor_text": a.get_text(strip=True),
                    "is_internal": is_internal,
                    "is_nofollow": "nofollow" in rel_str.lower()
                }
                links.append(link_obj)
                if is_internal:
                    discovered_links.append(full_url)

            # Viewport
            viewport_tag = soup.find("meta", attrs={"name": "viewport"})
            viewport = viewport_tag.get("content", "").strip() if viewport_tag else ""

            # Robots meta
            robots_tag = soup.find("meta", attrs={"name": "robots"})
            robots_meta = robots_tag.get("content", "").strip().lower() if robots_tag else ""
            if not robots_meta:
                robots_meta = resp.headers.get("X-Robots-Tag", "").strip().lower()

            # Canonical
            canonical_tag = soup.find("link", attrs={"rel": "canonical"})
            canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else ""
            if canonical_url:
                canonical_url = urljoin(url, canonical_url)

            # Structured Data (Schema JSON-LD)
            schema_tags = soup.find_all("script", attrs={"type": "application/ld+json"})
            has_schema = len(schema_tags) > 0

            # Open Graph & Twitter Social Tags
            og_title = (soup.find("meta", property="og:title") or {}).get("content", "").strip()
            og_desc = (soup.find("meta", property="og:description") or {}).get("content", "").strip()
            og_image = (soup.find("meta", property="og:image") or {}).get("content", "").strip()
            twitter_card = (soup.find("meta", attrs={"name": "twitter:card"}) or {}).get("content", "").strip()

            # HTML Lang & Charset
            html_tag = soup.find("html")
            html_lang = html_tag.get("lang", "").strip() if html_tag else ""
            charset_tag = soup.find("meta", charset=True) or soup.find("meta", attrs={"http-equiv": "content-type"})
            has_charset = bool(charset_tag)

            # Favicon
            favicon_tag = soup.find("link", rel=lambda r: r and any("icon" in str(x).lower() for x in (r if isinstance(r, list) else [r])))
            has_favicon = bool(favicon_tag)

            # Check if JavaScript-rendered Single Page App
            root_div = soup.find(id=["root", "__next", "app"])
            is_spa = bool(root_div and len(soup.find_all("script")) > 3)

            # Text content & word count
            soup_clean = BeautifulSoup(resp.text, "lxml")
            for element in soup_clean(["script", "style", "nav", "footer", "noscript"]):
                element.decompose()
            body_text = soup_clean.get_text(separator=" ", strip=True)
            word_count = len(body_text.split())
            text_sample = body_text[:400] if body_text else ""

            return {
                "url": url,
                "final_url": final_url,
                "depth": depth,
                "status_code": status_code,
                "load_time_ms": load_time_ms,
                "html_size": len(resp.content),
                "is_fetched": True,
                "fetch_error": None,
                "is_spa": is_spa,
                "redirect_count": redirect_count,
                "redirect_chain": redirect_chain,
                "title": title,
                "meta_description": meta_description,
                "h1_tags": h1_tags,
                "h2_tags": h2_tags,
                "h3_tags": h3_tags,
                "images": images,
                "links": links,
                "discovered_links": discovered_links,
                "canonical_url": canonical_url,
                "word_count": word_count,
                "viewport": viewport,
                "robots_meta": robots_meta,
                "has_schema": has_schema,
                "schema_count": len(schema_tags),
                "og_tags": {
                    "og_title": og_title,
                    "og_desc": og_desc,
                    "og_image": og_image,
                    "twitter_card": twitter_card
                },
                "html_lang": html_lang,
                "has_charset": has_charset,
                "has_favicon": has_favicon,
                "text_sample": text_sample
            }
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout crawling {url}")
            return {
                "url": url,
                "final_url": url,
                "depth": depth,
                "status_code": 0,
                "load_time_ms": self.timeout * 1000,
                "html_size": 0,
                "is_fetched": False,
                "fetch_error": "Connection timed out",
                "redirect_count": 0,
                "redirect_chain": [],
                "title": "",
                "meta_description": "",
                "h1_tags": [],
                "h2_tags": [],
                "h3_tags": [],
                "images": [],
                "links": [],
                "discovered_links": [],
                "canonical_url": "",
                "word_count": 0,
                "viewport": "",
                "robots_meta": "",
                "has_schema": False,
                "schema_count": 0,
                "og_tags": {},
                "html_lang": "",
                "has_charset": True,
                "has_favicon": False,
                "text_sample": ""
            }
        except Exception as e:
            logger.warning(f"Error crawling {url}: {e}")
            return {
                "url": url,
                "final_url": url,
                "depth": depth,
                "status_code": 0,
                "load_time_ms": 0,
                "html_size": 0,
                "is_fetched": False,
                "fetch_error": str(e),
                "redirect_count": 0,
                "redirect_chain": [],
                "title": "",
                "meta_description": "",
                "h1_tags": [],
                "h2_tags": [],
                "h3_tags": [],
                "images": [],
                "links": [],
                "discovered_links": [],
                "canonical_url": "",
                "word_count": 0,
                "viewport": "",
                "robots_meta": "",
                "has_schema": False,
                "schema_count": 0,
                "og_tags": {},
                "html_lang": "",
                "has_charset": True,
                "has_favicon": False,
                "text_sample": ""
            }

    def _verify_sample_links(self, crawled_pages: List[Dict[str, Any]]) -> None:
        """
        Samples up to 10 unique internal links discovered across crawled pages
        and sends lightweight HEAD requests to detect verified broken links.
        """
        crawled_urls = {p["url"] for p in crawled_pages}
        all_internal_links = set()
        link_sources: Dict[str, str] = {}

        for p in crawled_pages:
            for l in p.get("links", []):
                target = l.get("url")
                if target and l.get("is_internal") and target not in crawled_urls:
                    all_internal_links.add(target)
                    if target not in link_sources:
                        link_sources[target] = p["url"]

        # Sample up to 10 un-crawled internal links to test
        sample_to_test = list(all_internal_links)[:10]
        for test_url in sample_to_test:
            try:
                head_resp = self.session.head(test_url, headers=self.headers, timeout=3.0, allow_redirects=True)
                self.tested_links[test_url] = {
                    "source_url": link_sources.get(test_url, self.target_url),
                    "status_code": head_resp.status_code,
                    "is_broken": head_resp.status_code == 404,
                    "verified": True
                }
            except requests.exceptions.Timeout:
                self.tested_links[test_url] = {
                    "source_url": link_sources.get(test_url, self.target_url),
                    "status_code": 0,
                    "is_broken": False,
                    "verified": False,
                    "error": "Timeout"
                }
            except Exception as e:
                self.tested_links[test_url] = {
                    "source_url": link_sources.get(test_url, self.target_url),
                    "status_code": 0,
                    "is_broken": False,
                    "verified": False,
                    "error": str(e)
                }
