# Django applications
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

# Model loading and predictions
import tensorflow as tf
import tensorflow_hub as hub 
from tensorflow.keras.models import load_model
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D

# Image file operation
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageColor

# Mail operation
import random
import smtplib
from email.mime.text import MIMEText
from python_mail import Gmail_Account, Gmail_Password

# Better debugging
import traceback
from typing import Tuple

# Data manager from models.py file
from classification.models import DatabaseManager

data_manager = DatabaseManager() # initialize DatabaseManager
IMG_SIZE = (224, 224)

# class AnimalDetector:
#     def __init__(self):
#         # ---------------------------------------------------------------------------------------------------
#         # Object detection model URL
#         # MobileNetV2: "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
#         # Inception_ResNetV2: "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
#         # ---------------------------------------------------------------------------------------------------
#         self.module_handle = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1" 
#         self.detector = hub.load(self.module_handle).signatures['default']
        
#     def load_img_from_base64(self, base64_image_string):
#         """Load image from a Base64 string."""
#         # Decode the Base64 string
#         try:
#             base64_image_string = base64_image_string.split(",")[-1]
#         except:
#             base64_image_string = base64_image_string
#         img_data = base64.b64decode(base64_image_string) # Decode the base64 string back to bytes

#         # Convert to a NumPy array
#         img = tf.image.decode_jpeg(img_data, channels=3)
#         return img

#     def draw_bounding_box_on_image(self, image,
#                                    ymin, xmin, ymax, xmax,
#                                    color, font, thickness=4,
#                                    display_str_list=()):
#         """Adds a bounding box to an image."""
#         draw = ImageDraw.Draw(image)
#         im_width, im_height = image.size
#         (left, right, top, bottom) = (xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height)
#         draw.line([(left, top), (left, bottom), (right, bottom), (right, top), (left, top)],
#                 width=thickness,
#                 fill=color)

#         display_str_heights = [font.getbbox(ds)[3] for ds in display_str_list]
#         total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

#         if top > total_display_str_height:
#             text_bottom = top
#         else:
#             text_bottom = top + total_display_str_height

#         for display_str in display_str_list[::-1]:
#             bbox = font.getbbox(display_str)
#             text_width, text_height = bbox[2], bbox[3]
#             margin = np.ceil(0.05 * text_height)
#             draw.rectangle([(left, text_bottom - text_height - 2 * margin), (left + text_width, text_bottom)],
#                         fill=color)
#             draw.text((left + margin, text_bottom - text_height - margin),
#                     display_str,
#                     fill="black",
#                     font=font)
#             text_bottom -= text_height - 2 * margin

#     def draw_one_boxes(self, image, boxes, class_names, scores):
#         """Overlay labeled boxes on an image with formatted scores and label names."""
#         colors = list(ImageColor.colormap.values())
#         font = ImageFont.load_default()
        
#         ymin, xmin, ymax, xmax = tuple(boxes)
#         display_str = "{}: {}%".format(class_names.decode("ascii"), int(100 * scores))
#         color = colors[hash(class_names) % len(colors)]
        
#         image_pil = Image.fromarray(np.uint8(image)).convert("RGB")
        
#         self.draw_bounding_box_on_image(image_pil, 
#                                         ymin, xmin, ymax, xmax,
#                                         color, font,
#                                         display_str_list=[display_str])
        
#         np.copyto(image, np.array(image_pil))
#         return image

#     def run_detector_one_img(self, base64_str):
#         img = self.load_img_from_base64(base64_str)

#         # Detector inference
#         converted_img  = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
#         result = self.detector(converted_img)
#         result = {key: value.numpy() for key, value in result.items()}

#         # Draw result
#         image_with_boxes = self.draw_one_boxes(img.numpy(), result["detection_boxes"][0],
#                                                result["detection_class_entities"][0], result["detection_scores"][0])

#         object_class = result["detection_class_entities"][0].decode('utf-8')
        
#         return (object_class, image_with_boxes)

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

# -----------------------
# Default variables
# -----------------------
USERNAME = 'LoHoLeo2'
USER_IMG_PATH = 'user_img.txt'
USER_BOX_IMG_PATH = 'user_box_img.txt'
IMG_SIZE = 224 

# -----------------------
# Verifier loading
# -----------------------
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
    
verifier = Verification()

# Load real classes
label_data = np.load("label_data/three_categories.npz", allow_pickle=True)

# -----------------------
# Model loading
# -----------------------
def custom_loss_fn(y_true, y_pred):
    loss_fn = CategoricalCrossentropy()
    loss = loss_fn(y_true, y_pred)

    return loss

model_loaded = load_model(
    'model_data/three_final_classifier', 
    custom_objects={
        'MobileNetClassifier': AnimalClassifier, 
        'custom_loss_fn': custom_loss_fn
    }
)

# Animal detector
# animal_detector = AnimalDetector()

# Load classifiers
classifier = Classification(model_loaded, img_size=IMG_SIZE)

# Create your views here.
def save_base64_to_file(base64_string, fpath):
    """Save Base64 string to txt file"""
    with open(fpath, 'w') as file:
        file.write(base64_string)

def read_base64_from_file(fpath):
    """Read Base64 string from txt file"""
    with open(fpath, 'r') as file:
        return file.read()

def show_page(request, page_name):
    if page_name == 'login':
        return render(request, 'login_page.html')
    elif page_name == 'sign_up':
        return render(request, 'sign_up_page.html')
    elif page_name == 'upload':
        return render(request, 'upload_img_page.html', { 'USERNAME': USERNAME })
    elif page_name == 'gmail_verification':
        return render(request, 'gmail_verification.html')
    elif page_name == 'home':
        return render(request, 'main_page.html')
    else:
        return HttpResponse('Error')
    
def login_verification(request): 
    """Verify user information while login"""
    if request.method == 'POST':
        try:
            # Read data from request.body
            user_data = json.loads(request.body)
            print(user_data, type(user_data))

            login_result = verifier.login_verify(user_data)
            if login_result == 'yes': 
                username = user_data.get('user_name')
                return JsonResponse({'status': login_result, 'USERNAME': username})
            else: 
                return JsonResponse({'status': 'error', 'message': login_result})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def user_verification(request): 
    """Verify user information"""
    if request.method == 'POST':
        try:
            # Read data from request.body
            user_data = json.loads(request.body)
            print(user_data, type(user_data))

            user_is_exists = verifier.user_exists(user_data.get("user_name"))
            print(user_is_exists)

            return JsonResponse({'status': user_is_exists})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def sign_up_verification(request): 
    """Verify user information while sign up"""
    if request.method == 'POST':
        try:
            # Read data from request.body
            user_data = json.loads(request.body)
            print(user_data, type(user_data))

            sign_up_result = verifier.sign_up_verify(user_data)
            if sign_up_result.get('result')  == 'success': 
                return JsonResponse({'status': sign_up_result.get('result'), 'message': sign_up_result.get('msg'), 'redirect_url': '/login/'})
            else: 
                return JsonResponse({'status': sign_up_result.get('result'), 'message': sign_up_result.get('msg'), 'redirect_url': None})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def show_user_upload_page(request, username):
    """Show image uploading page based on username"""
    if request.method == 'GET':
        try:
            return render(request, 'upload_img_page.html', { 'USERNAME': username })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def numpy_array_to_base64_image(array):
    """
    Convert a NumPy array to a Base64 encoded image string.

    Parameters:
    array (numpy.ndarray): The input NumPy array representing the image.

    Returns:
    str: Base64 encoded image string that can be used in an <img> tag.
    """
    # Ensure the array is in the correct format (uint8)
    if array.dtype != np.uint8:
        array = array.astype(np.uint8)
    
    # Convert NumPy array to a PIL Image
    image = Image.fromarray(array)

    # Save the image to a BytesIO object
    buffered = BytesIO()
    image.save(buffered, format="JPEG")  # You can change the format if needed
    base64_data = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Create the HTML <img> tag with Base64 data
    return base64_data

class AnimalDetector:
    def __init__(self):
        self.img_path = 'C:/Users/User/Desktop/cat_dog_project/output_with_boxes.png'

    def run_detector_one_img(self, base64_str):
        self.output_img = np.array(Image.open(self.img_path).convert('RGB'))
        return 'Cat', self.output_img
    
animal_detector = AnimalDetector()

def upload_image_classification(request):
    """Receive image data from user and return the results of species classification"""
    global classifier
    
    if request.method == 'POST':
        try:
            # Read data from request.body
            user_img_uploaded = json.loads(request.body).get('image').replace('data:image/jpeg;base64,', '')
            save_base64_to_file(user_img_uploaded, fpath=USER_IMG_PATH) # save user's original image

            # Cat-Dog Detection....
            object_class, image_with_boxes = animal_detector.run_detector_one_img(user_img_uploaded)

            image_with_boxes_base64 = numpy_array_to_base64_image(image_with_boxes)
            save_base64_to_file(image_with_boxes_base64, fpath=USER_BOX_IMG_PATH) # save user's boxed image

            real_classes = label_data['cats'] if object_class == "Cat" else label_data['dogs']

            # Model prediction
            pred_results = classifier.send_results(user_img_uploaded, real_classes)
            print(pred_results, type(pred_results))
            status = pred_results.get('status')
            if status  == 'ok': 
                model_pred =  pred_results.get('model_pred')

                return JsonResponse({'status': status, 'species': object_class, 'model_pred': model_pred, 'message': None})
            else: 
                msg = pred_results.get('msg')
                return JsonResponse({'status': status, 'species': None, 'model_pred': None, 'message': msg})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        print("Invalid request method:", request.method)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def show_classification_results(request, cls_species, model_pred, username):
    """Show results of species classification on the '/show_results/' page"""
    if request.method == 'GET':
        try:
            # collect animal information from MySQL database
            animal_data = collect_animal_info(model_pred)

            # redirect to results page
            result_title = 'SPECIES: %s || BREED: %s' % (cls_species, model_pred)
            
            # images need to be decoded after MySQL querying
            user_img = read_base64_from_file(fpath=USER_BOX_IMG_PATH) # show the boxed image
            image_1 = animal_data['image_1'].decode('utf-8')
            image_2 = animal_data['image_2'].decode('utf-8')
            image_nums = zip(["Your Image", f"{model_pred} Image1", f"{model_pred} Image2"], 
                             [user_img, image_1, image_2])

            # animal description and link
            Description = animal_data['animal_description'] 
            Link = animal_data['animal_link']
            Data = {'description': Description, 'link': Link}
            real_classes = label_data['cats'] if cls_species == "Cat" else label_data['dogs']

            # full context
            context = {'Results': result_title,'image_nums': image_nums, 'Data': Data,
                       'Original_Breed': model_pred, 'USERNAME': username, 'breeds': real_classes}
            
            return render(request, 'show_results_page.html', context)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def save_data(request):
    """Save user's feedback and classification result to database"""
    if request.method == 'POST':
        try:
            # collect user's classification result
            user_data = json.loads(request.body)
            print(user_data, type(user_data))

            # get username, user's image, user's feedback
            username = user_data.get('username')
            user_img = read_base64_from_file(fpath=USER_IMG_PATH) # save user's original image
            cls_result = user_data.get('feedback')
            feedback = "%s,%s" %(cls_result['breedChoice'], cls_result['selectedBreed'])\
            
            # save to database
            saved = save_results_to_database(username=username, image=user_img, feedback=feedback)

            if saved: print("Successfully save feedback to MySQL database!")
            else: print("Fail, please check the function!")

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def update_user_historical_data(request, username, cur_page):
    """ Get historical data via username passed from front-end interface."""
    if request.method == 'GET':
        try:
            # collect user's data
            user_historical_data = collect_historical_data(user_name=username)

            # set paginator for HTML pagination
            cur_page = int(cur_page)
            paginator = Paginator(user_historical_data, 5) # pass all historical data and five per page
            print(f"historical_data_count: {len(user_historical_data)} | paginator's count (幾個，幾頁，頁碼): {paginator.count, paginator.num_pages, paginator.page_range}")
            page_range = paginator.page_range # rage of all page numbers
            page = paginator.page(cur_page) # current page object

            # Over than 11 pages
            if paginator.num_pages > 11:
                # -----------------------------------------------------------
                # When the last 5 pages of the current page number exceed 
                # the maximum page number, the last 10 items will be displayed.
                # -----------------------------------------------------------
                if cur_page + 5 > paginator.num_pages:
                    page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
                # -----------------------------------------------------------
                # When the first 5 pages of the current page number are negative, 
                # the first 10 items are displayed.
                # -----------------------------------------------------------
                elif cur_page - 5 < 1:
                    page_range = range(1, 12)
                else:
                    # Display the page numbers from page 5 on the left to page 5 on the right
                    page_range = range(cur_page - 5, cur_page + 5 + 1)
            # Show all page numbers if there are less than 11 pages
            else:
                page_range = paginator.page_range

            # create the context for HTML variables delivery
            context = {'USERNAME': username, 
                       'Historical_Data': page.object_list, 
                       'page': page, 
                       'current_num': cur_page, 
                       'page_range': page_range}

            return render(request, 'show_his_data_page.html', context)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def render_password_reset_page(request, username): 
    """ Render password resetting page with correct user account."""
    if request.method == 'GET':
        try:
           # create the context for HTML variables delivery
            context = {'USERNAME': username}

            return render(request, 'password_reset.html', context)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def user_gmail_verification(request): 
    """Send verification code to user's gmail account"""
    if request.method == 'POST':
        try:
           user_gmail_account = json.loads(request.body).get('gmail')
           verification_data = send_verification_code(to_user_gmail=user_gmail_account)
           return JsonResponse(verification_data)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def update_user_password(request):
    """Update user's password set on the front-end interface"""
    if request.method == 'POST':
        try:
           user_update_account = json.loads(request.body)
           print(user_update_account)
           user_name, new_password = user_update_account.get("username"), user_update_account.get("newUserPassword")
           print(user_name, new_password)
           user_updated = update_password(user_name=user_name, new_password=new_password) # return a boolean
           
           if user_updated:
               return JsonResponse({'result': 'success'})
           else:
               return JsonResponse({'result': 'Something Error'}) 

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


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