# from django.contrib import admin
from django.urls import path
from .views import *

app_name = 'accounts'
urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("register", UserRegisterView.as_view(), name="register"),
    path("profile", UserProfileUpdateView.as_view(), name="profile"),
    path('profile/upload-image/', ProfileImageUploadView.as_view(),
         name='profile_upload_image'),
]
