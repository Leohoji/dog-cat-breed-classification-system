# Django applications
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

# Model loading and predictions
import tensorflow_hub as hub 

# Image file operation
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import datetime
from pathlib import Path

# Mail operation
import random
import smtplib
from email.mime.text import MIMEText
from python_mail import Gmail_Account, Gmail_Password

from model_loader import load_animal_classifier

# Data manager from models.py file
from classification.models import DatabaseManager

data_manager = DatabaseManager() # initialize DatabaseManager
IMG_SIZE = (224, 224)


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

def save_results_to_database(username:str, image_path:str, feedback:json): 
    """
    Save user's classification results to MySQL database
    
    Args:
        username: User's name from front-end interface
        image_path: Image path for image saving
        feedback: Classification results from user's feedback
    Returns:
        Boolean, whether to save successfully
    """
    global data_manager
    saved = data_manager.update_historical_data(user_name=username, image_path=image_path, feedback=feedback)
    
    return saved

def read_base64_from_file(fpath):
    """Read Base64 string from txt file"""
    with open(fpath, 'r') as file:
        return file.read()

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
    user_historical_data = [
        (read_base64_from_file(data[2].split(',')[0]), data[3], data[4].strftime("%Y/%m/%d %H:%M:%S")) 
        for data in historical_data]

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
IMAGE_STORAGE_DIR = Path('D:/cats_dogs_classification_storage')

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
model_path = 'model_data/three_final_classifier'
label_path = 'label_data/three_categories.npz'
module_handle = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1" 
DETECTOR = hub.load(module_handle).signatures['default']

classifier = load_animal_classifier(model_path, label_path, IMG_SIZE, DETECTOR)


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

def upload_image_classification(request):
    """Receive image data from user and return the results of species classification"""
    global classifier
    
    if request.method == 'POST':
        try:
            # Read data from request.body
            user_img_uploaded = json.loads(request.body).get('image').replace('data:image/jpeg;base64,', '')

            # Model prediction
            pred_results = classifier.send_results(user_img_uploaded)
            status = pred_results.get('status')
            if status  == 'ok': 
                model_pred =  pred_results.get('model_pred')
                object_class = pred_results.get('object_class')

                return JsonResponse({'status': status, 'species': object_class, 'model_pred': model_pred})
            else: 
                msg = pred_results.get('msg')
                return JsonResponse({'status': status, 'message': msg})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        print("Invalid request method:", request.method)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def show_classification_results(request, cls_species, model_pred, username):
    """Show results of species classification on the '/show_results/' page"""
    global classifier
    if request.method == 'GET':
        try:
            # collect animal information from MySQL database
            animal_data = collect_animal_info(model_pred)

            # redirect to results page
            result_title = 'SPECIES: %s || BREED: %s' % (cls_species, model_pred)
            
            # images need to be decoded after MySQL querying
            img_with_bbox, _ = classifier.get_images()
            image_1 = animal_data['image_1'].decode('utf-8')
            image_2 = animal_data['image_2'].decode('utf-8')
            image_nums = zip([f"{cls_species}: {model_pred}", f"EX1: {model_pred}", f"EX2: {model_pred}"], 
                             [img_with_bbox, image_1, image_2])

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
    global classifier
    if request.method == 'POST':
        try:
            # collect user's classification result
            user_data = json.loads(request.body)

            # get username, user's image, user's feedback
            username = user_data.get('username')
            # user_img = read_base64_from_file(fpath=USER_IMG_PATH) # save user's original image
            img_with_bbox, cropped_img = classifier.get_images()
            cls_result = user_data.get('feedback')
            feedback = "%s,%s" %(cls_result['breedChoice'], cls_result['selectedBreed'])

            # create username folder and save images
            user_dir = IMAGE_STORAGE_DIR / username
            if not user_dir.is_dir():
                user_dir.mkdir(parents=True, exist_ok=True)
            
            paths = []
            for fname, img in [('bbox_img', img_with_bbox), ('cropped_img', cropped_img)]:
                image_save_to = str(user_dir / (fname + '_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt'))
                with open(image_save_to, 'w') as file:
                    file.write(img)
                paths.append(image_save_to)
            image_path = ', '.join(paths)
            print(f"image path: {image_path}")
            
            # save to database
            saved = save_results_to_database(username=username, image_path=image_path, feedback=feedback)

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
            page_range = paginator.page_range # range of all page numbers
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
