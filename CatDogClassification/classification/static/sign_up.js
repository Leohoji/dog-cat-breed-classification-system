// Listener for login
document.querySelector(".signin a").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to sign_up page
  window.location.href = "/login/";
});

// Function for format check of username creation
function validateUsername(username) {
  // Check if the username is at least 8 characters long
  // Check if the username contains at least one letter
  // Check if the username contains at least one number
  const hasLetter = /[a-zA-Z]/.test(username);
  const hasNumber = /\d/.test(username);
  if (username.length < 8 || !hasLetter || !hasNumber) {
    return { valid: false };
  }

  // If all conditions are satisfied, return valid
  return { valid: true };
}

// Check username first
document.querySelector("#username").addEventListener("input", () => {
  const usernameInput = document.querySelector("#username");
  const user_validated_result = validateUsername(usernameInput.value);
  if (!user_validated_result.valid) {
    usernameInput.classList.add("invalid");
  } else {
    usernameInput.classList.remove("invalid");
  }
});

// Listen the sign-up button
document.querySelector(".signup-btn").addEventListener("click", (event) => {
  // Prevent the list send automatically
  event.preventDefault();
  const username = document.querySelector("#username").value;
  const passwordValue = document.querySelector("#password").value;
  const confirmPasswordValue =
    document.querySelector("#confirm-password").value;
  // Check password and confirm password
  if (!passwordValue) {
    passwordValue = "Please enter password";
  } else if (!confirmPasswordValue) {
    confirmPasswordValue = "Please enter confirm password";
  } else if (passwordValue !== confirmPasswordValue) {
    passwordValue = confirmPasswordValue =
      "Password and confirm password are different !";
  }

  // Apply AJAX technique to sen data to backend
  fetch("/signUp_verify/", {
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
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});
