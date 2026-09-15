from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login_view),
    path('signup', views.signup_view),
    path('me', views.me_view),
    path('logout', views.logout_view),
]