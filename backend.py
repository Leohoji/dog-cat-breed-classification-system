import cv2
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input as EFNetPreProcessInput

from model import DatabaseManager

IMG_SIZE = (224, 224, 3)

class Verification(DatabaseManager):
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
            if member_info != UserPassword:
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

        # check information
        if not member_info:
            user_name, user_password  = self.get_user_info(user_data)
            self.add_member(user_name, user_password)
            response = 'success'
        else: response = 'fail' 

        return response

# data = { 'species': ##, 'image': ## }
class Classification:
    def __init__(self, json_payload:str):
        self.json_payload = json_payload

        # Parse the JSON payload
        self.data = json.loads(self.json_payload)

        # Extract base64 image string and species 
        self.species, self.base64_image_string = self.data['species'], self.data['image']

        # Load real classes and classifier
        self.real_classes = np.load('cats_classes.npy') \
                            if self.species == 'cats' \
                            else np.load('dogs_classes.npy')
        self.classifier_loaded = load_model('./cats_classifier.h5') \
                                 if self.species == 'cats' \
                                 else load_model('./dogs_classifier.h5')

    def decode_base64_image(self) -> np.array:
        """Decode the base64 string and return the image as a PIL object"""
        # Decode the base64 string back to bytes
        img_data = base64.b64decode(self.base64_image_string)
        
        # Use BytesIO to convert the decoded bytes to an image
        img = Image.open(BytesIO(img_data))
        
        # Convert the PIL image to a NumPy array
        self.img_array = np.array(img)
        
        return self.img_array

    def Model_Predict(self) -> str:
        """Predict image after preprocessing and return predicted class"""
        # Image preprocessing
        image_rgb = self.decode_base64_image()
        image_rgb = image_rgb.astype(np.float32)
        resized_image = cv2.resize(image_rgb, IMG_SIZE) # resize image to (224, 224, 3)
        processed_image = EFNetPreProcessInput(resized_image)  # preprocess image
        image_for_pred = np.expand_dims(processed_image, axis=0) # add a batch dim
        
        # Model prediction
        model_pred = self.classifier_loaded.predict(image_for_pred) # predict image
        pred_index = np.argmax(np.squeeze(model_pred)) # get the highest class index
        final_class = self.real_classes[pred_index] # final image class
        
        return final_class

    def send_results(self) -> str:
        """
        Send model prediction results to front-end in JSON data type.
        1. Model predicts the breed of image.
        2. Add prediction result to data.
        3. Convert results data into JSON format.
        """
        final_pred = self.Model_Predict()
        self.data['model_pred'] = final_pred
        results = json.dumps(self.data, indent=4)

        return results

class CheckHistoricalData:
    def collect_historical_data(self, user_name:str):

        pass

class LearningSystem:
    def feedback(self):
        pass

    def save_to_historical_data(self, user_data:dict):
        pass

    def fine_tune_classifier(self):
        pass