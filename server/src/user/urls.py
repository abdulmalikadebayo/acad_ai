from django.urls import path

from . import api

urlpatterns = [
    path("login/", api.LoginAPIView.as_view(), name="login"),
    path("register/", api.RegisterAPIView.as_view(), name="register"),
    path("profile/", api.RetrieveProfileAPIView.as_view(), name="profile"),
]
