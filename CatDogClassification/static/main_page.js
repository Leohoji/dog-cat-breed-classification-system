// -------------------------------
// Listener for Login
// -------------------------------
document.querySelector("#loginBtn").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to sign_up page
  window.location.href = "/login/";
});

// -------------------------------
// Listener for Signing up
// -------------------------------
document
  .querySelector("#signupBtn")
  .addEventListener("click", function (event) {
    // Prevent the list send automatically
    event.preventDefault();

    // Redirect to sign_up page
    window.location.href = "/signup/";
  });
