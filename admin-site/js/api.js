/*
  api.js - helpers shared by every admin page.

  - apiRequest()  talks to the server and adds the login token automatically
  - login state   (token saved in the browser's sessionStorage)
  - small helpers for safe text, prices, dates and pop-up messages
*/

const TOKEN_KEY = "lok_admin_token";
const USER_KEY = "lok_admin_user";

// sessionStorage = the login is forgotten when the browser tab is closed
function getToken() {
  try { return sessionStorage.getItem(TOKEN_KEY); } catch (e) { return null; }
}
function saveLogin(token, username) {
  try {
    sessionStorage.setItem(TOKEN_KEY, token);
    sessionStorage.setItem(USER_KEY, username);
  } catch (e) { /* storage blocked: login will not persist */ }
}
function clearLogin() {
  try {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  } catch (e) { /* ignore */ }
}
function getUsername() {
  try { return sessionStorage.getItem(USER_KEY) || "admin"; } catch (e) { return "admin"; }
}

/*
  Send a request to the server.
    apiRequest("/admin/properties")                          -> GET
    apiRequest("/admin/properties", {method:"POST", body})   -> POST with JSON
  Returns the JSON answer. Throws an Error (with the server's message) on failure.
*/
async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) headers["Authorization"] = "Bearer " + getToken();

  let response;
  try {
    response = await fetch(API_URL + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkError) {
    throw new Error("Cannot reach the server. Is it running?");
  }

  const data = await response.json().catch(() => ({}));

  // Token missing/expired: send the admin back to the login page
  if (response.status === 401 && auth) {
    clearLogin();
    window.location.href = "login.html";
    throw new Error(data.error || "Please log in again");
  }
  if (!response.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

/* ---------- small helpers ---------- */

// Make text safe before putting it inside HTML (stops visitors injecting scripts)
function esc(text) {
  return String(text ?? "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

// 4500000 -> "₹45,00,000" (Indian number style)
function formatPrice(value) {
  const number = Number(value || 0);
  return "₹" + number.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

// "2026-10-22 05:05:55" -> "22 Oct 2026"
function formatDate(text) {
  if (!text) return "";
  const date = new Date(text.replace(" ", "T").slice(0, 10) + "T00:00:00");
  if (isNaN(date)) return text;
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

// Small message at the bottom of the screen
function showToast(message, isError = false) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.className = "toast show" + (isError ? " error" : "");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => (toast.className = "toast"), 3500);
}
