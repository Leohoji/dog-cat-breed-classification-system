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
    fetch("/login_verify/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_name: username, password: password }),
    })
      .then((response) => {
        if (response.redirected) {
          // response successfully from backend using POST method
          window.location.href = response.url;
        } else {
          return response.json();
        }
      })
      .then((data) => {
        console.log("Success:", data);
        let input_username = document.querySelector("#username");
        document.querySelector("#password").value = "";

        // response fail from backend using POST method
        if (data.message == "user not exists") {
          input_username.value = "user not exists";
        } else if (data.message == "wrong password") {
          input_username.value = "wrong password";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });

// Listener for Signing up
document
  .querySelector(".signup a")
  .addEventListener("click", function (event) {
    // Prevent the list send automatically
    event.preventDefault();

    // Redirect to sign_up page
    window.location.href = "/signup/";
  });
