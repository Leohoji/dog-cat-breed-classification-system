import json
import base64
import traceback
import numpy as np
from io import BytesIO
from typing import Tuple
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.applications import MobileNet
import tensorflow_hub as hub 
from PIL import Image, ImageDraw, ImageFont, ImageColor

import random
import smtplib
from email.mime.text import MIMEText
from python_mail import Gmail_Account, Gmail_Password

# from mysql_manager import DatabaseManager
from classification.models import DatabaseManager

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

class AnimalDetector:
    def __init__(self):
        # ---------------------------------------------------------------------------------------------------
        # Object detection model URL
        # MobileNetV2: "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
        # Inception_ResNetV2: "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
        # ---------------------------------------------------------------------------------------------------
        self.module_handle = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1" 
        self.detector = hub.load(self.module_handle).signatures['default']
        
    def load_img_from_base64(self, base64_image_string):
        """Load image from a Base64 string."""
        # Decode the Base64 string
        try:
            base64_image_string = base64_image_string.split(",")[-1]
        except:
            base64_image_string = base64_image_string
        img_data = base64.b64decode(base64_image_string) # Decode the base64 string back to bytes

        # Convert to a NumPy array
        img = tf.image.decode_jpeg(img_data, channels=3)
        return img

    def draw_bounding_box_on_image(self, image,
                                   ymin, xmin, ymax, xmax,
                                   color, font, thickness=4,
                                   display_str_list=()):
        """Adds a bounding box to an image."""
        draw = ImageDraw.Draw(image)
        im_width, im_height = image.size
        (left, right, top, bottom) = (xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height)
        draw.line([(left, top), (left, bottom), (right, bottom), (right, top), (left, top)],
                width=thickness,
                fill=color)

        display_str_heights = [font.getbbox(ds)[3] for ds in display_str_list]
        total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

        if top > total_display_str_height:
            text_bottom = top
        else:
            text_bottom = top + total_display_str_height

        for display_str in display_str_list[::-1]:
            bbox = font.getbbox(display_str)
            text_width, text_height = bbox[2], bbox[3]
            margin = np.ceil(0.05 * text_height)
            draw.rectangle([(left, text_bottom - text_height - 2 * margin), (left + text_width, text_bottom)],
                        fill=color)
            draw.text((left + margin, text_bottom - text_height - margin),
                    display_str,
                    fill="black",
                    font=font)
            text_bottom -= text_height - 2 * margin

    def draw_one_boxes(self, image, boxes, class_names, scores):
        """Overlay labeled boxes on an image with formatted scores and label names."""
        colors = list(ImageColor.colormap.values())
        font = ImageFont.load_default()
        
        ymin, xmin, ymax, xmax = tuple(boxes)
        display_str = "{}: {}%".format(class_names.decode("ascii"), int(100 * scores))
        color = colors[hash(class_names) % len(colors)]
        
        image_pil = Image.fromarray(np.uint8(image)).convert("RGB")
        
        self.draw_bounding_box_on_image(image_pil, 
                                        ymin, xmin, ymax, xmax,
                                        color, font,
                                        display_str_list=[display_str])
        
        np.copyto(image, np.array(image_pil))
        return image

    def run_detector_one_img(self, base64_str):
        img = self.load_img_from_base64(base64_str)

        # Detector inference
        converted_img  = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        result = self.detector(converted_img)
        result = {key: value.numpy() for key, value in result.items()}

        # Draw result
        image_with_boxes = self.draw_one_boxes(img.numpy(), result["detection_boxes"][0],
                                               result["detection_class_entities"][0], result["detection_scores"][0])

        object_class = result["detection_class_entities"][0].decode('utf-8')
        
        return (object_class, image_with_boxes)

class AnimalClassifier(tf.keras.Model):
    """MobileNetV2-based classifier for animal classification."""
    
    def __init__(self, 
                 input_feature: Tuple[int], output_dimension: int, model_name: str = 'animal_classifier'):
        """
        Create a transfer learning model based on MobileNetV2 for animal classification.

        Parameters:
            input_feature (List[int]): Shape of the input image (height, width, channels).
            output_dimension (int): Number of output classes.
            model_name (str): Name of the model (optional).
        """
        super(AnimalClassifier, self).__init__(name=model_name)

        self.input_feature = input_feature
        self.output_dimension = output_dimension

        # Define the model
        self.model = tf.keras.Sequential([
            MobileNet(input_shape=self.input_feature, include_top=False),  
            Dense(64, activation="relu", name="dense_layer", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.4),
            Dense(32, activation="relu", name="dense_layer_2", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.2),
            Dense(16, activation="relu", name="dense_layer_3", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.1),
            Dense(8, activation="relu", name="dense_layer_4", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            Dropout(0.1),
            GlobalAveragePooling2D(name="global_average_pooling_layer"),
            Dense(output_dimension, activation="softmax", name="output_layer")
        ])
        
        self.model.layers[0].trainable = False  # Freeze the pre-trained weights

    def call(self, inputs, training=False, mask=None):
        """Forward pass of the model."""
        return self.model.call(inputs, training, mask)

    def get_config(self):
        """
        Get the model configuration for serialization.
        """
        return {
            "input_feature": self.input_feature,
            "output_dimension": self.output_dimension,
            "model_name": self.name
        }

    @classmethod
    def from_config(cls, config):
        """
        Create a new model instance from the given configuration.
        """
        return cls(**config)

class Classification:
    def __init__(self, classifier, img_size):
        self.classifier = classifier
        self.img_size = img_size

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

    def Model_Predict(self, base64_image_string:str, real_classes:list) -> str:
        """Predict image after preprocessing and return predicted class"""
        # Image preprocessing
        image_rgb = self.decode_base64_image(base64_image_string)
        image = tf.image.convert_image_dtype(image_rgb, tf.float32)
        image_for_pred = tf.image.resize(image, size=[self.img_size, self.img_size])[tf.newaxis, ...]
        
        # Model prediction
        model_pred = self.classifier.predict(image_for_pred) # predict image
        pred_index = np.argmax(np.squeeze(model_pred)) # get the highest class index
        final_class = real_classes[pred_index] # final image class
        
        return final_class

    def send_results(self, base64_image_string:str, real_classes:list) -> dict:
        """
        Send model prediction results to front-end in JSON data type.
        1. Model predicts the breed of image.
        2. Add prediction result to data.
        3. Convert results data into JSON format.
        """
        try:
            final_pred = self.Model_Predict(base64_image_string, real_classes)
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
    _ = smtp.send_message(mail)
    smtp.quit()

    return {'verification_code': random_number}

def update_password(user_name:str, new_password:str):
    global data_manager
    user_updated = data_manager.update_user_password(user_name=user_name, new_password=new_password) # return a boolean
    
    return user_updated

if __name__ == "__main__":
    
    import base64
    import io
    import numpy as np
    from PIL import Image
    import tensorflow as tf

    class ImageReader:
        def __init__(self, image_path):
            self._image_path = image_path

        def read(self):
            with open(self._image_path, 'rb') as file:
                self._image_bytes = file.read()
            return self._image_bytes
        
        def from_base64(self, image_bytes):
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            img_data = base64.b64decode(base64_string)
            image_io = io.BytesIO(img_data)
            image_array = Image.open(image_io)
            return image_array
        
        def to_numpy(self, image_array: Image) -> np.array:
            return np.array(image_array)
        
        def run(self):
            image_byte = self.read()
            image = self.from_base64(image_byte)
            image = self.to_numpy(image)
            image = tf.image.convert_image_dtype(image, tf.float32)
            image = tf.image.resize(image, size=[224, 224])
            return image[tf.newaxis, ...]

    imgPath = 'Bengal.jpg'
    image_reader = ImageReader(imgPath)
    image = image_reader.run()
    # print(image)

    def custom_loss_fn(y_true, y_pred):
        loss_fn = tf.keras.losses.CategoricalCrossentropy()
        loss = loss_fn(y_true, y_pred)

        return loss

    loaded_final_classifier = tf.keras.models.load_model(
        'model_data/three_final_classifier', 
        custom_objects={
            'MobileNetClassifier': AnimalClassifier, 
            'custom_loss_fn': custom_loss_fn
        }
    )

    pred_prob = loaded_final_classifier(image)
    
    print(pred_prob)