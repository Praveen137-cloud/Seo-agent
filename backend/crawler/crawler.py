import time
import logging
from typing import List, Dict, Any
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from .url_queue import URLQueue
from .robots import RobotsChecker

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, target_url: str, max_pages: int = 50, max_depth: int = 3, timeout: int = 10):
        self.target_url = target_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SEOAgentBot/1.0 (SEO Audit Tool)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        self.queue = URLQueue(target_url, max_depth=max_depth)
        self.robots = RobotsChecker(target_url)

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
                
                # Discover new links
                for link in page_data.get("discovered_links", []):
                    self.queue.add(link, depth + 1)

                if progress_callback:
                    progress_callback(crawled_count, self.max_pages, url)

            time.sleep(0.1)  # Polite crawling delay

        return crawled_pages

    def _fetch_and_parse(self, url: str, depth: int) -> Dict[str, Any]:
        start_time = time.time()
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            load_time_ms = round((time.time() - start_time) * 1000, 2)
            status_code = resp.status_code
            content_type = resp.headers.get("Content-Type", "")

            if "text/html" not in content_type:
                return {
                    "url": url,
                    "depth": depth,
                    "status_code": status_code,
                    "load_time_ms": load_time_ms,
                    "html_size": len(resp.content),
                    "title": "",
                    "meta_description": "",
                    "h1_tags": [],
                    "h2_tags": [],
                    "images": [],
                    "links": [],
                    "discovered_links": [],
                    "canonical_url": "",
                    "word_count": 0,
                    "raw_soup": None
                }

            soup = BeautifulSoup(resp.text, "lxml")
            
            # Extract basic SEO elements
            title_tag = soup.find("title")
            title = title_tag.string.strip() if title_tag and title_tag.string else ""

            meta_desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""

            h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all("h1")]
            h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all("h2")]

            # Images
            images = []
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src") or ""
                alt = img.get("alt", "")
                images.append({
                    "src": urljoin(url, src),
                    "alt": alt,
                    "has_alt": bool(alt and alt.strip())
                })

            # Links
            discovered_links = []
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
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

            # Canonical tag
            canonical_tag = soup.find("link", attrs={"rel": "canonical"})
            canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else ""
            if canonical_url:
                canonical_url = urljoin(url, canonical_url)

            # Text content & word count
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()
            body_text = soup.get_text(separator=" ", strip=True)
            word_count = len(body_text.split())

            return {
                "url": url,
                "depth": depth,
                "status_code": status_code,
                "load_time_ms": load_time_ms,
                "html_size": len(resp.content),
                "title": title,
                "meta_description": meta_description,
                "h1_tags": h1_tags,
                "h2_tags": h2_tags,
                "images": images,
                "links": links,
                "discovered_links": discovered_links,
                "canonical_url": canonical_url,
                "word_count": word_count,
                "raw_soup": soup
            }
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return {
                "url": url,
                "depth": depth,
                "status_code": 0,
                "load_time_ms": 0,
                "html_size": 0,
                "title": "",
                "meta_description": "",
                "h1_tags": [],
                "h2_tags": [],
                "images": [],
                "links": [],
                "discovered_links": [],
                "canonical_url": "",
                "word_count": 0,
                "error": str(e)
            }
