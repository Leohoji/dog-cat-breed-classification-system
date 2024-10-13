from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

import io
import json
import base64
import numpy as np
from PIL import Image
from io import BytesIO
from pathlib import Path
from tensorflow.keras.models import load_model
from backend import Verification, Classification, AnimalDetector
from backend import collect_animal_info, save_results_to_database, collect_historical_data
from backend import send_verification_code, update_password

# -----------------------
# Default variables
# -----------------------
USERNAME = 'LoHoLeo2'
USER_IMG_PATH = 'user_img.txt'
USER_BOX_IMG_PATH = 'user_box_img.txt'

# -----------------------
# Verifier loading
# -----------------------
verifier = Verification()

# Load real classes
cat_real_classes = np.load(Path('label_data').joinpath('cats_classes.npy'))
dog_real_classes = np.load(Path('label_data').joinpath('dogs_classes.npy'))

# -----------------------
# Model loading
# -----------------------
cats_classifier_path = Path('model_data').joinpath('cats_classifier.h5')
dogs_classifier_path = Path('model_data').joinpath('dogs_classifier.h5')
cat_classifier_loaded = load_model(cats_classifier_path)
dog_classifier_loaded = load_model(dogs_classifier_path)

# Animal detector
animal_detector = AnimalDetector()

# Load classifiers
classifier = Classification()

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
                print(username)
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

def upload_image_classification(request):
    """Receive image data from user and return the results of species classification"""
    global classifier
    
    if request.method == 'POST':
        try:
            # Read data from request.body
            user_img_uploaded = json.loads(request.body).get('image').replace('data:image/jpeg;base64,', '')
            save_base64_to_file(user_img_uploaded, fpath=USER_IMG_PATH) # save user's original image
            print(type(user_img_uploaded))

            # Cat-Dog Detection....
            object_class, image_with_boxes = animal_detector.run_detector_one_img(user_img_uploaded)
            print(object_class)

            image_with_boxes_base64 = numpy_array_to_base64_image(image_with_boxes)
            save_base64_to_file(image_with_boxes_base64, fpath=USER_BOX_IMG_PATH) # save user's boxed image


            if object_class == "Cat":
                classifier.register_species("Cat", cat_classifier_loaded, cat_real_classes)
            else:
                classifier.register_species("Dog", dog_classifier_loaded, dog_real_classes)

            # Model prediction
            pred_results = classifier.send_results(user_img_uploaded)
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
            real_classes = cat_real_classes if cls_species == "Cat" else dog_real_classes

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