from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import json
import numpy as np
from pathlib import Path
from tensorflow.keras.models import load_model
from backend import Verification, Classification
from backend import collect_animal_info

# -----------------------
# Default variables
# -----------------------
USERNAME = 'LoHoLeo2'
USER_IMG_FILE_NAME = 'user_img.txt' # user's image
species = 'cats' # 這邊先暫定 cats

# -----------------------
# Verifier loading
# -----------------------
verifier = Verification()

def save_base64_to_file(base64_string):
    """Save Base64 string to txt file"""
    with open(USER_IMG_FILE_NAME, 'w') as file:
        file.write(base64_string)

def read_base64_from_file():
    """Read Base64 string from txt file"""
    with open(USER_IMG_FILE_NAME, 'r') as file:
        return file.read()

# Load real classes
real_classes = np.load(Path('label_data').joinpath('cats_classes.npy')) \
                       if species == 'cats' \
                       else np.load(Path('label_data').joinpath('dogs_classes.npy'))

# -----------------------
# Model loading
# -----------------------
cats_classifier_path = Path('model_data').joinpath('cats_classifier.h5')
dogs_classifier_path = Path('model_data').joinpath('dogs_classifier.h5')

def load_classifier(species):
    if species == 'cats':
        model_path = cats_classifier_path
    else:
        model_path = dogs_classifier_path

    model = load_model(model_path)
    return model

model_loaded = load_classifier(species=species)

# Load classifiers
classifier = Classification(species=species, classifier=model_loaded, real_classes=real_classes)

# Create your views here.
def show_page(request, page_name):
    if page_name == 'login':
        return render(request, 'login_page.html')
    elif page_name == 'sign_up':
        return render(request, 'sign_up_page.html')
    elif page_name == 'upload':
        return render(request, 'upload_img_page.html', { 'USERNAME': USERNAME })
    elif page_name == 'results':
        Results = 'Some results here'
        Image_Nums = enumerate([1, 2, 3], start=1)
        Description = '''Lorem Ipsum is simply dummy text of the printing and typesetting
        industry. Lorem Ipsum has been the industry's standard dummy text ever
        since ...'''
        Link = 'https://en.wikipedia.org/wiki/Cat'
        Original_Breed = "None"
        Data = {'description': Description, 'link': Link}
        context = { 'Results': Results, 'image_nums': Image_Nums, 
                   'Data': Data, 'Original_Breed': Original_Breed, 
                   'USERNAME': USERNAME, 'breeds': [str(i) for i in range(10)] }
        return render(request, 'show_results_page.html', context)
    elif page_name == 'his_data':
        return render(request, 'show_his_data_page.html')
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
            user_img_uploaded = json.loads(request.body).get('image')
            # print(user_img_uploaded)
            print(type(user_img_uploaded))
            save_base64_to_file(user_img_uploaded.replace('data:image/jpeg;base64,', ''))

            # 這邊會先進行 cats dog detection....
            
            # Model prediction
            pred_results = classifier.send_results(user_img_uploaded)
            print(pred_results, type(pred_results))
            status = pred_results.get('status')
            if status  == 'ok': 
                model_pred =  pred_results.get('model_pred')
                return JsonResponse({'status': status, 'species': species, 'model_pred': model_pred, 'message': None})
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
            result_title = 'SPECIES: %s || BREED: %s' % (cls_species.capitalize(), model_pred)
            
            # images need to be decoded after MySQL querying
            user_img = read_base64_from_file()
            image_1 = animal_data['image_1'].decode('utf-8')
            image_2 = animal_data['image_2'].decode('utf-8')
            image_nums = zip(["Your Image", f"{model_pred} Image1", f"{model_pred} Image2"], 
                             [user_img, image_1, image_2])

            # animal description and link
            Description = animal_data['animal_description'] 
            Link = animal_data['animal_link']
            Data = {'description': Description, 'link': Link}

            # full context
            context = {'Results': result_title,'image_nums': image_nums, 'Data': Data,
                       'Original_Breed': model_pred, 'USERNAME': username, 'breeds': real_classes}
            
            return render(request, 'show_results_page.html', context)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})