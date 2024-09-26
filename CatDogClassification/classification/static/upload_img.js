// Listener for login
document.querySelector(".logout a").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to login page
  window.location.href = "/login/";
});

// Listener for historical data checking
document.querySelector(".footer a").addEventListener("click", function (event) {
  // Prevent the list send automatically
  event.preventDefault();

  // Redirect to historical_data page
  window.location.href = "/historical_data/";
});

// Listener for image uploading
document
  .querySelector("#file-upload")
  .addEventListener("change", function (event) {
    // Collect the chosen file
    const file = event.target.files[0];
    console.log(file);
    if (file) {
      const reader = new FileReader();

      // 當讀取完成後執行的操作
      reader.onload = function (e) {
        // If image already exists, remove it
        let existingImage = document.querySelector("#uploaded-image");
        let existingDeleteButton = document.querySelector("#delete-button");
        let existingClassifyButton = document.getElementById("classify-button");
        if (existingImage) {
          existingImage.remove();
        }
        if (existingDeleteButton) {
          existingDeleteButton.remove();
        }
        if (existingClassifyButton) {
          existingClassifyButton.remove();
        }

        // Create img element to show image
        const img = document.createElement("img");
        img.id = "uploaded-image";
        img.src = e.target.result;
        img.style.maxWidth = "224px"; // control th width of image
        img.style.maxHeight = "224px";
        img.style.display = "block"; // Set as block element
        img.style.margin = "5px auto 10px auto"; // auto center

        // 創建一個容器來放置按鈕
        const buttonContainer = document.createElement("div");
        buttonContainer.style.display = "flex";
        buttonContainer.style.justifyContent = "center";
        buttonContainer.style.margin = "10px 0";

        // 創建刪除按鈕
        const deleteButton = document.createElement("button");
        deleteButton.id = "delete-button";
        deleteButton.textContent = "Delete Photo";
        deleteButton.style.backgroundColor = "#f44336";
        deleteButton.style.color = "white";
        deleteButton.style.border = "none";
        deleteButton.style.padding = "5px 10px";
        deleteButton.style.cursor = "pointer";
        deleteButton.style.marginRight = "10px"; // 添加右邊距

        // 創建 classify 按鈕
        const classifyButton = document.createElement("button");
        classifyButton.id = "classify-button";
        classifyButton.textContent = "Classify";
        classifyButton.style.backgroundColor = "#4CAF50";
        classifyButton.style.color = "white";
        classifyButton.style.border = "none";
        classifyButton.style.padding = "5px 10px";
        classifyButton.style.cursor = "pointer";

        // 將按鈕添加到容器中
        buttonContainer.appendChild(deleteButton);
        buttonContainer.appendChild(classifyButton);

        // 在這裡添加 classify 按鈕的功能
        classifyButton.addEventListener("click", function () {
          alert("Classifying the image..."); // 這裡可以加入分類的邏輯
        });

        // 刪除按鈕的事件監聽器
        deleteButton.addEventListener("click", function () {
          img.remove();
          buttonContainer.remove();
          document.querySelector("#file-upload").value = "";
        });

        // 插入元素
        const uploadContainer = document.querySelector(".upload-box");
        uploadContainer.insertBefore(img, uploadContainer.firstChild);
        uploadContainer.insertBefore(buttonContainer, img.nextSibling);
      };

      //   讀取圖片檔案為 Data URL
      reader.readAsDataURL(file);
    }
  });
