from django.urls import path
from .views import  RegisterView, UserLoginView, ConfirmEmailView, user_logout_view
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
        path('activate/<str:uidb64>/<str:token>/', ConfirmEmailView.as_view(), name='activate'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout_view, name='logout'),
]
