/* login.js - sends the username and password to the server */

// Already logged in? skip the login page
if (getToken()) window.location.href = "dashboard.html";

const form = document.getElementById("loginForm");
const errorBox = document.getElementById("error");
const button = document.getElementById("loginBtn");

form.addEventListener("submit", async (event) => {
  event.preventDefault();          // stop the page from reloading
  errorBox.textContent = "";
  button.disabled = true;
  button.textContent = "Signing in...";

  try {
    const result = await apiRequest("/admin/login", {
      method: "POST",
      auth: false,                 // we have no token yet
      body: {
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
      },
    });
    saveLogin(result.token, result.username);
    window.location.href = "dashboard.html";
  } catch (error) {
    errorBox.textContent = error.message;
    button.disabled = false;
    button.textContent = "Log in";
  }
});
