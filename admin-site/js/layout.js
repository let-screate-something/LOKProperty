/*
  layout.js - used by every page EXCEPT the login page.

  1. Blocks the page if the admin is not logged in.
  2. Draws the left menu (so we write it only once, not in every HTML file).

  Each page sets <body data-page="..."> so the right menu item is highlighted.
*/
(function () {
  // 1. Not logged in? go to the login page
  if (!getToken()) {
    window.location.href = "login.html";
    return;
  }

  // 2. Menu items: [page name, file, label]
  const items = [
    ["dashboard", "dashboard.html", "Dashboard"],
    ["properties", "properties.html", "Properties"],
    ["enquiries", "enquiries.html", "Enquiries"],
    ["sales", "sales.html", "Sales records"],
  ];
  const current = document.body.dataset.page;

  const links = items.map(([page, file, label]) =>
    `<a href="${file}" class="${page === current ? "active" : ""}">${label}</a>`
  ).join("");

  document.getElementById("sidebar").innerHTML = `
    <div class="brand">LOK <span>Admin</span></div>
    <nav>${links}</nav>
    <div class="sidebar-footer">
      <div class="who">Signed in as <strong>${esc(getUsername())}</strong></div>
      <button id="logoutBtn" class="btn btn-light btn-small">Log out</button>
    </div>`;

  document.getElementById("logoutBtn").addEventListener("click", () => {
    clearLogin();
    window.location.href = "login.html";
  });
})();
