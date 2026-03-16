from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout_user, name="logout"),
    path('apply/', views.apply_relief, name='apply_relief'),
]