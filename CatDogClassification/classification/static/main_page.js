// -------------------------------
// Listener for Login
// -------------------------------
document
  .querySelector("#login-btn")
  .addEventListener("click", function (event) {
    // Prevent the list send automatically
    event.preventDefault();

    // Redirect to sign_up page
    window.location.href = "/login/";
  });

// -------------------------------
// Listener for Signing up
// -------------------------------
document
  .querySelector("#sign-up-btn")
  .addEventListener("click", function (event) {
    // Prevent the list send automatically
    event.preventDefault();

    // Redirect to sign_up page
    window.location.href = "/signup/";
  });
