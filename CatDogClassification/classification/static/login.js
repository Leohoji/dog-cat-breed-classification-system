// Collect the user data
document
  .querySelector(".login-btn")
  .addEventListener("click", function (event) {
    // Prevent the list send automatically
    event.preventDefault();

    // Collect the values of input
    const username = document.querySelector("#username").value;
    const password = document.querySelector("#password").value;

    // Apply AJAX technique to sen data to backend
    fetch("/verify/", {
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
      .then((data) => {console.log("Success:", data);})
      .catch((error) => {
        console.error("Error:", error);
      });
  });
