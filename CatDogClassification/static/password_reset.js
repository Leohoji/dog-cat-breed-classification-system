function validatePasswords(password) {
  if (password.length < 8) {
    return { valid: false };
  }
  return { valid: true };
}

// ---------------------------------
// Listener for submit new password
// ---------------------------------
document.querySelector("#reset-btn").addEventListener("click", (event) => {
  event.preventDefault();
  let newPasswordInput = document.querySelector("#new-password");
  let newConfirmPasswordInput = document.querySelector("#new-confirm-password");

  // validation new password
  const passwordValid = validatePasswords(newPasswordInput.value).valid;
  const confirmValid = validatePasswords(newConfirmPasswordInput.value).valid;
  const passwordsMatch =
    newPasswordInput.value === newConfirmPasswordInput.value;

  const btnInfo = { button: "Click Me!" };
  const characterInvalidInfo = "8-12 characters long.";

  // Check validation and show alerts using switch
  switch (true) {
    case !passwordValid || !confirmValid:
      newPasswordInput.value = "";
      swal("Invalid Password!", characterInvalidInfo, "warning", btnInfo);
      break;
    case !passwordsMatch:
      newPasswordInput.value = "";
      newConfirmPasswordInput.value = "";
      swal("Something Error!", "Passwords do not match!", "warning");
      break;
    default:
      // -------------------------------------------------
      // Apply AJAX technique to send data to backend
      // -------------------------------------------------
      const username = document.querySelector("#user-account").innerText;
      const newUserPassword = newPasswordInput.value;

      return axios
        .post(
          "/update/",
          { username, newUserPassword },
          { headers: { "Content-Type": "application/json" } }
        )
        .then((response) => {
          const result = response.data.result;
          console.log(result);
          if (result === "success") {
            swal("Good! Go To Login!", `${result}`, "success").then(() => {
              window.location.href = "/login/";
            });
          } else {
            swal("Error!", `${result}`, "error");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
  }
});
