"""CatDogClassification URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from functools import partial
from classification.views import show_page, show_user_upload_page, show_classification_results
from classification.views import login_verification, sign_up_verification, user_verification
from classification.views import upload_image_classification, save_data, update_user_historical_data
from classification.views import user_gmail_verification, render_password_reset_page, update_user_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', partial(show_page, page_name='home')),
    path('login/', partial(show_page, page_name='login'), name='login'), # user login
    path('signup/', partial(show_page, page_name='sign_up'), name='sign_up'), # user sign up
    path('upload/', partial(show_page, page_name='upload'), name='upload'), # upload image for classification

    path('gmail_verify/', partial(show_page, page_name='gmail_verification'), name='gmail_verification'), # gmail verification
    path('send_code/', user_gmail_verification, name='send_verification_code'), # send verification code
    path('pasReset/<str:username>', render_password_reset_page, name='password_reset'), # password reset
    path('update/', update_user_password, name='password_update'), # password update

    path('user_verify/', user_verification, name='user_verification'), # user verification
    path('login_verify/', login_verification, name='login_verification'), # login verification
    path('signUp_verify/', sign_up_verification, name='sing_up_verification'), # sign up verification
    path('upload/<str:username>', show_user_upload_page, name='image_uploading'), # user upload image
    path('imgCls/', upload_image_classification, name='classification'), # image classification
    path('show_results/<str:cls_species>&<str:model_pred>&<str:username>', show_classification_results, name='show_results'), # show results
    path('save_data/', save_data, name='save_results'), # save classification result
    path('historical_data/<str:username>&cur_page=<str:cur_page>', update_user_historical_data, name='user_historical_data'), # user's data
]
