// -------------------------------
// Listener for login
// -------------------------------
document.querySelector(".logout").addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the list send automatically
  window.location.href = "/login/"; // Redirect to login page
});

// -------------------------------
// For user account verification
// -------------------------------
const username = document
  .querySelector("#user-name")
  .innerText.replace("User name: ", "");

// -------------------------------
// Listener for upload page
// -------------------------------
document.querySelector(".back-button").addEventListener("click", () => {
  window.location.href = `/upload/${encodeURIComponent(username)}`; // Redirect to upload page
});
