from django.shortcuts import render

# Create your views here.
def show_login_page(request):
    return render(request, 'login_page.html')

def show_sign_up_page(request):
    return render(request, 'sign_up_page.html')

def show_upload_img_page(request):
    return render(request, 'upload_img_page.html')