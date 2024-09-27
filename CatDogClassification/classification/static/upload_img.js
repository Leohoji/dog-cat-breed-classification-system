// -------------------------------
// Listener for login
// -------------------------------
document.querySelector(".logout a").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to login page
  window.location.href = "/login/";
});

// -------------------------------
// Listener for historical data checking
// -------------------------------
document.querySelector(".footer a").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to historical_data page
  window.location.href = "/historical_data/";
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

function createButtonEle(
  id,
  textContent,
  backgroundColor,
  color,
  border,
  padding,
  cursor
) {
  const buttonElement = document.createElement("button");
  deleteButton.id = id;
  deleteButton.textContent = textContent;
  deleteButton.style.backgroundColor = backgroundColor;
  deleteButton.style.color = color;
  deleteButton.style.border = border;
  deleteButton.style.padding = padding;
  deleteButton.style.cursor = cursor;

  return buttonElement;
}

// -------------------------------
// Listener for image uploading
// -------------------------------
document
  .querySelector("#file-upload")
  .addEventListener("change", function (event) {
    // Collect the chosen file
    const file = event.target.files[0];
    console.log(file);
    if (file) {
      const reader = new FileReader();

      // Actions after image reading
      reader.onload = function (e) {
        const imagePath = fileInput.value;
        console.log("Image path:", imagePath);

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
        const buttonContainer = document.createElement("div");
        buttonContainer.style.display = "flex";
        buttonContainer.style.justifyContent = "center";
        buttonContainer.style.margin = "10px 0";

        // Create delete button
        const deleteButton = createButtonEle(
          (id = "delete-button"),
          (textContent = "Delete Photo"),
          (backgroundColor = "#f44336"),
          (color = "white"),
          (border = "none"),
          (padding = "5px 10px"),
          (cursor = "pointer")
        );
        deleteButton.style.marginRight = "10px"; // right margin

        // Create classify button
        const classifyButton = createButtonEle(
          (id = "classify-button"),
          (textContent = "Classify"),
          (backgroundColor = "#4CAF50"),
          (color = "white"),
          (border = "none"),
          (padding = "5px 10px"),
          (cursor = "pointer")
        );

        // Append buttons to div container
        buttonContainer.appendChild(deleteButton);
        buttonContainer.appendChild(classifyButton);

        // 在這裡添加 classify 按鈕的功能
        classifyButton.addEventListener("click", function () {
          alert("Classifying the image..."); // 這裡可以加入分類的邏輯
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

      // Read image as data URL
      reader.readAsDataURL(file);
    }
  });
