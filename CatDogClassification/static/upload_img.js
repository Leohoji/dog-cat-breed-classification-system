// -------------------------------
// Listener for login
// -------------------------------
document.querySelector(".logout a").addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the list send automatically
  window.location.href = "/"; // Redirect to login page
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
  const page = 1;
  window.location.href =
    `/historical_data/` +
    `${encodeURIComponent(username)}&` +
    `cur_page=${encodeURIComponent(page)}`; // Redirect to historical_data page
});

// DOM Elements
const fileInput = document.getElementById("fileInput");
const uploadBox = document.getElementById("uploadBox");
const analyzeBtn = document.getElementById("analyzeBtn");

// Constants
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB in bytes
const ALLOWED_TYPES = ["image/jpeg", "image/png"];

let currentFile = null;

// File validation and handling
function handleFile(file) {
  // Validate file type
  if (!ALLOWED_TYPES.includes(file.type)) {
    swal("Invalid File Type", "Please upload only JPG or PNG images.", "error");
    return;
  }

  // Validate file size
  if (file.size > MAX_FILE_SIZE) {
    swal("File Too Large", "File size must be less than 5MB.", "error");
    return;
  }

  // Show preview
  displayPreview(file);
}

// Display image preview
function displayPreview(file) {
  const reader = new FileReader();

  reader.onload = (e) => {
    // Reset current file
    currentFile = null;

    // Create preview elements
    const previewContainer = document.createElement("div");
    previewContainer.className = "preview-container";

    const previewImage = document.createElement("img");
    previewImage.src = e.target.result;
    previewImage.style.maxWidth = "300px";
    previewImage.style.maxHeight = "300px";
    previewImage.style.margin = "0px";

    const fileName = document.createElement("div");
    fileName.textContent = file.name;
    fileName.style.fontSize = "14px";
    fileName.style.color = "#666";

    // Clear upload box content
    uploadBox.innerHTML = "";

    // Add preview elements
    previewContainer.appendChild(previewImage);
    previewContainer.appendChild(fileName);
    uploadBox.appendChild(previewContainer);

    // Store the valid file
    currentFile = reader.result;
  };

  reader.readAsDataURL(file);
}

// ========== Main program ==========
// Add drag and drop event listeners
uploadBox.addEventListener("dragover", (e) => {
  e.preventDefault();
  e.stopPropagation();
  uploadBox.style.borderColor = "#4a6baf";
});

uploadBox.addEventListener("dragleave", (e) => {
  e.preventDefault();
  e.stopPropagation();
  uploadBox.style.borderColor = "#d0d7e6";
});

uploadBox.addEventListener("drop", (e) => {
  e.preventDefault();
  e.stopPropagation();
  uploadBox.style.borderColor = "#d0d7e6";

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFile(files[0]);
  }
});

// Handle file input change
fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFile(e.target.files[0]);
  }
});

analyzeBtn.addEventListener("click", async () => {
  // Check if a file has been selected
  if (!currentFile) {
    swal("No File Selected", "Please upload an image first.", "warning");
    return;
  }

  // Function to handle button state updates
  const updateButtonState = (isProcessing = true) => {
    analyzeBtn.disabled = isProcessing;
    analyzeBtn.textContent = isProcessing
      ? "Processing..."
      : "Start Recognition";

    if (isProcessing) {
      analyzeBtn.style.backgroundColor = "#cccccc";
      analyzeBtn.style.cursor = "not-allowed";
    } else {
      analyzeBtn.style.backgroundColor = "#4a6baf";
      analyzeBtn.style.cursor = "pointer";
    }
  };

  // Function to validate input data
  const validateData = (base64Data, username) => {
    if (!base64Data) {
      throw new Error("Image data is missing");
    }
    if (!username) {
      throw new Error("Username is required");
    }
  };

  // Function to handle redirection with results
  const redirectToResults = (species, modelPred, username) => {
    const params = [
      encodeURIComponent(species),
      encodeURIComponent(modelPred),
      encodeURIComponent(username),
    ].join("&");

    window.location.href = `/show_results/${params}`;
  };

  try {
    // Validate the input data before processing
    validateData(currentFile, username);

    // Update button state to processing
    updateButtonState(true);

    // Send request to backend API
    const response = await axios.post(
      "/imgCls/",
      { image: currentFile },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    // Log successful response for debugging
    console.log("Server response:", response.data);

    // Handle response based on status
    if (response.data.status === "ok") {
      const { status, species, model_pred } = response.data;
      redirectToResults(species, model_pred, username);
    } else {
      // If status is not OK, handle as a backend error
      console.error("Backend error:", response.data.message);
      swal("Processing Error", response.data.message, "error");
    }
  } catch (error) {
    // Handle different types of errors
    if (error.response) {
      // Backend returned an error response (status code outside 2xx)
      console.error("Backend error response:", {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
      });

      // Show user-friendly message from backend if available
      const errorMessage =
        error.response.data.message || "Server processing error";
      swal("Server Error", errorMessage, "error");
    } else if (error.request) {
      // Request was made but no response received
      console.error("Network error:", error.request);
      swal(
        "Network Error",
        "Unable to connect to the server. Please check your internet connection.",
        "error"
      );
    } else {
      // Error occurred during request setup
      console.error("Request setup error:", error.message);
      swal(
        "Error",
        "An error occurred while preparing your request. Please try again.",
        "error"
      );
    }
  } finally {
    // Reset button state regardless of outcome
    updateButtonState(false);
  }
});
