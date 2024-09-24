// Listener for login
document.querySelector(".signin a").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to sign_up page
  window.location.href = "/login/";
});


// Listener for input values
const usernameInput = document.querySelector("#username");
const passwordInput = document.querySelector("#password");
const confirmPasswordInput = document.querySelector("#confirm-password");
const signupBtn = document.querySelector(".signup-btn");

// Function for format check of username creation
function validateUsername(username) {
  // Check if the username is at least 8 characters long
  // Check if the username contains at least one letter
  // Check if the username contains at least one number
  const hasLetter = /[a-zA-Z]/.test(username);
  const hasNumber = /\d/.test(username);
  if ((username.length < 8) | !hasLetter | !hasNumber) {
    return { valid: false };
  }

  // If all conditions are satisfied, return valid
  return { valid: true };
}

// Check username first
usernameInput.addEventListener('input', () => {
    usernameValue = usernameInput.value;
    const user_validated_result = validateUsername(usernameValue);
    if (!user_validated_result.valid) {
      usernameInput.classList.add("invalid");
    } else {
      usernameInput.classList.remove("invalid");
    }
})

signupBtn.addEventListener;('click', () => {
  const passwordValue = passwordInput.value;
  const confirmPasswordValue = confirmPasswordInput.value;

  // Check password and confirm password
  if (!passwordValue) {
    passwordValue = "Please enter password";
    return;
  } else if (!confirmPasswordValue) {
    confirmPasswordValue = "Please enter confirm password";
    return;
  } else if (passwordValue !== confirmPasswordValue) {
    passwordValue = confirmPasswordValue =
      "Password and confirm password are different !";
    return;
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
})