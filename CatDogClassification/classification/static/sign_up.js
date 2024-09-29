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

function resetPasswordValue(passwordHTML) {
  passwordHTML.addEventListener("click", () => {
    if (passwordHTML.type != "password") {
      passwordHTML.value = "";
      passwordHTML.type = "password";
    }
  });
}

// Listen the sign-up button
document.querySelector(".signup-btn").addEventListener("click", (event) => {
  // Prevent the list send automatically
  event.preventDefault();
  let username = document.querySelector("#username");
  let passwordValue = document.querySelector("#password");
  let confirmPasswordValue = document.querySelector("#confirm-password");

  if (!validateUsername(username.value).valid) {
    username.value = "Invalid User Format !";
    usernameInput.classList.add("invalid");
  }
  resetPasswordValue(passwordValue);
  resetPasswordValue(confirmPasswordValue);

  // Check password and confirm password
  if (!passwordValue.value) {
    passwordValue.type = "text";
    passwordValue.value = "Please enter password";
    return;
  } else if (!confirmPasswordValue.value) {
    confirmPasswordValue.type = "text";
    confirmPasswordValue.value = "Please enter confirm password";
    return;
  } else if (passwordValue.value !== confirmPasswordValue.value) {
    passwordValue.type = "text";
    confirmPasswordValue.type = "text";
    passwordValue.value = confirmPasswordValue.value = "Different Password !";
    return;
  }

  // Apply AJAX technique to sen data to backend
  const userValue = username.value;
  const userPassword = passwordValue.value;
  fetch("/signUp_verify/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_name: userValue, password: userPassword }),
  })
    .then((response) => {
      if (response.redirected) {
        console.log("Redirect...");
        // response successfully from backend using POST method
        window.location.href = response.url;
      } else {
        console.log(response);
        const fail_info = response.json();
        username.value = `${fail_info.status}: ${fail_info.message}`;
        return;
      }
    })
    .then((data) => {
      console.log("Success:", data);
      return;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});
