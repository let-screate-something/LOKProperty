/*
  api.js - helpers used by every public page.

  - publicRequest()  sends a request to the API (no login token needed)
  - esc()            makes text safe before putting it in innerHTML
  - formatPrice()    formats a number as Indian rupee string  e.g. ₹45,00,000
  - formatDate()     formats a date string for display        e.g. 22 Oct 2026
  - showToast()      shows a small pop-up message at the bottom of the screen
  - buildQuery()     builds a URL query string from an object
*/

/*
  Send a GET or POST request to the public API (no login needed).
  path    - e.g. "/properties" or "/enquiries"
  options - optional: { method, body } where body is a plain object
  Returns the parsed JSON on success.
  Throws an Error with the server's error message on failure.
*/
async function publicRequest(path, { method = "GET", body = null } = {}) {
  const headers = { "Content-Type": "application/json" };

  let response;
  try {
    response = await fetch(API_URL + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (_networkError) {
    throw new Error("Could not reach the server. Please check your connection.");
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }
  return data;
}

/* ---------- small helpers ---------- */

/*
  Escape special HTML characters so user data cannot run as code.
  Always use this when inserting server data into innerHTML.
  Example: esc("<script>") → "&lt;script&gt;"
*/
function esc(text) {
  return String(text ?? "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

/*
  Format a raw number as Indian rupee string.
  Example: formatPrice(4500000) → "₹45,00,000"
*/
function formatPrice(value) {
  const number = Number(value || 0);
  return "₹" + number.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

/*
  Format a SQLite date/time string for display.
  Example: formatDate("2026-10-22 05:05:55") → "22 Oct 2026"
*/
function formatDate(text) {
  if (!text) return "";
  /* SQLite stores dates with a space; Date() needs a T for reliable parsing */
  const date = new Date(text.replace(" ", "T").slice(0, 10) + "T00:00:00");
  if (isNaN(date)) return text;
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

/*
  Show a small message at the bottom of the screen for 3.5 seconds.
  isError = true makes it red.
*/
function showToast(message, isError = false) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.className = "toast show" + (isError ? " error" : "");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => (toast.className = "toast"), 3500);
}

/*
  Build a URL query string from an object, skipping empty values.
  Example: buildQuery({ type: "plot", city: "" }) → "?type=plot"
*/
function buildQuery(params) {
  const parts = [];
  for (const [key, value] of Object.entries(params)) {
    if (value !== "" && value !== null && value !== undefined) {
      parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(value));
    }
  }
  return parts.length ? "?" + parts.join("&") : "";
}

/*
  Read query string parameters from the current page URL.
  Returns an object. Missing keys return "".
*/
function getQueryParams() {
  const params = {};
  new URLSearchParams(window.location.search).forEach((value, key) => {
    params[key] = value;
  });
  return params;
}
