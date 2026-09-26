from collections import deque
from urllib.parse import urlparse, urlunparse, urldefrag

class URLQueue:
    def __init__(self, initial_url: str, max_depth: int = 3):
        self.initial_url = self.normalize_url(initial_url)
        self.base_domain = urlparse(self.initial_url).netloc.lower()
        self.max_depth = max_depth
        self.queue = deque([(self.initial_url, 0)])  # (url, depth)
        self.visited = set()
        self.visited.add(self.initial_url)

    @staticmethod
    def normalize_url(url: str) -> str:
        url, _ = urldefrag(url)  # remove anchor fragments
        parsed = urlparse(url)
        # Normalize scheme & netloc to lower
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path or "/"
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))

    def is_same_domain(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc.lower() == self.base_domain or parsed.netloc.lower().endswith("." + self.base_domain)

    def add(self, url: str, depth: int) -> bool:
        if depth > self.max_depth:
            return False
        normalized = self.normalize_url(url)
        if not self.is_same_domain(normalized):
            return False
        if normalized in self.visited:
            return False
        self.visited.add(normalized)
        self.queue.append((normalized, depth))
        return True

    def pop(self):
        if self.queue:
            return self.queue.popleft()
        return None, 0

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def __len__(self):
        return len(self.queue)
