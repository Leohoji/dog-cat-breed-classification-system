from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
import json

from backend import Verification

verifier = Verification()

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