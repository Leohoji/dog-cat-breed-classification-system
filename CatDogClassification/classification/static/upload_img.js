// -------------------------------
// Listener for login
// -------------------------------
document.querySelector(".logout a").addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the list send automatically
  window.location.href = "/login/"; // Redirect to login page
});

// -------------------------------
// For user account verification
// -------------------------------
const username = document.querySelector("#user-account").innerText;

// -------------------------------
// Listener for historical data checking
// -------------------------------
document.querySelector(".footer a").addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the list send automatically
  window.location.href = `/historical_data/${encodeURIComponent(username)}`; // Redirect to historical_data page
});

function createButtonEle(id, textContent, backgroundColor) {
  /*
  Create button element for HTML generation.
  @param {id}: Id attribute for button HTML tag
  @param {textContent}: Text Content for button HTML tag
  @param {backgroundColor}: BackgroundColor for button HTML tag
  @return {button element}
  */
  const buttonElement = document.createElement("button");
  buttonElement.id = id;
  buttonElement.textContent = textContent;
  buttonElement.style.backgroundColor = backgroundColor;
  buttonElement.style.color = "white";
  buttonElement.style.border = "2px solid transparent"; // default border transparent
  buttonElement.style.borderRadius = "5px"; // rounded corners
  buttonElement.style.padding = "5px 10px";
  buttonElement.style.cursor = "pointer";
  buttonElement.style.boxShadow = "0 2px 3px rgba(0, 0, 0, 0.1)"; // add shadow

  return buttonElement;
}

function createDeleteClassifyButton() {
  const buttonContainer = document.createElement("div");
  buttonContainer.id = "button-container";
  buttonContainer.style.display = "flex";
  buttonContainer.style.justifyContent = "center";
  buttonContainer.style.margin = "10px 0";
  const deleteButton = createButtonEle(
    "delete-button",
    "Delete Photo",
    "#f44336"
  );
  deleteButton.style.marginRight = "20px"; // right margin
  const classifyButton = createButtonEle(
    "classify-button",
    "Classify",
    "#4CAF50"
  );

  // Append buttons to div container
  buttonContainer.appendChild(deleteButton);
  buttonContainer.appendChild(classifyButton);

  return { buttonContainer, deleteButton, classifyButton };
}

function createImgDisplay(src) {
  /* 
  Create element for image display. 
  @param {src}: Image source
  */
  const img = document.createElement("img");
  img.id = "uploaded-image";
  img.src = src;
  img.style.maxWidth = "224"; // control th width of image
  img.style.maxHeight = "224px";
  img.style.display = "block"; // Set as block element
  img.style.margin = "5px auto 10px auto"; // auto center

  return img;
}

function createFileNameDisplay(fileName) {
  // Create element for fine name display
  const fileNameDisplay = document.createElement("div");
  fileNameDisplay.textContent = `File: ${fileName}`;
  fileNameDisplay.id = "upload-file-name";
  fileNameDisplay.style.marginBottom = "10px"; // margin bottom
  fileNameDisplay.style.padding = "2px"; // padding
  fileNameDisplay.style.border = "1px solid #4CAF50"; // border
  fileNameDisplay.style.borderRadius = "5px"; // radius
  fileNameDisplay.style.backgroundColor = "#f9f9f9"; // background color
  fileNameDisplay.style.boxShadow = "0 2px 5px rgba(0, 0, 0, 0.2)"; // box shadow
  fileNameDisplay.style.maxWidth = "240px"; // same width as img element
  fileNameDisplay.style.margin = "0 auto"; // margin automatically

  return fileNameDisplay;
}

function toggleButtonState(button, isEnabled) {
  button.disabled = !isEnabled;
  button.style.opacity = isEnabled ? "1" : "0.5";
}

// -------------------------------
// Listener for image uploading
// -------------------------------
document
  .querySelector("#file-upload")
  .addEventListener("change", function (event) {
    const file = event.target.files[0]; // collect the chosen file
    if (file) {
      const reader = new FileReader();

      // Actions after image reading
      reader.onload = function (e) {
        const fileName = file.name;
        const base64Data = reader.result;
        const img = createImgDisplay(e.target.result); // Create img element to show image
        const fileNameDisplay = createFileNameDisplay(fileName); // Create element for fine name display
        const { buttonContainer, deleteButton, classifyButton } =
          createDeleteClassifyButton(); // Create a delete and classify button

        // Insert elements created before
        const uploadContainer = document.querySelector(".upload-box");
        uploadContainer.insertBefore(img, uploadContainer.firstChild);
        uploadContainer.insertBefore(buttonContainer, img.nextSibling);
        uploadContainer.insertBefore(
          fileNameDisplay,
          uploadContainer.firstChild
        );

        // Delete listener for delete event
        deleteButton.addEventListener("click", function () {
          img.remove();
          buttonContainer.remove();
          fileNameDisplay.remove();
          document.querySelector("#file-upload").value = "";
        });

        // classify listener for image classification
        classifyButton.addEventListener("click", function () {
          toggleButtonState(classifyButton, false); // disabled button
          classifyButton.textContent = "Predicting...";

          // --------------------
          // image classification
          // --------------------
          axios
            .post(
              "/imgCls/",
              { image: base64Data },
              { headers: { "Content-Type": "application/json" } }
            )
            .then(function (response) {
              const data = response.data;
              console.log(data);
              const status = data.status;
              if (status === "ok") {
                const species = data.species;
                const modelPred = data.model_pred;

                // URL redirection --> to show_results
                window.location.href =
                  `/show_results/` +
                  `${encodeURIComponent(species)}&` +
                  `${encodeURIComponent(modelPred)}&` +
                  `${encodeURIComponent(username)}`;
              } else {
                const errorInfo = data.message;
                swal("Error!", `${errorInfo}`, "error");
              }
            })
            .catch(function (error) {
              console.log("Error: ", error);
            });
        });
      };
      reader.readAsDataURL(file); // Read image as data URL
    }
  });
