from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout_user, name="logout"),
]

app_name = 'donations'

urlpatterns = [
    # Main pages
    path('', views.donation_page, name='donation_page'),
    path('success/<str:transaction_id>/', views.donation_success, name='donation_success'),
    
    # API endpoints
    path('api/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('api/mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('api/donation-stats/', views.get_donation_stats, name='donation_stats'),
]