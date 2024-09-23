from django.shortcuts import render
from django.http import HttpResponse

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