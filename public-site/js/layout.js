/*
  layout.js - writes the navbar and footer on every page.

  Call initLayout() once at the top of each page's JS file.
  It reads BUSINESS_NAME, PHONE, WHATSAPP_NUMBER, EMAIL, ADDRESS from config.js.
  It marks the current page's nav link as active based on the URL.
*/

/* Build and insert the navbar at the top of <body>. */
function buildNavbar() {
  /* Determine which page is active so we can highlight the right nav link */
  const page = window.location.pathname.split("/").pop() || "index.html";

  const links = [
    { href: "index.html",    label: "Home" },
    { href: "listings.html", label: "Properties" },
    { href: "about.html",    label: "About" },
    { href: "contact.html",  label: "Contact" },
  ];

  /* Build list items; mark the active one */
  const navItems = links.map((link) => {
    const isActive = page === link.href || (page === "" && link.href === "index.html");
    return `<li>
      <a href="${link.href}" class="nav-link${isActive ? " active" : ""}">${esc(link.label)}</a>
    </li>`;
  }).join("");

  const navbar = document.createElement("header");
  navbar.className = "site-header";
  /* Use textContent-safe pattern: build structure then set text nodes individually */
  navbar.innerHTML = `
    <div class="header-inner">
      <a href="index.html" class="brand" aria-label="${esc(BUSINESS_NAME)} - Home">
        <span class="brand-lok">LOK</span><span class="brand-rest"> Property Solutions</span>
      </a>
      <button class="nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false"
              aria-controls="mainNav">
        <span class="hamburger"></span>
      </button>
      <nav id="mainNav" aria-label="Main navigation">
        <ul class="nav-list">${navItems}</ul>
      </nav>
    </div>
  `;
  document.body.prepend(navbar);

  /* Toggle hamburger menu on phones */
  const toggleBtn = document.getElementById("navToggle");
  const nav = document.getElementById("mainNav");
  toggleBtn.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggleBtn.setAttribute("aria-expanded", open ? "true" : "false");
  });

  /* Close menu when a link is clicked (useful on phones) */
  nav.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      toggleBtn.setAttribute("aria-expanded", "false");
    });
  });
}

/* Build and insert the footer at the end of <body>. */
function buildFooter() {
  const footer = document.createElement("footer");
  footer.className = "site-footer";
  footer.innerHTML = `
    <div class="footer-inner">
      <div class="footer-col">
        <p class="footer-brand"><span class="brand-lok">LOK</span> Property Solutions</p>
        <p class="footer-tagline">${esc(TAGLINE)}</p>
      </div>
      <div class="footer-col">
        <h3 class="footer-heading">Quick links</h3>
        <ul class="footer-links">
          <li><a href="index.html">Home</a></li>
          <li><a href="listings.html">All Properties</a></li>
          <li><a href="listings.html?type=plot">Plots</a></li>
          <li><a href="listings.html?type=house">Houses</a></li>
          <li><a href="about.html">About us</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3 class="footer-heading">Contact us</h3>
        <ul class="footer-contact-list">
          <li>
            <a href="tel:${esc(PHONE)}" class="footer-contact-link">
              <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07
                         A19.5 19.5 0 0 1 4.63 12 19.79 19.79 0 0 1 1.58 3.48
                         2 2 0 0 1 3.55 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81
                         a2 2 0 0 1-.45 2.11L7.91 8.91a16 16 0 0 0 6.06 6.06l.91-.91
                         a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.92 16.92z"/>
              </svg>
              ${esc(PHONE)}
            </a>
          </li>
          <li>
            <a href="https://wa.me/${esc(WHATSAPP_NUMBER)}" target="_blank" rel="noopener"
               class="footer-contact-link">
              <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148
                         -.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075
                         -.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059
                         -.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174
                         .198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612
                         -.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01
                         -.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462
                         1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306
                         1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719
                         2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
                <path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.554 4.118 1.528 5.847L0 24l6.335-1.51
                         A11.943 11.943 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.894
                         a9.887 9.887 0 0 1-5.031-1.381l-.361-.214-3.741.982.997-3.648-.235-.374
                         A9.893 9.893 0 0 1 2.106 12C2.106 6.579 6.579 2.106 12 2.106
                         17.421 2.106 21.894 6.579 21.894 12S17.421 21.894 12 21.894z"/>
              </svg>
              WhatsApp
            </a>
          </li>
          <li>
            <a href="mailto:${esc(EMAIL)}" class="footer-contact-link">
              <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="4" width="20" height="16" rx="2"/>
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
              </svg>
              ${esc(EMAIL)}
            </a>
          </li>
          <li class="footer-address">
            <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            ${esc(ADDRESS)}
          </li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; ${new Date().getFullYear()} ${esc(BUSINESS_NAME)}. All rights reserved.</p>
    </div>
  `;
  document.body.appendChild(footer);
}

/* Add a toast div that api.js showToast() uses, if not already present. */
function ensureToast() {
  if (!document.getElementById("toast")) {
    const t = document.createElement("div");
    t.id = "toast";
    t.className = "toast";
    document.body.appendChild(t);
  }
}

/*
  initLayout() - call this at the top of every page JS file.
  Builds the navbar and footer, and sets up the toast container.
*/
function initLayout() {
  buildNavbar();
  buildFooter();
  ensureToast();
}
