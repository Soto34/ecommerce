from django.shortcuts import render


def home(request):
    return render(request,'home/index.html')

def custom_page_not_found(request):
    return render(request,'home/404.html', status=404)