# Media Scraper

A simple desktop application built with **Python + Flet** for extracting publicly exposed download links from supported media websites.

Currently supported sources:

- **Kusonime**
- **Driverays**

The application uses direct page URLs rather than search, making scraping faster and more predictable.

## ✨ Features

- 🔗 Paste a media page URL
- 🌐 Choose the source website
- ⚡ Scrape the page directly
- 🎬 Automatically detect the title
- 📺 Group download links by quality
- 🔗 Detect supported download hosts
- 📋 Copy download links
- ↗️ Open download links in your browser
- 🖥️ Desktop UI using Flet
- 🧵 Background scraping so the UI doesn't freeze

## 📁 Project Structure

```text
media-scraper/
│
├── main.py
├── kusonime.py
├── drivebluray.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── assets/
    └── icon.png
```

## 🛠️ Requirements

- Python 3.10+
- Flet 0.86.5

Other dependencies are listed in `requirements.txt`.

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/media-scraper.git
cd media-scraper
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run

Start the application with:

```bash
python main.py
```

Or:

```bash
flet run main.py
```

## 🔗 Usage

1. Open the application.
2. Select a source:
   - Kusonime
   - Driverays

3. Paste the URL of the media page.
4. Press **Scrape** or hit **Enter**.
5. Wait for the results.
6. Copy or open the available links.

Example:

```text
Source:
[Kusonime]

URL:
https://kusonime.com/example-page/

[ Scrape ]
```

The application will then display available links grouped by quality:

```text
1080P

Pixeldrain       [Copy] [Open]
Terabox          [Copy] [Open]

720P

Pixeldrain       [Copy] [Open]
```

## 📦 Supported Hosts

The scraper currently recognizes several commonly exposed download hosts, depending on the source website.

Examples include:

- Pixeldrain
- Terabox
- Google Drive
- Mega
- Acefile
- Hxfile

The list can be expanded in `kusonime.py` and `drivebluray.py`.

## ⚙️ How It Works

The application has three main components:

### `main.py`

Handles the Flet user interface.

```text
User
 │
 ▼
Paste URL
 │
 ▼
Select source
 │
 ▼
Scrape
 │
 ▼
KusonimeScraper / DriveraysScraper
 │
 ▼
Parse HTML
 │
 ▼
Find supported links
 │
 ▼
Display results
```

### `kusonime.py`

Contains the Kusonime scraper.

Main methods:

```python
search(query)
scrape(url)
```

The current application uses:

```python
scrape(url)
```

because direct URL scraping is faster than performing a site-wide search first.

### `drivebluray.py`

Contains the Driverays scraper.

Main methods:

```python
search(query)
scrape(url)
```

The application currently uses the direct:

```python
scrape(url)
```

workflow.

## 🧪 Development

Run the application:

```bash
python main.py
```

If you modify dependencies:

```bash
pip freeze > requirements.txt
```

However, for a cleaner project, manually pin only the dependencies actually required by the application.

## 🏗️ Building for Windows

Flet can package the application as a Windows application.

```bash
flet build windows
```

The generated build files will be placed inside the project's build directory.

For the current development environment, this project targets:

```text
Flet 0.86.5
Flutter 3.44.8
```

## ⚠️ Disclaimer

This project is intended for educational and personal automation purposes.

The scraper only processes information and links that are publicly exposed by the target webpage. It does not attempt to bypass authentication, CAPTCHA, DRM, paywalls, or other access controls.

Make sure you have the right to access and download any content you use this application with, and comply with the terms of the websites you access.

## 📄 License

You can add your preferred license here.

For example:

```text
MIT License
```

---

Made with Python 🐍 and Flet.
