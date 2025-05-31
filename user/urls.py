from django.urls import path
from .views import login_view, register_view, recover_view, profile_view,logout_view

app_name = 'user'

urlpatterns = [
    path('login/',    login_view,    name='login'),
    path('register/', register_view, name='register'),
    path('recover/',  recover_view,  name='recover'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'), 
    
]
