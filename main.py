import threading
import webbrowser

import flet as ft

from kusonime import KusonimeScraper
from drivebluray import DriveraysScraper


# ============================================================
# HELPERS
# ============================================================

def quality_number(value):
    try:
        return int(
            "".join(
                c for c in value
                if c.isdigit()
            )
        )
    except Exception:
        return 0


def host_icon(host):
    icons = {
        "Pixeldrain": ft.Icons.CLOUD_DOWNLOAD,
        "Terabox": ft.Icons.CLOUD,
        "Google Drive": ft.Icons.CLOUD,
        "Mega": ft.Icons.CLOUD,
        "Acefile": ft.Icons.LINK,
        "Hxfile": ft.Icons.LINK,
    }

    return icons.get(
        host,
        ft.Icons.LINK,
    )


# ============================================================
# APP
# ============================================================

def main(page: ft.Page):

    page.title = "Matt's Scrapper"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0F19"
    page.padding = 0

    # --------------------------------------------------------
    # SCRAPERS
    # --------------------------------------------------------

    kusonime = KusonimeScraper()
    driverays = DriveraysScraper()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = ft.Container(
        content=ft.Row(
            [
                ft.Icon(
                    ft.Icons.DOWNLOAD,
                    size=34,
                    color="#60A5FA",
                ),

                ft.Column(
                    [
                        ft.Text(
                            "Matt's Scrapper",
                            size=27,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            "Extract publicly exposed download links",
                            size=13,
                            color="#9CA3AF",
                        ),
                    ],
                    spacing=2,
                ),
            ],
            spacing=12,
        ),

        padding=ft.Padding(
            left=30,
            right=30,
            top=25,
            bottom=20,
        ),
    )

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    source_dropdown = ft.Dropdown(
        label="Source",
        value="kusonime",

        options=[
            ft.DropdownOption(
                key="kusonime",
                text="Kusonime",
            ),

            ft.DropdownOption(
                key="driverays",
                text="Driverays",
            ),
        ],

        width=200,
    )

    # --------------------------------------------------------
    # URL INPUT
    # --------------------------------------------------------

    url_input = ft.TextField(
        label="Page URL",
        hint_text="Paste Kusonime / Driverays URL...",
        prefix_icon=ft.Icons.LINK,
        expand=True,
        autofocus=True,
    )

    # --------------------------------------------------------
    # SCRAPE BUTTON
    # --------------------------------------------------------

    scrape_button = ft.Button(
        "Scrape",
        icon=ft.Icons.SEARCH,
        height=50,
    )

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    progress = ft.ProgressRing(
        width=22,
        height=22,
        visible=False,
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = ft.Text(
        "",
        size=13,
        color="#9CA3AF",
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    results = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # ========================================================
    # MESSAGE
    # ========================================================

    def show_message(text):

        page.snack_bar = ft.SnackBar(
            content=ft.Text(text)
        )

        page.snack_bar.open = True
        page.update()

    # ========================================================
    # COPY
    # ========================================================

    async def copy_link(url):

        try:

            await page.clipboard.set(
                url
            )

            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    "Link copied to clipboard."
                )
            )

            page.snack_bar.open = True

            page.update()

        except Exception as exc:

            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    f"Clipboard error: {exc}"
                )
            )

            page.snack_bar.open = True

            page.update()

    # ========================================================
    # OPEN LINK
    # ========================================================

    def open_link(url):

        try:

            webbrowser.open(url)

        except Exception as exc:

            show_message(
                f"Could not open link: {exc}"
            )

    # ========================================================
    # DOWNLOAD CARD
    # ========================================================

    def create_download_card(item):

        host = item.get(
            "host",
            "Unknown",
        )

        url = item.get(
            "url",
            "",
        )

        return ft.Container(

            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            host_icon(host),
                            size=24,
                            color="#60A5FA",
                        ),

                        width=35,

                        alignment=ft.Alignment.CENTER,
                    ),

                    ft.Column(
                        [
                            ft.Text(
                                host,
                                size=15,
                                weight=(
                                    ft.FontWeight.BOLD
                                ),
                            ),

                            ft.Text(
                                url,
                                size=11,
                                color="#9CA3AF",
                                max_lines=2,
                                overflow=(
                                    ft.TextOverflow.ELLIPSIS
                                ),
                            ),
                        ],

                        spacing=3,

                        expand=True,
                    ),

                    ft.IconButton(
                        icon=ft.Icons.CONTENT_COPY,
                        tooltip="Copy link",

                        on_click=lambda e, u=url:
                            copy_link(u),
                    ),

                    ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        tooltip="Open link",

                        on_click=lambda e, u=url:
                            open_link(u),
                    ),
                ],

                spacing=10,

                vertical_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
            ),

            padding=15,

            bgcolor="#111827",

            border_radius=12,

            border=ft.Border.all(
                1,
                "#1F2937",
            ),
        )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    def display_results(data):

        results.controls.clear()

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = data.get(
            "title",
            "Unknown",
        )

        source = data.get(
            "source",
            "",
        )

        results.controls.append(

            ft.Container(

                content=ft.Column(
                    [
                        ft.Text(
                            title,
                            size=22,
                            weight=(
                                ft.FontWeight.BOLD
                            ),
                        ),

                        ft.Text(
                            source,
                            size=12,
                            color="#6B7280",
                        ),
                    ],

                    spacing=5,
                ),

                padding=20,

                bgcolor="#111827",

                border_radius=15,
            )
        )

        # ----------------------------------------------------
        # DOWNLOADS
        # ----------------------------------------------------

        downloads = data.get(
            "downloads",
            {},
        )

        if not downloads:

            results.controls.append(

                ft.Container(

                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.LINK_OFF,
                                size=40,
                                color="#6B7280",
                            ),

                            ft.Text(
                                "No supported download links found.",
                                color="#9CA3AF",
                            ),

                            ft.Text(
                                "The page may use a download host "
                                "that isn't supported yet.",
                                size=12,
                                color="#6B7280",
                            ),
                        ],

                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                    ),

                    padding=40,
                )
            )

            page.update()

            return

        # ----------------------------------------------------
        # SORT QUALITY
        # ----------------------------------------------------

        qualities = sorted(
            downloads.keys(),

            key=quality_number,

            reverse=True,
        )

        # ----------------------------------------------------
        # QUALITY SECTIONS
        # ----------------------------------------------------

        for quality in qualities:

            links = downloads[
                quality
            ]

            cards = []

            for item in links:

                cards.append(
                    create_download_card(
                        item
                    )
                )

            section = ft.Container(

                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    quality.upper(),
                                    size=18,
                                    weight=(
                                        ft.FontWeight.BOLD
                                    ),
                                ),

                                ft.Text(
                                    f"{len(links)} host(s)",
                                    size=12,
                                    color="#9CA3AF",
                                ),
                            ],

                            spacing=10,
                        ),

                        *cards,
                    ],

                    spacing=10,
                ),

                padding=20,

                bgcolor="#0F172A",

                border_radius=15,
            )

            results.controls.append(
                section
            )

        page.update()

    # ========================================================
    # SCRAPE
    # ========================================================

    def scrape():

        url = (
            url_input.value or ""
        ).strip()

        # ----------------------------------------------------
        # VALIDATE URL
        # ----------------------------------------------------

        if not url:

            status.value = (
                "Please paste a page URL first."
            )

            status.color = "#F87171"

            page.update()

            return

        if not url.startswith(
            (
                "http://",
                "https://",
            )
        ):

            status.value = (
                "URL must start with http:// or https://"
            )

            status.color = "#F87171"

            page.update()

            return

        source = (
            source_dropdown.value
        )

        # ----------------------------------------------------
        # UI STATE
        # ----------------------------------------------------

        scrape_button.disabled = True

        progress.visible = True

        status.value = (
            f"Scraping {source.title()}..."
        )

        status.color = "#60A5FA"

        results.controls.clear()

        page.update()

        # ----------------------------------------------------
        # WORKER
        # ----------------------------------------------------

        def worker():

            try:

                if source == "kusonime":

                    data = kusonime.scrape(
                        url
                    )

                elif source == "driverays":

                    data = driverays.scrape(
                        url
                    )

                else:

                    raise ValueError(
                        "Unknown source."
                    )

                # --------------------------------------------
                # DISPLAY
                # --------------------------------------------

                display_results(
                    data
                )

                total = sum(
                    len(values)

                    for values
                    in data.get(
                        "downloads",
                        {},
                    ).values()
                )

                status.value = (
                    f"Found {total} download link(s)."
                )

                status.color = "#4ADE80"

            except Exception as exc:

                results.controls.clear()

                results.controls.append(

                    ft.Container(

                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.ERROR_OUTLINE,
                                    size=40,
                                    color="#F87171",
                                ),

                                ft.Text(
                                    "Scraping failed.",
                                    size=18,
                                    weight=(
                                        ft.FontWeight.BOLD
                                    ),
                                ),

                                ft.Text(
                                    str(exc),
                                    size=12,
                                    color="#9CA3AF",
                                ),
                            ],

                            horizontal_alignment=(
                                ft.CrossAxisAlignment.CENTER
                            ),
                        ),

                        padding=40,
                    )
                )

                status.value = (
                    f"Error: {exc}"
                )

                status.color = "#F87171"

                page.update()

            finally:

                progress.visible = False

                scrape_button.disabled = False

                page.update()

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    # ========================================================
    # BUTTON
    # ========================================================

    scrape_button.on_click = (
        lambda e:
        scrape()
    )

    # ========================================================
    # ENTER KEY
    # ========================================================

    url_input.on_submit = (
        lambda e:
        scrape()
    )

    # ========================================================
    # SOURCE CHANGE
    # ========================================================

    def source_changed(e):

        status.value = ""

        results.controls.clear()

        page.update()

    source_dropdown.on_change = (
        source_changed
    )

    # ========================================================
    # INPUT SECTION
    # ========================================================

    input_section = ft.Container(

        content=ft.Column(
            [
                ft.Row(
                    [
                        source_dropdown,

                        url_input,

                        scrape_button,

                        progress,
                    ],

                    spacing=10,
                ),

                status,
            ],

            spacing=8,
        ),

        padding=ft.Padding(
            left=30,
            right=30,
            bottom=20,
        ),
    )

    # ========================================================
    # RESULTS HEADER
    # ========================================================

    results_header = ft.Container(

        content=ft.Text(
            "Results",
            size=18,
            weight=ft.FontWeight.BOLD,
        ),

        padding=ft.Padding(
            left=30,
            right=30,
            bottom=10,
        ),
    )

    # ========================================================
    # RESULTS
    # ========================================================

    results_container = ft.Container(

        content=results,

        expand=True,

        padding=ft.Padding(
            left=30,
            right=30,
            bottom=30,
        ),
    )

    # ========================================================
    # PAGE
    # ========================================================

    page.add(
        header,
        input_section,
        results_header,
        results_container,
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    ft.run(main)