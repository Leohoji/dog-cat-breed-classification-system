// -------------------------------
// Listener for Gmail verification
// -------------------------------
let VerifiedCode;

document
  .querySelector("#send-gmail-btn")
  .addEventListener("click", function (event) {
    // Prevent the list send automatically
    event.preventDefault();

    // Username verification
    const username = document.querySelector("#username").value;
    axios
      .post(
        "/user_verify/",
        { user_name: username },
        { headers: { "Content-Type": "application/json" } }
      )
      .then((response) => {
        const status = response.data.status;
        console.log(status);
        // Check verification results
        if (status !== "yes") {
          swal("Warning", "Invalid User Account", "warning");
          return;
        } else {
          // Disable the send button to prevent multiple requests
          const sendButton = document.querySelector("#send-gmail-btn");
          sendButton.innerText = "Sending...";
          sendButton.disabled = true; // Disable the button

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
                VerifiedCode = verifiedData.verification_code;
                console.log("correct code", VerifiedCode);

                // Simulate sending Gmail and moving to next step
                document.getElementById("gmail-section").style.display = "none";
                document.getElementById("verification-section").style.display =
                  "block";

                // Logic to resend the code
                document
                  .getElementById("resend-link")
                  .addEventListener("click", async function () {
                    VerifiedCode = await resendCode(gmailInputValue);
                    console.log("correct code", VerifiedCode);
                  });

                document
                  .getElementById("verify-btn")
                  .addEventListener("click", function () {
                    const verificationCode =
                      document.getElementById("verification").value;

                    console.log("correct code", VerifiedCode);

                    // Perform verification code check (this is usually done on the server)
                    if (Number(verificationCode) === VerifiedCode) {
                      swal("Good", "Verification successful!", "success").then(
                        () => {
                          window.location.href = `/pasReset/${username}`;
                        }
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
            swal(
              "Gmail is empty",
              "Please enter your Gmail account.",
              "warning"
            );
            return;
          }
        }
      });
  });

// -------------------------------
// Logic to resend the code
// -------------------------------
async function resendCode(gmail) {
  const resendLink = document.querySelector("#resend-link");
  resendLink.innerText = "Resending...";

  try {
    const response = await axios.post(
      "/send_code/",
      { gmail: gmail },
      { headers: { "Content-Type": "application/json" } }
    );
    const verifiedData = response.data;
    const gmailCode = verifiedData.verification_code;
    console.log("New Code:", gmailCode);

    // Show a message that the code was resent
    swal("Code Resent", "A new verification code has been sent.", "success");

    // Reset the resend button text
    resendLink.innerText = "Send again";

    return gmailCode;
  } catch (error) {
    console.error("Error:", error);
    swal("Error", "Failed to resend verification code.", "error");

    // Reset the resend button text even in case of error
    resendLink.innerText = "Send again";

    return null; // Return null if there was an error
  }
}
