// -------------------------------
// Listener for Gmail verification
// -------------------------------
document.querySelector(".send-btn").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Collect the values of input
  const gmailInput = document.querySelector("#gmail");

  if (!gmailInput.value.trim()) {
    gmailInput.style.border = "2px solid red";
  } else {
    gmailInput.style.border = "2px solid black";
    const gmail = gmailInput.value;
    axios
      .post(
        "/login_verify/",
        { gmail },
        { headers: { "Content-Type": "application/json" } }
      )
      .then((response) => {
        
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
});
