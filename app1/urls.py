
from django.urls import path
from . import views

app_name = 'app1'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
]