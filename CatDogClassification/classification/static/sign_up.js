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
  const hasLetter = /[a-zA-Z]/.test(username); // at least one letter
  const hasNumber = /\d/.test(username); // at least one number
  if (username.length < 8 || !hasLetter || !hasNumber) {
    return { valid: false };
  }
  return { valid: true }; // All conditions are satisfied
}

function validatePasswords(password) {
  if (password.length < 8) {
    return { valid: false };
  }
  return { valid: true };
}

function validateInput(inputElement, validateFunction) {
  const isValid = validateFunction(inputElement.value).valid;
  let signupBtn = document.querySelector("#signup-btn");

  signupBtn.disabled = !isValid; // Able or disable signup button based on valid result
  if (!isValid) {
    inputElement.classList.add("invalid");
  } else {
    inputElement.classList.remove("invalid");
  }
}

// ----------------------------
// 1. check input format first
// ----------------------------

// check username format
document.querySelector("#username").addEventListener("input", (event) => {
  validateInput(event.target, validateUsername);
});

// check password format
document.querySelector("#password").addEventListener("input", (event) => {
  validateInput(event.target, validatePasswords);
});

// check confirm password format
document
  .querySelector("#confirm-password")
  .addEventListener("input", (event) => {
    validateInput(event.target, validatePasswords);
  });

// ----------------------------
// 2. check signup button event
// ----------------------------
document.querySelector("#signup-btn").addEventListener("click", (event) => {
  event.preventDefault();
  let usernameInput = document.querySelector("#username");
  let passwordInput = document.querySelector("#password");
  let confirmPasswordInput = document.querySelector("#confirm-password");

  // validation again
  const userValid = validateUsername(usernameInput.value).valid;
  const passwordValid = validatePasswords(passwordInput.value).valid;
  const confirmValid = validatePasswords(confirmPasswordInput.value).valid;
  const passwordsMatch = passwordInput.value === confirmPasswordInput.value;

  btnInfo = { button: "Click Me!" };

  // Check validation and show alerts using switch
  switch (true) {
    case !userValid:
      usernameInput.value = "";
      swal(
        "Invalid Username!",
        "8-12 characters long including at least a letter and a number.",
        "warning",
        btnInfo
      );
      break;
    case !passwordValid:
      passwordInput.value = "";
      swal("Invalid Password!", "8-12 characters long.", "warning", btnInfo);
      break;
    case !confirmValid:
      confirmPasswordInput.value = "";
      swal(
        "Invalid Confirm Password!",
        "8-12 characters long.",
        "warning",
        btnInfo
      );
      break;
    case !passwordsMatch:
      passwordInput.value = "";
      confirmPasswordInput.value = "";
      swal("Something Error!", "Passwords do not match!", "warning");
      break;
    default:
      // -------------------------------------------------
      // 3.  Apply AJAX technique to send data to backend
      // -------------------------------------------------
      const userValue = usernameInput.value;
      const userPassword = passwordInput.value;

      return fetch("/signUp_verify/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_name: userValue,
          user_password: userPassword,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          // convert response into JSON format
          return response.json();
        })
        .then((data) => {
          console.log(data);
          const { status, message, redirect_url } = data;
          if (status === "success") {
            swal("Good! Go To Login!", `${message}`, "success").then(() => {
              window.location.href = redirect_url;
            });
          } else {
            swal("Error!", `${message}`, "error");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
  }
});
