# Media Scraper

A lightweight web application for extracting publicly exposed
download links from supported media pages.

## Features

- Direct URL scraping
- Kusonime support
- Driverays support
- Download links grouped by quality
- Copy links
- Open links
- Responsive design
- SEO-friendly pages
- Sitemap
- Robots.txt
- Open Graph metadata
- JSON-LD structured data
- FastAPI backend

## Project Structure

```text
media-scraper/
├── app.py
├── kusonime.py
├── drivebluray.py
├── requirements.txt
├── render.yaml
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── kusonime.html
│   ├── driverays.html
│   ├── how-to-use.html
│   └── about.html
│
└── static/
    ├── style.css
    ├── app.js
    ├── robots.txt
    └── sitemap.xml
```
