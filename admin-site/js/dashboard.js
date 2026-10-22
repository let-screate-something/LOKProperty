/* dashboard.js - fills the numbers and the latest enquiries */

async function loadDashboard() {
  try {
    // Ask the server for both things at the same time
    const [stats, enquiries] = await Promise.all([
      apiRequest("/admin/stats"),
      apiRequest("/admin/enquiries"),
    ]);

    document.getElementById("statTotal").textContent = stats.total;
    document.getElementById("statAvailable").textContent = stats.available;
    document.getElementById("statSold").textContent = stats.sold;
    document.getElementById("statEnquiries").textContent = stats.enquiries;
    document.getElementById("statSales").textContent = formatPrice(stats.sales_total);

    const body = document.getElementById("recentBody");
    const latest = enquiries.slice(0, 5);   // only the 5 newest
    if (latest.length === 0) {
      body.innerHTML = '<tr><td colspan="5" class="empty">No enquiries yet</td></tr>';
      return;
    }
    body.innerHTML = latest.map((e) => `
      <tr>
        <td>${esc(formatDate(e.created_at))}</td>
        <td>${esc(e.name)}</td>
        <td><a href="mailto:${esc(e.email)}">${esc(e.email)}</a></td>
        <td>${esc(e.property_title || "General")}</td>
        <td class="message-cell">${esc(e.message)}</td>
      </tr>`).join("");
  } catch (error) {
    showToast(error.message, true);
  }
}

loadDashboard();
