from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

import json
from pathlib import Path
from tensorflow.keras.models import load_model

from backend import Verification, Classification

# -----------------------
# Verifier loading
# -----------------------
verifier = Verification()

# -----------------------
# Model loading
# -----------------------
cats_classifier_path = Path('model_data').joinpath('cats_classifier.h5')
dogs_classifier_path = Path('model_data').joinpath('dogs_classifier.h5')

species = 'cats' # 這邊先暫定 cats
classifier_loaded = False

# Create your views here.
def show_page(request, page_name):
    if page_name == 'login':
        return render(request, 'login_page.html')
    elif page_name == 'sign_up':
        return render(request, 'sign_up_page.html')
    elif page_name == 'upload':
        return render(request, 'upload_img_page.html')
    elif page_name == 'results':
        return render(request, 'show_results_page.html')
    elif page_name == 'his_data':
        return render(request, 'show_his_data_page.html')
    else:
        return HttpResponse('Error')
    
def login_verification(request): 
    if request.method == 'POST':
        try:
            # Read data from request.body
            user_data = json.loads(request.body)
            print(user_data, type(user_data))

            login_result = verifier.login_verify(user_data)
            if login_result == 'yes': 
                return redirect('/upload/') # Response the successful JSON data
            else: 
                return JsonResponse({'status': 'error', 'message': login_result})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def sign_up_verification(request): 
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

def upload_image_classification(request):
    global classifier_loaded
    
    if request.method == 'POST':
        try:
            # Read data from request.body
            img_uploaded = json.loads(request.body)
            print(img_uploaded, type(img_uploaded))

            # 這邊會先進行 cats dog detection....

            # Load classifiers
            if not classifier_loaded: 
                model_loaded = load_model(cats_classifier_path) \
                               if species == 'cats' \
                               else load_model(dogs_classifier_path)
                classifier = Classification(species=species, classifier=model_loaded)
                classifier_loaded = True
            model_pred = classifier.Model_Predict(img_uploaded)

            # sign_up_result = verifier.sign_up_verify(user_data)
            # if sign_up_result.get('result')  == 'success': 
            #     return JsonResponse({'status': sign_up_result.get('result'), 'message': sign_up_result.get('msg'), 'redirect_url': '/login/'})
            # else: 
            #     return JsonResponse({'status': sign_up_result.get('result'), 'message': sign_up_result.get('msg'), 'redirect_url': None})
            return JsonResponse({'status': 'cats_connection', 'model_pred': model_pred})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})