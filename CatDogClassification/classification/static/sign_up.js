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
  if (password.length < 8 || password.length > 12) {
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
    console.log("disabled");
  } else {
    inputElement.classList.remove("invalid");
    console.log("disabled remove");
  }
}

function resetPasswordValue(passwordHTML) {
  passwordHTML.addEventListener("click", function () {
    if (passwordHTML.type != "password") {
      passwordHTML.value = "";
      passwordHTML.type = "password";
    }
  });
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
document.querySelector("#signup-btn").addEventListener("click", );




// document.querySelector("#signup-btn").addEventListener("click", (event) => {
//   event.preventDefault();
//   let usernameInput = document.querySelector("#username");
//   let passwordValue = document.querySelector("#password");
//   let confirmPasswordValue = document.querySelector("#confirm-password");

//   const isValid = validateUsername(usernameInput.value).valid;
//   if (!isValid) {
//     console.log("username invalid");
//     usernameInput.classList.add("invalid");
//     usernameInput.value = "username invalid";
//   }

//   // Check password and confirm password
//   if (!passwordValue.value) {
//     passwordValue.type = "text";
//     passwordValue.value = "Please enter password";
//     return;
//   } else if (!confirmPasswordValue.value) {
//     confirmPasswordValue.type = "text";
//     confirmPasswordValue.value = "Please enter confirm password";
//     return;
//   } else if (passwordValue.value !== confirmPasswordValue.value) {
//     passwordValue.type = "text";
//     confirmPasswordValue.type = "text";
//     passwordValue.value = confirmPasswordValue.value = "Different Password !";
//     return;
//   }

// let disabled = document.querySelector("#signup-btn").disabled;
// if (!disabled) {
//   // Apply AJAX technique to sen data to backend
//   const userValue = username.value;
//   const userPassword = passwordValue.value;
//   fetch("/signUp_verify/", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ user_name: userValue, password: userPassword }),
//   })
//     .then((response) => {
//       if (response.redirected) {
//         console.log("Redirect...");
//         // response successfully from backend using POST method
//         // window.location.href = response.url;
//       } else {
//         console.log(response);
//         const fail_info = response.json();
//         username.value = `${fail_info.status}: ${fail_info.message}`;
//         return;
//       }
//     })
//     .then((data) => {
//       console.log("Success:", data);
//       return;
//     })
//     .catch((error) => {
//       console.error("Error:", error);
//     });
// }
// });
