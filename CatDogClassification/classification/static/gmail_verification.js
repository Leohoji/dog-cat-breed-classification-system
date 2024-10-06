// -------------------------------
// Listener for Gmail verification
// -------------------------------
document.querySelector(".send-btn").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();
  document.querySelector(".send-btn").value = "Sending...";

  // Collect the values of input
  const gmailInputValue = document.querySelector("#gmail").value;

  if (gmailInputValue) {
    axios
      .post(
        "/send_code/",
        { gmail: gmailInputValue },
        { headers: { "Content-Type": "application/json" } }
      )
      .then((response) => {
        const verifiedData = response.data;
        const gmailCode = verifiedData.verification_code;
        console.log(gmailCode);

        // Simulate sending Gmail and moving to next step
        document.getElementById("gmail-section").style.display = "none";
        document.getElementById("verification-section").style.display = "block";

        document
          .getElementById("verify-btn")
          .addEventListener("click", function () {
            const verificationCode =
              document.getElementById("verification").value;

            // Perform verification code check (this is usually done on the server)
            if (Number(verificationCode) === gmailCode) {
              swal("Good", "Verification successful!", "success").then(
                () => {}
              );
            } else {
              swal("Warning", "Invalid verification code.", "warning");
            }
          });
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    swal("Gmail is empty", "Please enter your Gmail account.", "warning");
    return;
  }
});
