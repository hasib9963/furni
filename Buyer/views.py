from django.shortcuts import  redirect, get_object_or_404
from django.views.generic.edit import FormView
from .forms import SignUpForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.views import LoginView
from django.http import JsonResponse

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from django.template.loader import render_to_string
from django.core.mail import  EmailMultiAlternatives
from django.views import View
from django.http import HttpResponse
# Create your views here.

class SignUpView(FormView):
    template_name = 'signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Send activation email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # confirm_link = f"http://127.0.0.1:8000/activate/{uid}/{token}/"
        confirm_link = f"https://furni-qnpo.onrender.com/activate/{uid}/{token}/"

        email_subject = "Account Activation"
        email_body = render_to_string('confirmation_email.html', {
            'user': user,
            'confirm_link': confirm_link
        })

        email = EmailMultiAlternatives(email_subject, '', to=[user.email])
        email.attach_alternative(email_body, "text/html")
        email.send()

        # Handle AJAX response
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Account created successfully! Please check your email to activate account.',
                'redirect_url': str(self.success_url)
            })

        # Non-AJAX fallback
        messages.success(self.request, 'Account created successfully! Please check your email to activate account.')
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class ConfirmEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(get_user_model(), pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse("Your account has been activated successfully. You can login Now")
        else:
            return HttpResponse("Invalid activation link.")



# class UserLoginView(LoginView):
#     template_name = 'login.html'
#     form_class = AuthenticationForm

#     def form_invalid(self, form):
#         if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#         messages.error(self.request, "Invalid username or password")
#         return super().form_invalid(form)

#     def form_valid(self, form):
#         """Login and return JSON on AJAX or normal redirect otherwise"""
#         response = super().form_valid(form)
#         if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Login successful!',
#                 'redirect_url': self.get_success_url()
#             })
#         return response

#     def get_success_url(self):
#         return reverse_lazy('home')  # Change this to your dashboard/home


from .forms import CustomAuthenticationForm

class UserLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomAuthenticationForm

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Login successful!',
                'redirect_url': self.get_success_url()
            })
        return response

    def get_success_url(self):
        return reverse_lazy('home')

def user_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect(reverse_lazy('home'))

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from Shop.models import Order

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # or whatever field
    return render(request, 'profile.html', {'profile': profile, 'orders': orders})


@login_required
def edit_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        # Manually update both user and profile
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        profile.mobile = request.POST.get('mobile')
        profile.address = request.POST.get('address')
        profile_image = request.FILES.get('image')
        if profile_image:
            profile.profile_image = profile_image
        profile.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Your Profile Updated Successfully'}, status=200)
        
        messages.success(request, 'Your Profile Updated Successfully')
        return redirect('profile')
    
    return render(request, 'edit_profile.html', {'user': user, 'profile': profile})


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

class PassChangeView(View):
    template_name = 'password_change.html'

    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your Password Updated Successfully')

            # Send email to the user
            mail_subject = 'Password Change Notification'
            message = render_to_string('password_change_message.html', {'user': request.user})
            to_email = request.user.email
            send_email = EmailMultiAlternatives(mail_subject, '', to=[to_email])
            send_email.attach_alternative(message, "text/html")
            send_email.send()

            update_session_auth_hash(request, form.user)
            return redirect('profile')

        return render(request, self.template_name, {'form': form})