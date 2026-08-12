from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

from kusonime import KusonimeScraper
from drivebluray import DriveraysScraper


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Media Scraper",
    description=(
        "A free web application for extracting "
        "publicly exposed download links."
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static",
)


# ============================================================
# SCRAPERS
# ============================================================

kusonime = KusonimeScraper()
driverays = DriveraysScraper()


executor = ThreadPoolExecutor(
    max_workers=4
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ScrapeRequest(BaseModel):

    source: str

    url: HttpUrl


# ============================================================
# URL VALIDATION
# ============================================================

def get_hostname(url: str) -> str:

    hostname = urlparse(url).hostname

    if not hostname:
        return ""

    return hostname.lower()


def validate_source(
    source: str,
    url: str,
):

    hostname = get_hostname(url)

    if source == "kusonime":

        valid = (
            hostname == "kusonime.com"
            or hostname.endswith(".kusonime.com")
        )

        if not valid:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Please use a valid Kusonime URL."
                ),
            )

    elif source == "driverays":

        valid = (
            hostname == "driverays.quest"
            or hostname.endswith(".driverays.quest")
        )

        if not valid:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Please use a valid Driverays URL."
                ),
            )

    else:

        raise HTTPException(
            status_code=400,
            detail="Unsupported source.",
        )


# ============================================================
# SEO PAGES
# ============================================================

@app.get("/")
async def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": (
                "Media Scraper - Find Download Links Easily"
            ),

            "description": (
                "Free online media scraper for extracting "
                "publicly exposed download links from "
                "supported media pages."
            ),

            "canonical": "/",
        },
    )


@app.get("/kusonime")
async def kusonime_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="kusonime.html",
        context={
            "title": (
                "Kusonime Download Link Scraper"
            ),

            "description": (
                "Extract publicly exposed download links "
                "from Kusonime pages using a direct URL."
            ),

            "canonical": "/kusonime",
        },
    )


@app.get("/driverays")
async def driverays_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="driverays.html",
        context={
            "title": (
                "Driverays Download Link Scraper"
            ),

            "description": (
                "Extract publicly exposed download links "
                "from Driverays pages using a direct URL."
            ),

            "canonical": "/driverays",
        },
    )


@app.get("/how-to-use")
async def how_to_use(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="how-to-use.html",
        context={
            "title": (
                "How to Use Media Scraper"
            ),

            "description": (
                "Learn how to use Media Scraper "
                "to extract publicly exposed download links."
            ),

            "canonical": "/how-to-use",
        },
    )


@app.get("/about")
async def about(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "title": (
                "About Media Scraper"
            ),

            "description": (
                "Learn about Media Scraper, "
                "its features, and how it works."
            ),

            "canonical": "/about",
        },
    )


# ============================================================
# SEO FILES
# ============================================================

@app.get(
    "/robots.txt",
    include_in_schema=False,
)
async def robots():

    return FileResponse(
        BASE_DIR / "static" / "robots.txt",
        media_type="text/plain",
    )


@app.get(
    "/sitemap.xml",
    include_in_schema=False,
)
async def sitemap():

    return FileResponse(
        BASE_DIR / "static" / "sitemap.xml",
        media_type="application/xml",
    )


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/api/health",
    include_in_schema=False,
)
async def health():

    return {
        "status": "ok",
        "service": "media-scraper",
    }


# ============================================================
# SOURCES
# ============================================================

@app.get(
    "/api/sources",
    include_in_schema=False,
)
async def sources():

    return {
        "sources": [
            {
                "id": "kusonime",
                "name": "Kusonime",
                "domain": "kusonime.com",
            },
            {
                "id": "driverays",
                "name": "Driverays",
                "domain": "driverays.quest",
            },
        ]
    }


# ============================================================
# SCRAPE
# ============================================================

@app.post("/api/scrape")
async def scrape(
    request: ScrapeRequest,
):

    source = request.source.lower().strip()

    url = str(request.url)

    validate_source(
        source,
        url,
    )

    if source == "kusonime":

        scraper = kusonime

    elif source == "driverays":

        scraper = driverays

    else:

        raise HTTPException(
            status_code=400,
            detail="Unsupported source.",
        )

    try:

        future = executor.submit(
            scraper.scrape,
            url,
        )

        result = future.result(
            timeout=60
        )

        return {
            "success": True,
            "data": result,
        }

    except TimeoutError:

        raise HTTPException(
            status_code=504,
            detail=(
                "Scraping timed out. "
                "Please try again."
            ),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )