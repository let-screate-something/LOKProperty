/*
  properties.js - the Properties page.

  Parts:
    1. load + show the table (with filters)
    2. add / edit pop-up
    3. mark sold pop-up (saves the buy record)
    4. make available again, delete
*/

let allProperties = [];        // everything from the server
let editingId = null;          // id of the property being edited (null = adding new)
let soldId = null;             // id of the property being marked sold

// Shortcut to find an element
const $ = (id) => document.getElementById(id);

/* ------------------------------------------------------------------
   1. Load and show the table
------------------------------------------------------------------ */
async function loadProperties() {
  try {
    allProperties = await apiRequest("/admin/properties");
    renderTable();
  } catch (error) {
    $("propertyBody").innerHTML = `<tr><td colspan="7" class="empty">${esc(error.message)}</td></tr>`;
  }
}

function renderTable() {
  // Apply the three filters
  const status = $("filterStatus").value;
  const type = $("filterType").value;
  const search = $("filterSearch").value.trim().toLowerCase();

  const rows = allProperties.filter((p) =>
    (!status || p.status === status) &&
    (!type || p.type === type) &&
    (!search || (p.title + " " + p.city).toLowerCase().includes(search))
  );

  if (rows.length === 0) {
    $("propertyBody").innerHTML = '<tr><td colspan="7" class="empty">No properties found</td></tr>';
    return;
  }

  $("propertyBody").innerHTML = rows.map((p) => {
    const photo = p.cover_image
      ? `<img class="thumb" src="${esc(p.cover_image)}" alt="" loading="lazy">`
      : '<div class="thumb"></div>';

    // Different buttons depending on the current status
    const statusButton = p.status === "available"
      ? `<button class="btn btn-small btn-success" data-action="sold" data-id="${p.id}">Mark sold</button>`
      : `<button class="btn btn-small btn-light" data-action="available" data-id="${p.id}">Make available</button>`;

    return `
      <tr>
        <td>${photo}</td>
        <td><strong>${esc(p.title)}</strong><div class="muted">${p.area_sqft ? esc(p.area_sqft) + " sq ft" : ""}${p.type === "house" && p.bedrooms ? " · " + esc(p.bedrooms) + " BHK" : ""}</div></td>
        <td>${p.type === "house" ? "House" : "Plot"}</td>
        <td>${esc(p.city)}</td>
        <td>${formatPrice(p.price)}</td>
        <td><span class="badge ${p.status}">${p.status === "sold" ? "Sold" : "Available"}</span></td>
        <td>
          <div class="actions">
            ${statusButton}
            <button class="btn btn-small btn-light" data-action="edit" data-id="${p.id}">Edit</button>
            <button class="btn btn-small btn-danger" data-action="delete" data-id="${p.id}">Delete</button>
          </div>
        </td>
      </tr>`;
  }).join("");
}

["filterStatus", "filterType"].forEach((id) => $(id).addEventListener("change", renderTable));
$("filterSearch").addEventListener("input", renderTable);

// One listener for all buttons inside the table (event delegation)
$("propertyBody").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = Number(button.dataset.id);
  const action = button.dataset.action;

  if (action === "edit") openPropertyDialog(id);
  if (action === "sold") openSoldDialog(id);
  if (action === "available") makeAvailable(id);
  if (action === "delete") deleteProperty(id);
});

// Any button with data-close="dialogId" closes that pop-up
document.addEventListener("click", (event) => {
  const closeId = event.target.dataset && event.target.dataset.close;
  if (closeId) $(closeId).close();
});

/* ------------------------------------------------------------------
   2. Add / edit pop-up
------------------------------------------------------------------ */
// Bedrooms only matter for houses, so hide the field for plots
function updateBedroomsField() {
  $("bedroomsField").style.display = $("fType").value === "house" ? "" : "none";
}
$("fType").addEventListener("change", updateBedroomsField);

async function openPropertyDialog(id = null) {
  editingId = id;
  $("propertyForm").reset();
  $("propertyError").textContent = "";
  $("propertyDialogTitle").textContent = id ? "Edit property" : "Add property";

  if (id) {
    try {
      // The list does not include all photos, so ask for the full property
      const p = await apiRequest("/admin/properties/" + id);
      $("fTitle").value = p.title;
      $("fType").value = p.type;
      $("fPrice").value = p.price;
      $("fArea").value = p.area_sqft ?? "";
      $("fBedrooms").value = p.bedrooms ?? "";
      $("fCity").value = p.city;
      $("fAddress").value = p.address || "";
      $("fDescription").value = p.description || "";
      $("fImages").value = (p.images || []).join("\n");
    } catch (error) {
      showToast(error.message, true);
      return;
    }
  }
  updateBedroomsField();
  $("propertyDialog").showModal();
}

$("addBtn").addEventListener("click", () => openPropertyDialog());

$("propertyForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("propertyError").textContent = "";
  $("propertySave").disabled = true;

  // Collect the form values into one object for the server
  const body = {
    title: $("fTitle").value,
    type: $("fType").value,
    price: $("fPrice").value,
    area_sqft: $("fArea").value,
    bedrooms: $("fBedrooms").value,
    city: $("fCity").value,
    address: $("fAddress").value,
    description: $("fDescription").value,
    images: $("fImages").value.split("\n"),   // one link per line
  };

  try {
    if (editingId) {
      await apiRequest("/admin/properties/" + editingId, { method: "PUT", body });
      showToast("Property updated");
    } else {
      await apiRequest("/admin/properties", { method: "POST", body });
      showToast("Property added");
    }
    $("propertyDialog").close();
    loadProperties();
  } catch (error) {
    $("propertyError").textContent = error.message;
  } finally {
    $("propertySave").disabled = false;
  }
});

/* ------------------------------------------------------------------
   3. Mark sold pop-up (creates the buy record)
------------------------------------------------------------------ */
function openSoldDialog(id) {
  const property = allProperties.find((p) => p.id === id);
  soldId = id;
  $("soldForm").reset();
  $("soldError").textContent = "";
  $("soldTitle").textContent = property.title + " · listed at " + formatPrice(property.price);
  $("sPrice").value = property.price;       // start with the listed price
  $("soldDialog").showModal();
}

$("soldForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("soldError").textContent = "";
  $("soldSave").disabled = true;

  try {
    await apiRequest(`/admin/properties/${soldId}/status`, {
      method: "PATCH",
      body: {
        status: "sold",
        buyer_name: $("sName").value,
        buyer_email: $("sEmail").value,
        buyer_phone: $("sPhone").value,
        sale_price: $("sPrice").value,
      },
    });
    $("soldDialog").close();
    showToast("Marked as sold and sale recorded");
    loadProperties();
  } catch (error) {
    $("soldError").textContent = error.message;
  } finally {
    $("soldSave").disabled = false;
  }
});

/* ------------------------------------------------------------------
   4. Make available again / delete
------------------------------------------------------------------ */
async function makeAvailable(id) {
  if (!confirm("Make this property available again?\nIts sale record will be removed.")) return;
  try {
    await apiRequest(`/admin/properties/${id}/status`, { method: "PATCH", body: { status: "available" } });
    showToast("Marked as available");
    loadProperties();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function deleteProperty(id) {
  if (!confirm("Delete this property permanently?")) return;
  try {
    await apiRequest("/admin/properties/" + id, { method: "DELETE" });
    showToast("Property deleted");
    loadProperties();
  } catch (error) {
    showToast(error.message, true);   // e.g. sold properties cannot be deleted
  }
}

/* ------------------------------------------------------------------
   Start: load the table (and open the Add pop-up if the link had ?add=1)
------------------------------------------------------------------ */
loadProperties();
if (new URLSearchParams(window.location.search).get("add")) openPropertyDialog();
