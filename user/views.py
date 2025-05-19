from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def recover_view(request):
    return render(request, 'recover.html')
