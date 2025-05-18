from django.urls import path
from . import views
from .views import  SignUpView, UserLoginView, ConfirmEmailView, PassChangeView, user_logout_view
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<str:uidb64>/<str:token>/', ConfirmEmailView.as_view(), name='activate'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),
    path('profile/pass_change/', PassChangeView.as_view(), name='pass_change'),
    path('logout/', user_logout_view, name='logout'),
]
