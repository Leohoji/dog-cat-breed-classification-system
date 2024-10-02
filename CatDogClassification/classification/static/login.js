// -------------------------------
// Listener for Signing up
// -------------------------------
document.querySelector(".signup a").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to sign_up page
  window.location.href = "/signup/";
});

// Listener for collecting the user data
document
  .querySelector(".login-btn")
  .addEventListener("click", function (event) {
    // Prevent the list send automatically
    event.preventDefault();

    // Collect the values of input
    const username = document.querySelector("#username").value;
    const password = document.querySelector("#password").value;

    // Apply AJAX technique to sen data to backend
    axios
      .post(
        "/login_verify/",
        { user_name: username, password: password },
        { headers: { "Content-Type": "application/json" } }
      )
      .then((response) => {
        const data = response.data;
        console.log(data);
        const status = data.status;

        // Check verification results
        if (status === "yes") {
          const username = data.USERNAME;
          window.location.href = `/upload/` + `${encodeURIComponent(username)}`; // URL redirection
        } else {
          const input_username = document.querySelector("#username");
          input_username.style.borderColor = "red";
          document.querySelector("#password").value = "";

          // response fail from backend using POST method
          if (data.message == "user not exists") {
            input_username.value = "user not exists";
          } else if (data.message == "wrong password") {
            input_username.value = "wrong password";
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
