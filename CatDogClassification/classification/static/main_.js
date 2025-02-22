document.addEventListener("DOMContentLoaded", function () {
  const loginBtn = document.querySelector("#loginBtn");
  const signupBtn = document.querySelector("#signupBtn");
  const uploadSection = document.querySelector("#uploadSection");
  const uploadBox = document.querySelector("#uploadBox");
  const fileInput = document.querySelector("#fileInput");
  const analyzeBtn = document.querySelector("#analyzeBtn");

  // 定義啟用上傳功能的函數
  function enableUpload() {
    // 啟用上傳區域
    uploadSection.classList.add("active");
    uploadBox.classList.add("active");

    // 啟用檔案上傳
    fileInput.disabled = false;

    // 啟用分析按鈕
    analyzeBtn.disabled = false;
    analyzeBtn.classList.add("active");

    // 添加上傳框點擊事件
    uploadBox.onclick = function () {
      fileInput.click();
    };
  }

  // 定義禁用上傳功能的函數
  function disableUpload() {
    // 禁用上傳區域
    uploadSection.classList.remove("active");
    uploadBox.classList.remove("active");

    // 禁用檔案上傳
    fileInput.disabled = true;

    // 禁用分析按鈕
    analyzeBtn.disabled = true;
    analyzeBtn.classList.remove("active");

    // 移除上傳框點擊事件
    uploadBox.onclick = null;

    // 清除已選擇的文件
    fileInput.value = "";
  }

  // 處理登入按鈕點擊
  loginBtn.addEventListener("click", function () {
    window.location.href = "/login/";
  });

  // 處理註冊按鈕點擊
  signupBtn.addEventListener("click", function () {
    window.location.href = "/signup/";
  });

  // 檢查是否已登入（這裡需要根據你的實際登入狀態判斷邏輯來實現）
  function checkLoginStatus() {
    // 假設這裡通過某種方式檢查登入狀態
    const isLoggedIn = false; // 這裡要改為實際的登入狀態檢查
    if (isLoggedIn) {
      enableUpload();
    } else {
      disableUpload();
    }
  }

  // 檔案選擇處理
  fileInput.addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
      // 檢查檔案類型
      if (!file.type.match("image/jpeg") && !file.type.match("image/png")) {
        alert("只允許上傳 JPG 或 PNG 圖片檔案！");
        fileInput.value = "";
        return;
      }

      // 檢查檔案大小（5MB）
      if (file.size > 5 * 1024 * 1024) {
        alert("檔案大小不能超過 5MB！");
        fileInput.value = "";
        return;
      }

      console.log("File selected:", file.name);
      analyzeBtn.disabled = false;
      // 添加分析按鈕點擊事件
      analyzeBtn.addEventListener("click", function () {
        if (!analyzeBtn.disabled) {
          console.log("Starting recognition process...");
          // 這裡可以添加後續的處理邏輯
        }
      });
    }
  });

  // 初始檢查登入狀態
  checkLoginStatus();
});
