import logging
import urllib.robotparser
from urllib.parse import urlparse, urljoin
import requests

logger = logging.getLogger(__name__)

class RobotsChecker:
    def __init__(self, target_url: str, user_agent: str = "SEOAgentBot/1.0"):
        self.user_agent = user_agent
        self.parser = urllib.robotparser.RobotFileParser()
        self.parsed_target = urlparse(target_url)
        self.base_url = f"{self.parsed_target.scheme}://{self.parsed_target.netloc}"
        self.robots_url = urljoin(self.base_url, "/robots.txt")
        self.sitemaps = []
        self.has_robots_txt = False
        self._load_robots()

    def _load_robots(self):
        try:
            resp = requests.get(self.robots_url, timeout=5, headers={"User-Agent": self.user_agent})
            if resp.status_code == 200:
                self.has_robots_txt = True
                self.parser.parse(resp.text.splitlines())
                # Extract sitemaps
                for line in resp.text.splitlines():
                    if line.strip().lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        self.sitemaps.append(sitemap_url)
            else:
                self.has_robots_txt = False
                self.parser.allow_all = True
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt for {self.base_url}: {e}")
            self.has_robots_txt = False
            self.parser.allow_all = True

    def is_allowed(self, url: str) -> bool:
        if not self.has_robots_txt:
            return True
        try:
            return self.parser.can_fetch(self.user_agent, url)
        except Exception:
            return True
