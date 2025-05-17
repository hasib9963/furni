from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Contact
from django.http import JsonResponse
# Create your views here.


def contact(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the data
        Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            message=message
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Your message has been sent!'})

        return render(request, 'contact.html', {'success': True})

    return render(request, 'contact.html')

