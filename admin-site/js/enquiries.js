/* enquiries.js - shows messages sent by visitors from the public website */

async function loadEnquiries() {
  const body = document.getElementById("enquiryBody");
  try {
    const rows = await apiRequest("/admin/enquiries");
    document.getElementById("count").textContent = rows.length + " total";

    if (rows.length === 0) {
      body.innerHTML = '<tr><td colspan="6" class="empty">No enquiries yet</td></tr>';
      return;
    }
    body.innerHTML = rows.map((e) => `
      <tr>
        <td>${esc(formatDate(e.created_at))}</td>
        <td>${esc(e.name)}</td>
        <td><a href="mailto:${esc(e.email)}">${esc(e.email)}</a></td>
        <td>${esc(e.property_title || "General")}</td>
        <td class="message-cell">${esc(e.message)}</td>
        <td><button class="btn btn-small btn-danger" data-id="${e.id}">Delete</button></td>
      </tr>`).join("");
  } catch (error) {
    body.innerHTML = `<tr><td colspan="6" class="empty">${esc(error.message)}</td></tr>`;
  }
}

// Delete button (one listener for the whole table)
document.getElementById("enquiryBody").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-id]");
  if (!button || !confirm("Delete this enquiry?")) return;
  try {
    await apiRequest("/admin/enquiries/" + button.dataset.id, { method: "DELETE" });
    showToast("Enquiry deleted");
    loadEnquiries();
  } catch (error) {
    showToast(error.message, true);
  }
});

loadEnquiries();
