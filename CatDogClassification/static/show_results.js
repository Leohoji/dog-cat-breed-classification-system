// -------------------------------
// Listener for back upload image
// -------------------------------
const username = document.querySelector("#user-account").innerText;
document.querySelector(".back-button").addEventListener("click", () => {
  window.location.href = `/upload/${encodeURIComponent(username)}`; // Redirect to upload page
});

function validationSelection(breedCheck, breedSelect) {
  /*
  Check classification feedback (yes or no) and breed selection (if selection is no)
  @param {breedCheck}: button for classification feedback
  @param {breedSelect}: dropdown menu value for breed selection
  @return {boolean: true or false}
  */
  if (breedCheck.value === "no" && !breedSelect.value) {
    optionsContainer.style.border = "2px solid red"; // set border as red
    errorMessage.style.display = "block"; // display error message
    return false;
  }
  return true;
}

// -------------------------------
// Listener for selection display
// -------------------------------
const breedRadioButtons = document.querySelectorAll('input[name="breed"]');
const breedSelect = document.querySelector(".breed-select");
const optionsContainer = document.querySelector(".options"); // option container
const errorMessage = document.querySelector(".error-message"); // error message

// Clear all the error style before submitting selection
breedRadioButtons.forEach((radio) => {
  radio.addEventListener("change", function () {
    if (this.value === "no") {
      breedSelect.style.display = "block";
      optionsContainer.style.border = "none";
      errorMessage.style.display = "none";
    } else {
      breedSelect.style.display = "none";
      breedSelect.value = "";
      optionsContainer.style.border = "none";
      errorMessage.style.display = "none";
    }
  });
});

breedSelect.addEventListener("change", function () {
  if (this.value) {
    optionsContainer.style.border = "none";
    errorMessage.style.display = "none";
  }
});

// -------------------------------
// Listener for data checking
// -------------------------------
document.querySelector(".save-data").addEventListener("click", function () {
  const breedSelect = document.querySelector(".breed-select");
  const breedCheck = document.querySelector('input[name="breed"]:checked');
  checkValidated = validationSelection(breedCheck, breedSelect); // validation and error display

  // Get values of radio if checked and dropout
  if (checkValidated) {
    // Save yes or no choice and real breed
    const originalBreed = document.querySelector("#original-class");
    const breedRadioButtons = document.querySelectorAll('input[name="breed"]');
    let selectedBreed;
    let breedChoice;
    breedRadioButtons.forEach((radio) => {
      if (radio.checked) {
        breedChoice = radio.value;
        if (breedChoice === "no") {
          selectedBreed = breedSelect.value; // Get value of dropdown menu
        } else {
          selectedBreed = originalBreed.innerText;
        }
      }
    });

    swal(
      "Thanks For Your Feedback!",
      "Go back to upload page!",
      "success"
    ).then(() => {
      // Save classification results to database ...
      const feedback = { breedChoice, selectedBreed };
      axios
        .post(
          "/save_data/",
          { username, feedback },
          { headers: { "Content-Type": "application/json" } }
        )
        .then(
          () => {
            window.location.href = `/upload/${encodeURIComponent(username)}`;
          } // Redirect to upload page});
        );
      console.log(
        `Breed Choice (Yes/No): ${breedChoice} | Selected Breed: ${selectedBreed}`
      );
    });
  }
});
