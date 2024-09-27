// -------------------------------
// Listener for login
// -------------------------------
document.querySelector(".logout a").addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the list send automatically
  window.location.href = "/login/"; // Redirect to login page
});

// -------------------------------
// Listener for historical data checking
// -------------------------------
document.querySelector(".footer a").addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the list send automatically
  window.location.href = "/historical_data/"; // Redirect to historical_data page
});

function removeEleIfExists(idTag) {
  /* 
  Remove element if it exists. 
  @param {idTag}: Attribute of HTML element tag, it must be id
  */
  let existingElement = document.querySelector(`#${idTag}`);
  if (existingElement) {
    existingElement.remove();
  }
}

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
  buttonElement.style.border = "none";
  buttonElement.style.padding = "5px 10px";
  buttonElement.style.cursor = "pointer";

  return buttonElement;
}

function createDeleteClassifyButton() {
  const buttonContainer = document.createElement("div");
  buttonContainer.style.display = "flex";
  buttonContainer.style.justifyContent = "center";
  buttonContainer.style.margin = "10px 0";
  const deleteButton = createButtonEle(
    "delete-button",
    "Delete Photo",
    "#f44336"
  );
  deleteButton.style.marginRight = "10px"; // right margin
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
    // const fileInput = document.querySelector("#file-upload");
    // console.log(file);
    if (file) {
      const reader = new FileReader();

      // Actions after image reading
      reader.onload = function (e) {
        const base64Data = reader.result;
        const name = file.name;
        const type = file.type;
        const size = file.size;

        // If image already exists, remove it
        removeEleIfExists("uploaded-image");
        removeEleIfExists("delete-button");
        removeEleIfExists("classify-button");

        // Create img element to show image
        const img = document.createElement("img");
        img.id = "uploaded-image";
        img.src = e.target.result;
        img.style.maxWidth = "224px"; // control th width of image
        img.style.maxHeight = "224px";
        img.style.display = "block"; // Set as block element
        img.style.margin = "5px auto 10px auto"; // auto center

        // -------------------------------
        // Create a div element to collect
        // delete and classify button
        // -------------------------------
        const { buttonContainer, deleteButton, classifyButton } =
          createDeleteClassifyButton();

        // 在這裡添加 classify 按鈕的功能
        classifyButton.addEventListener("click", function () {
          const imageObject = { name, type, size, base64Data };
          const jsonData = JSON.stringify(imageObject);
          console.log(jsonData);
          toggleButtonState(classifyButton, false); // 禁用分類按鈕
          classifyButton.textContent = "Predicting...";
          // alert("Classifying the image..."); // 這裡可以加入分類的邏輯
        });

        // Delete listener for delete event
        deleteButton.addEventListener("click", function () {
          img.remove();
          buttonContainer.remove();
          document.querySelector("#file-upload").value = "";
        });

        // Insert elements created before
        const uploadContainer = document.querySelector(".upload-box");
        uploadContainer.insertBefore(img, uploadContainer.firstChild);
        uploadContainer.insertBefore(buttonContainer, img.nextSibling);
      };
      reader.readAsDataURL(file); // Read image as data URL
    }
  });
