const sourceSelect = document.getElementById("source");

const urlInput = document.getElementById("url");

const scrapeButton = document.getElementById("scrapeButton");

const buttonIcon = document.getElementById("buttonIcon");

const buttonText = document.getElementById("buttonText");

const statusElement = document.getElementById("status");

const resultsElement = document.getElementById("results");

const toast = document.getElementById("toast");

/* ============================================================
   STATUS
   ============================================================ */

function setStatus(message, type = "loading") {
  statusElement.textContent = message;

  statusElement.className = `status ${type}`;
}

/* ============================================================
   CLEAR STATUS
   ============================================================ */

function clearStatus() {
  statusElement.textContent = "";

  statusElement.className = "status hidden";
}

/* ============================================================
   LOADING
   ============================================================ */

function setLoading(loading) {
  scrapeButton.disabled = loading;

  if (loading) {
    buttonIcon.textContent = "⏳";

    buttonText.textContent = "Scraping...";
  } else {
    buttonIcon.textContent = "↗";

    buttonText.textContent = "Scrape";
  }
}

/* ============================================================
   TOAST
   ============================================================ */

let toastTimeout;

function showToast(message) {
  toast.textContent = message;

  toast.classList.add("show");

  clearTimeout(toastTimeout);

  toastTimeout = setTimeout(() => {
    toast.classList.remove("show");
  }, 1800);
}

/* ============================================================
   COPY
   ============================================================ */

async function copyLink(url) {
  try {
    await navigator.clipboard.writeText(url);

    showToast("Link copied!");
  } catch (error) {
    /*
     * Fallback for browsers where
     * navigator.clipboard isn't available.
     */

    const textarea = document.createElement("textarea");

    textarea.value = url;

    textarea.style.position = "fixed";

    textarea.style.opacity = "0";

    document.body.appendChild(textarea);

    textarea.select();

    document.execCommand("copy");

    textarea.remove();

    showToast("Link copied!");
  }
}

/* ============================================================
   OPEN
   ============================================================ */

function openLink(url) {
  window.open(url, "_blank", "noopener,noreferrer");
}

/* ============================================================
   ESCAPE HTML
   ============================================================ */

function escapeHtml(value) {
  const div = document.createElement("div");

  div.textContent = value ?? "";

  return div.innerHTML;
}

/* ============================================================
   HOST ICON
   ============================================================ */

function getHostIcon(host) {
  const icons = {
    Pixeldrain: "☁",

    Terabox: "☁",

    "Google Drive": "☁",

    Mega: "☁",

    Acefile: "↗",

    Hxfile: "↗",
  };

  return icons[host] || "🔗";
}

/* ============================================================
   QUALITY SORT
   ============================================================ */

function qualityNumber(value) {
  const match = String(value).match(/\d+/);

  return match ? Number(match[0]) : 0;
}

/* ============================================================
   RENDER RESULTS
   ============================================================ */

function renderResults(data) {
  resultsElement.innerHTML = "";

  const title = data.title || "Unknown";

  const source = data.source || "Unknown";

  const titleCard = document.createElement("div");

  titleCard.className = "title-card";

  titleCard.innerHTML = `
        <h2>
            ${escapeHtml(title)}
        </h2>

        <div class="source">
            ${escapeHtml(source)}
        </div>
    `;

  resultsElement.appendChild(titleCard);

  const downloads = data.downloads || {};

  const qualities = Object.keys(downloads).sort(
    (a, b) => qualityNumber(b) - qualityNumber(a),
  );

  if (qualities.length === 0) {
    const empty = document.createElement("div");

    empty.className = "empty-state";

    empty.innerHTML = `
            <div class="empty-icon">
                🔗
            </div>

            <h2>
                No supported links found
            </h2>

            <p>
                No supported public download
                links were found on this page.
            </p>
        `;

    resultsElement.appendChild(empty);

    return;
  }

  qualities.forEach((quality) => {
    const links = downloads[quality] || [];

    const section = document.createElement("section");

    section.className = "quality-section";

    const header = document.createElement("div");

    header.className = "quality-header";

    header.innerHTML = `
                <span class="quality-name">
                    ${escapeHtml(String(quality).toUpperCase())}
                </span>

                <span class="host-count">
                    ${links.length} host${links.length === 1 ? "" : "s"}
                </span>
            `;

    section.appendChild(header);

    links.forEach((item) => {
      const host = item.host || "Unknown";

      const url = item.url || "";

      const card = document.createElement("div");

      card.className = "link-card";

      card.innerHTML = `
                        <div class="host-icon">
                            ${getHostIcon(host)}
                        </div>

                        <div class="link-info">

                            <div class="host-name">
                                ${escapeHtml(host)}
                            </div>

                            <div
                                class="link-url"
                                title="${escapeHtml(url)}"
                            >
                                ${escapeHtml(url)}
                            </div>

                        </div>

                        <div class="link-actions">

                            <button
                                class="icon-button copy-button"
                                title="Copy link"
                            >
                                📋
                            </button>

                            <button
                                class="icon-button open-button"
                                title="Open link"
                            >
                                ↗
                            </button>

                        </div>
                    `;

      card
        .querySelector(".copy-button")
        .addEventListener("click", () => copyLink(url));

      card
        .querySelector(".open-button")
        .addEventListener("click", () => openLink(url));

      section.appendChild(card);
    });

    resultsElement.appendChild(section);
  });
}

/* ============================================================
   ERROR
   ============================================================ */

function renderError(message) {
  resultsElement.innerHTML = `
        <div class="error-card">

            <div class="error-icon">
                ⚠️
            </div>

            <h2>
                Scraping failed
            </h2>

            <p>
                ${escapeHtml(message)}
            </p>

        </div>
    `;
}

/* ============================================================
   SCRAPE
   ============================================================ */

async function scrape() {
  const source = sourceSelect.value;

  const url = urlInput.value.trim();

  if (!url) {
    setStatus("Please enter a page URL.", "error");

    urlInput.focus();

    return;
  }

  try {
    new URL(url);
  } catch {
    setStatus("Please enter a valid URL.", "error");

    urlInput.focus();

    return;
  }

  setLoading(true);

  setStatus(`Scraping ${source}...`, "loading");

  try {
    const response = await fetch("/api/scrape", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        source,
        url,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Scraping failed.");
    }

    if (!result.success) {
      throw new Error("Scraping failed.");
    }

    renderResults(result.data);

    const downloads = result.data.downloads || {};

    const count = Object.values(downloads).reduce(
      (total, links) => total + links.length,
      0,
    );

    setStatus(
      `Found ${count} download link${count === 1 ? "" : "s"}.`,
      "success",
    );
  } catch (error) {
    renderError(error.message);

    setStatus(error.message, "error");
  } finally {
    setLoading(false);
  }
}

/* ============================================================
   EVENTS
   ============================================================ */

scrapeButton.addEventListener("click", scrape);

urlInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    scrape();
  }
});
