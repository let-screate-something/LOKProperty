/* sales.js - the buy records (one row for every sold property) */

async function loadSales() {
  const body = document.getElementById("salesBody");
  try {
    const rows = await apiRequest("/admin/sales");

    // Add up the sale prices for the summary line
    const total = rows.reduce((sum, s) => sum + Number(s.sale_price || 0), 0);
    document.getElementById("summary").textContent =
      rows.length + " sold · total " + formatPrice(total);

    if (rows.length === 0) {
      body.innerHTML = '<tr><td colspan="6" class="empty">No sales recorded yet</td></tr>';
      return;
    }
    body.innerHTML = rows.map((s) => `
      <tr>
        <td>${esc(formatDate(s.sold_on))}</td>
        <td><strong>${esc(s.property_title)}</strong><div class="muted">${esc(s.property_city)}</div></td>
        <td>${esc(s.buyer_name)}</td>
        <td>${s.buyer_email ? `<a href="mailto:${esc(s.buyer_email)}">${esc(s.buyer_email)}</a>` : ""}
            <div class="muted">${esc(s.buyer_phone)}</div></td>
        <td>${formatPrice(s.listed_price)}</td>
        <td><strong>${formatPrice(s.sale_price)}</strong></td>
      </tr>`).join("");
  } catch (error) {
    body.innerHTML = `<tr><td colspan="6" class="empty">${esc(error.message)}</td></tr>`;
  }
}

loadSales();
