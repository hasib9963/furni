from django.shortcuts import render
from Shop.models import Product
def home(request):
    data = Product.objects.all()
    return render(request, 'index.html', {'data': data})

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def service(request):
    data = Product.objects.all()
    return render(request, 'services.html', {'data': data})