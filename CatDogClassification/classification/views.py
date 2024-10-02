from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

import json
from pathlib import Path
from tensorflow.keras.models import load_model
from backend import Verification, Classification

# -----------------------
# User name saving
# -----------------------
USERNAME = 'LoHoLeo2' # default user

# -----------------------
# Verifier loading
# -----------------------
verifier = Verification()

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

species = 'cats' # 這邊先暫定 cats
model_loaded = load_classifier(species=species)

# Load classifiers
classifier = Classification(species=species, classifier=model_loaded)

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
        Image_Nums = range(3)
        Description = '''Lorem Ipsum is simply dummy text of the printing and typesetting
        industry. Lorem Ipsum has been the industry's standard dummy text ever
        since ...'''
        Original_Breed = "None"
        context = { 'Results': Results, 'image_nums': Image_Nums, 'Description': Description, 'Original_Breed': Original_Breed }
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
            img_uploaded = json.loads(request.body).get('image')
            print(img_uploaded, type(img_uploaded))

            # 這邊會先進行 cats dog detection....
            
            # Model prediction
            pred_results = classifier.send_results(img_uploaded)
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
            # 這裡獲取 animal species 的 information (MySQL database)

            # redirect to results page
            result_title = '%s || %s' % (cls_species.capitalize(), model_pred)
            image_nums = ['First', 'Second', 'Third']
            context = {
                'Results': result_title,
                'image_nums': image_nums,
                'Description': '''Lorem Ipsum is simply dummy text of the printing and typesetting
                               industry. Lorem Ipsum has been the industry's standard dummy text ever
                               since ...''',
                'Original_Breed': model_pred,
                'USERNAME': username
            }
            
            return render(request, 'show_results_page.html', context)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})