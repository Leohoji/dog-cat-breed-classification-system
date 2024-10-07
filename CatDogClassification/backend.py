import cv2
import json
import base64
import traceback
import numpy as np
from io import BytesIO
from PIL import Image
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

import random
import smtplib
from email.mime.text import MIMEText
from python_mail import Gmail_Account, Gmail_Password

from mysql_manager import DatabaseManager

data_manager = DatabaseManager() # initialize DatabaseManager
IMG_SIZE = (224, 224)

class Verification(DatabaseManager):
    def user_exists(self, username:str):
        """
        Verify whether user account exists.

        Args:
            username: User's account information.
        Returns:
            String of 'user not exists' or 'yes'.
        """
        # get member information
        member_info = self.get_member_info({"user_name": username})

        # check information
        if not member_info:
            result = 'user not exists'
        else:
           result = 'yes'

        return result
    
    def login_verify(self, user_data:dict) -> str:
        """
        Verify user data from login interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'user not exists', 'wrong password', or 'yes'.
        """
        # get member information
        member_info = self.get_member_info(user_data)

        # check information
        if not member_info:
            result = 'user not exists'
        else:
            _, UserName, UserPassword, _ = member_info # (id, user_name, user_password, timestamp)
            result = (UserName, UserPassword)
            print(f"output: {result}")
            if user_data.get('password') != UserPassword:
                result = 'wrong password' # password is incorrect
            else:
                result = 'yes'

        return result
    
    def sign_up_verify(self, user_data:dict) -> str:
        """
        Verify user data from sign_up interface.

        Args:
            user_data: Dictionary of user's information.
        Returns:
            String of 'success', or 'fail'.
        """
        # get member information
        member_info = self.get_member_info(user_data)
        print(member_info)

        # check information
        if not member_info:
            user_name, user_password  = self.get_user_info(user_data)
            self.add_member(user_name, user_password)
            response = {'result':'success', 'msg': 'Sing up successfully !'}
        else: 
            response = {'result':'fail', 'msg': 'This username has been exists.'}

        return response

class Classification:
    def __init__(self, species, classifier, real_classes):
        self.species = species
        self.classifier_loaded = classifier
        self.real_classes = real_classes

    def decode_base64_image(self, base64_image_string:str) -> np.array:
        """Decode the base64 string and return the image as a PIL object"""
        try:
            self.base64_image_string = base64_image_string.split(",")[-1]
        except:
            self.base64_image_string = base64_image_string
        img_data = base64.b64decode(self.base64_image_string) # Decode the base64 string back to bytes
        img = Image.open(BytesIO(img_data)) # Use BytesIO to convert the decoded bytes to an image
        self.img_array = np.array(img) # Convert the PIL image to a NumPy array
        return self.img_array

    def Model_Predict(self, base64_image_string:str) -> str:
        """Predict image after preprocessing and return predicted class"""
        # Image preprocessing
        image_rgb = self.decode_base64_image(base64_image_string)
        image_rgb = image_rgb.astype(np.float32)
        resized_image = cv2.resize(image_rgb, IMG_SIZE) # resize image to (224, 224, 3)
        processed_image = EFNetPreProcessInput(resized_image)  # preprocess image
        image_for_pred = np.expand_dims(processed_image, axis=0) # add a batch dim
        
        # Model prediction
        model_pred = self.classifier_loaded.predict(image_for_pred) # predict image
        pred_index = np.argmax(np.squeeze(model_pred)) # get the highest class index
        final_class = self.real_classes[pred_index] # final image class
        
        return final_class

    def send_results(self, base64_image_string:str) -> dict:
        """
        Send model prediction results to front-end in JSON data type.
        1. Model predicts the breed of image.
        2. Add prediction result to data.
        3. Convert results data into JSON format.
        """
        try:
            final_pred = self.Model_Predict(base64_image_string)
            results = { 'status': 'ok', 'model_pred': final_pred }
        except Exception as E:
            traceback.print_exc()
            results = { 'status': 'error', 'msg': E.__class__.__name__ }

        return results

def collect_animal_info(animal_breed:str):
    """
    Get animal information of animal breed from front-end interface.

    Args:
        animal_breed: Animal's breed name from model prediction
    Returns:
        Animal information (breed_name, images, description, link) in dictionary data type
    """
    global data_manager
    animal_data = data_manager.get_animal_info(animal_breed)
    
    return animal_data

def save_results_to_database(username:str, image:str, feedback:json): 
    """
    Save user's classification results to MySQL database
    
    Args:
        username: User's name from front-end interface
        image: Image object in base64 data type
        feedback: Classification results from user's feedback
    Returns:
        Boolean, whether to save successfully
    """
    global data_manager
    saved = data_manager.update_historical_data(user_name=username, image=image, feedback=feedback)
    
    return saved

def collect_historical_data(user_name:str) -> list:
    """
    Get historical data of via username passed from front-end interface.

    Args:
        user_name: Member's user name
    Returns:
        List format of user historical data
    """
    global data_manager
    historical_data = data_manager.get_historical_data(user_name) # return a list
    user_historical_data = [(data[2].decode('utf-8'), data[3], data[4].strftime("%Y/%m/%d %H:%M:%S")) for data in historical_data]

    return user_historical_data

def send_verification_code(to_user_gmail:str) -> dict:
    """
    Generate a verification code and sed it to user's gmail account
    
    Args:
        to_user_gmail: The user gmail account to send
    Returns:
        A dictionary contains sending verification code
    """
    # Generate 5-digit random number
    random_number = random.randint(10000, 99999)
    html = '''
    <html lang="en">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; text-align: center; padding: 50px;">
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="margin: 0;">Your Verification Code</h1>
            <p style="margin: 10px 0;">Please use the following code to complete verification:</p>
            <div style="font-size: 24px; font-weight: bold; color: #007BFF;">{}</div>
            <p style="margin: 10px 0;">If you did not request this code, please ignore this email.</p>
        </div>
    </body>
    </html>
    '''.format(random_number)

    mail = MIMEText(html, 'html', 'utf-8') # plain 換成 html，就能寄送 HTML 格式的信件
    mail['Subject']='Cat And Dog System Verification Code'
    mail['From']= Gmail_Account
    mail['To']= to_user_gmail

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(Gmail_Account, Gmail_Password)
    status = smtp.send_message(mail)
    smtp.quit()

    return {'verification_code': random_number}


if __name__ == "__main__":
    verifier = Verification()
    print(verifier.login_verify({"user_name": "Leo"}))