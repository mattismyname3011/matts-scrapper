import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://kusonime.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
}


DOWNLOAD_HOSTS = {
    "pixeldrain.com": "Pixeldrain",
    "pixeldrain.net": "Pixeldrain",
    "terabox.com": "Terabox",
    "teraboxapp.com": "Terabox",
    "1024terabox.com": "Terabox",
    "acefile.co": "Acefile",
    "hxfile.co": "Hxfile",
    "hxfile.com": "Hxfile",
}


class KusonimeScraper:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    # ========================================================
    # HTTP
    # ========================================================

    def get(self, url):
        response = self.session.get(
            url,
            timeout=20,
            allow_redirects=True,
        )

        response.raise_for_status()

        return response

    # ========================================================
    # UTIL
    # ========================================================

    @staticmethod
    def clean(text):
        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    @staticmethod
    def detect_host(url):

        hostname = urlparse(url).hostname

        if not hostname:
            return None

        hostname = hostname.lower()

        for domain, name in DOWNLOAD_HOSTS.items():

            if (
                hostname == domain
                or hostname.endswith("." + domain)
            ):
                return name

        return None

    @staticmethod
    def detect_quality(text):

        text = text.upper()

        qualities = [
            "2160P",
            "1440P",
            "1080P",
            "720P",
            "480P",
            "360P",
            "240P",
        ]

        for quality in qualities:

            if quality in text:
                return quality.lower()

        return None

    # ========================================================
    # SEARCH
    # ========================================================

    def search(self, query):

        query = query.strip()

        if not query:
            return []

        # Kusonime uses WordPress-style search.
        search_url = (
            f"{BASE_URL}/"
            f"?s={requests.utils.quote(query)}"
        )

        response = self.get(search_url)

        soup = BeautifulSoup(
            response.text,
            "lxml",
        )

        results = []
        seen = set()

        # Search result links.
        for anchor in soup.select(
            "a[href]"
        ):

            href = anchor.get("href")

            if not href:
                continue

            href = urljoin(
                response.url,
                href,
            )

            parsed = urlparse(href)

            if parsed.netloc != urlparse(
                BASE_URL
            ).netloc:
                continue

            text = self.clean(
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )

            if not text:
                continue

            # Avoid navigation/category links.
            if len(text) < 2:
                continue

            if href.rstrip("/") == BASE_URL.rstrip("/"):
                continue

            if href in seen:
                continue

            # Look for links that resemble posts.
            path = parsed.path.lower()

            if (
                "/category/" in path
                or "/tag/" in path
                or "/page/" in path
                or "/genre/" in path
            ):
                continue

            seen.add(href)

            results.append(
                {
                    "title": text,
                    "url": href,
                }
            )

        # Remove obvious duplicates.
        unique = []

        titles = set()

        for result in results:

            key = (
                result["title"].lower(),
                result["url"],
            )

            if key in titles:
                continue

            titles.add(key)
            unique.append(result)

        return unique[:30]

    # ========================================================
    # TITLE
    # ========================================================

    def extract_title(self, soup):

        selectors = [
            "h1.entry-title",
            "h1.post-title",
            "h1",
        ]

        for selector in selectors:

            element = soup.select_one(
                selector
            )

            if element:

                text = self.clean(
                    element.get_text(
                        " ",
                        strip=True,
                    )
                )

                if text:
                    return text

        title = soup.find("title")

        if title:

            text = self.clean(
                title.get_text()
            )

            text = re.sub(
                r"\s*[-|]\s*Kusonime.*$",
                "",
                text,
                flags=re.IGNORECASE,
            )

            return text

        return "Unknown"

    # ========================================================
    # SCRAPE DOWNLOAD LINKS
    # ========================================================

    def scrape(self, url):

        response = self.get(url)

        soup = BeautifulSoup(
            response.text,
            "lxml",
        )

        title = self.extract_title(
            soup
        )

        downloads = {}

        seen = set()

        for anchor in soup.select(
            "a[href]"
        ):

            href = anchor.get("href")

            if not href:
                continue

            absolute = urljoin(
                response.url,
                href,
            )

            host = self.detect_host(
                absolute
            )

            if not host:
                continue

            if absolute in seen:
                continue

            seen.add(absolute)

            text = self.clean(
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )

            context = text

            if anchor.parent:

                context = self.clean(
                    anchor.parent.get_text(
                        " ",
                        strip=True,
                    )
                )

            quality = self.detect_quality(
                f"{text} {context}"
            )

            if not quality:
                quality = "unknown"

            downloads.setdefault(
                quality,
                []
            )

            downloads[quality].append(
                {
                    "host": host,
                    "url": absolute,
                    "text": text,
                }
            )

        return {
            "source": "Kusonime",
            "title": title,
            "url": response.url,
            "downloads": downloads,
        }