import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://driverays.quest"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


DOWNLOAD_HOSTS = {
    "pixeldrain.com": "Pixeldrain",
    "pixeldrain.net": "Pixeldrain",
    "terabox.com": "Terabox",
    "teraboxapp.com": "Terabox",
    "1024terabox.com": "Terabox",
    "drive.google.com": "Google Drive",
    "mega.nz": "Mega",
    "acefile.co": "Acefile",
    "hxfile.co": "Hxfile",
    "hxfile.com": "Hxfile",
}


class DriveraysScraper:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            HEADERS
        )

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

        # WordPress-style search.
        search_url = (
            f"{BASE_URL}/"
            f"?s={requests.utils.quote(query)}"
        )

        response = self.get(
            search_url
        )

        soup = BeautifulSoup(
            response.text,
            "lxml",
        )

        results = []

        seen = set()

        # Try common WordPress post selectors first.
        selectors = [
            "article a[href]",
            ".post a[href]",
            ".entry-title a[href]",
            "h2 a[href]",
            "h3 a[href]",
        ]

        anchors = []

        for selector in selectors:

            found = soup.select(
                selector
            )

            if found:
                anchors.extend(
                    found
                )

        # Fallback.
        if not anchors:

            anchors = soup.select(
                "a[href]"
            )

        for anchor in anchors:

            href = anchor.get(
                "href"
            )

            if not href:
                continue

            href = urljoin(
                response.url,
                href,
            )

            parsed = urlparse(
                href
            )

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

            if len(text) < 2:
                continue

            path = parsed.path.lower()

            if (
                "/category/" in path
                or "/tag/" in path
                or "/page/" in path
                or "/genre/" in path
            ):
                continue

            if href in seen:
                continue

            seen.add(href)

            results.append(
                {
                    "title": text,
                    "url": href,
                }
            )

        # Remove duplicates by URL.
        unique = []

        urls = set()

        for item in results:

            if item["url"] in urls:
                continue

            urls.add(
                item["url"]
            )

            unique.append(
                item
            )

        return unique[:30]

    # ========================================================
    # TITLE
    # ========================================================

    def extract_title(self, soup):

        selectors = [
            "h1.entry-title",
            "h1.post-title",
            "h1",
            ".entry-title",
        ]

        for selector in selectors:

            element = soup.select_one(
                selector
            )

            if element:

                value = self.clean(
                    element.get_text(
                        " ",
                        strip=True,
                    )
                )

                if value:
                    return value

        title = soup.find(
            "title"
        )

        if title:

            return self.clean(
                title.get_text()
            )

        return "Unknown"

    # ========================================================
    # SCRAPE
    # ========================================================

    def scrape(self, url):

        if not url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            url = urljoin(
                BASE_URL,
                url,
            )

        response = self.get(
            url
        )

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

            href = anchor.get(
                "href"
            )

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

            seen.add(
                absolute
            )

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
            "source": "Driverays",
            "title": title,
            "url": response.url,
            "downloads": downloads,
        }