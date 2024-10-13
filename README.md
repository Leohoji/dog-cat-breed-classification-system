# Cat and Dog Recognition System

This is a deep learning-based cat and dog recognition system aimed at helping users identify whether an image contains a cat or a dog. The system is developed using Python 3.8 and the Django framework, utilizing TensorFlow for training the deep learning model.

# How do I complete this project?

This project follows the [SDLC V-Model](https://www.geeksforgeeks.org/software-engineering-sdlc-v-model/) software development process, which includes:

1. **Requirement Analysis**: Define system functionality and performance requirements.
2. **System Design**: Design the overall architecture and database structure.
3. **Implementation**: Write code to implement functionalities.
4. **Unit Testing**: Test individual modules to ensure correctness.
5. **Integration Testing**: Test the integration between modules.
6. **Acceptance Testing**: Perform comprehensive testing in the final environment.
7. **Maintenance**: Continuously improve the system based on user feedback.

## Tech Stack

- **Language**: Python 3.8
- **Framework**: Django 2.2.28
- **Deep Learning**: TensorFlow 2.5.0 
- **Frontend**: HTML, CSS, JavaScript

**GPU Available** (optional) 【💻 My GPU is **GeForce GTX 1050 Ti**】

If you have GPU to accelerate, devices I installed:

-  tensorflow-gpu 2.5.0
-  CUDA 11.2
-  cuDNN 8.1

## Features

### Login and Sign up

User have to login the website first, if you do not have an account, they can register first.

<img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/Login%20and%20Sign-up.jpg?raw=true" alt="User Login" style="width: 500px; height: 400px;"/>

### Upload Image For Classification

User can upload their animal image for breed classification, in addition, users can also view the recognition result records of this account through button "Check historical data".

<div style="display: flex; justify-content: space-around; width: 950px">
  <img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/upload.png?raw=true" alt="Upload User's Image" style="width: 300px; height: 400px;"/>
  <img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/uploaded_image.png?raw=true" alt="Image Uploaded" style="width: 300px; height: 400px;"/>
  <img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/Show%20Historical%20Data.jpg?raw=true" alt="Historical Data" style="width: 300px; height: 400px;"/>
</div>

### Classification Result

After image uploading and classifying, the classification result will display to user, the information include:

1. Detect there is an animal present on the image, and what is the animal is (cat or dog)
2. Recognize the `species` and `breed` to interface
3. Show the relative information and link to user
4. Display another two image to let user check the result
5. Provide a `feedback` area to user for record and further model fine-tune

<img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/classification_result.png?raw=true" alt="User Login" style="width: 800px; height: 600px;"/>

<ins>Password Forgotting?</ins>

User can enter their Gmail account to receive a verification code for password reset:

1. Collect user's Gmail
2. Generate a verification code to user
3. Verify code and password reset

<div style="display: flex; justify-content: space-around; width: 950px">
  <img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/enter-user-gmail.png?raw=true" alt="Enter User's Gmail" style="width: 300px; height: 350px;"/>
  <img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/send-verification-code.png?raw=true" alt="Send Verification Code To User" style="width: 300px; height: 350px;"/>
  <img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/Images/reset-user-password.png?raw=true" alt="Rest Password" style="width: 300px; height: 350px;"/>
</div>


## Installation and Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/cat-dog-recognition.git
