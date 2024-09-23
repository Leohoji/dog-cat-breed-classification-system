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
from classification.views import show_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', partial(show_page, page_name='login')),
    path('signup/', partial(show_page, page_name='sign_up')),
    path('upload/', partial(show_page, page_name='upload')),
    path('results/', partial(show_page, page_name='results')),
    path('historical_data/', partial(show_page, page_name='his_data')),
]
