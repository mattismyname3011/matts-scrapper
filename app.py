from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

from kusonime import KusonimeScraper
from drivebluray import DriveraysScraper


app = FastAPI(
    title="Media Scraper",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

kusonime = KusonimeScraper()
driverays = DriveraysScraper()

executor = ThreadPoolExecutor(
    max_workers=4
)


class ScrapeRequest(BaseModel):
    source: str
    url: HttpUrl


def get_hostname(url: str) -> str:
    hostname = urlparse(url).hostname

    if not hostname:
        return ""

    return hostname.lower()


def validate_source(source: str, url: str):

    hostname = get_hostname(url)

    if source == "kusonime":

        if not (
            hostname == "kusonime.com"
            or hostname.endswith(".kusonime.com")
        ):
            raise HTTPException(
                status_code=400,
                detail="The URL is not a Kusonime URL.",
            )

    elif source == "driverays":

        if not (
            hostname == "driverays.quest"
            or hostname.endswith(".driverays.quest")
        ):
            raise HTTPException(
                status_code=400,
                detail="The URL is not a Driverays URL.",
            )

    else:

        raise HTTPException(
            status_code=400,
            detail="Unsupported source.",
        )


@app.get("/")
async def index():

    return FileResponse(
        "templates/index.html"
    )


@app.get("/api/health")
async def health():

    return {
        "status": "ok",
        "service": "media-scraper",
    }


@app.post("/api/scrape")
async def scrape(request: ScrapeRequest):

    source = request.source.lower().strip()
    url = str(request.url)

    validate_source(
        source,
        url,
    )

    if source == "kusonime":

        scraper = kusonime

    else:

        scraper = driverays

    try:

        # Run the synchronous scraper
        # outside the async event loop.
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
            detail="Scraping timed out.",
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@app.get("/api/sources")
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