from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'id' : 'required'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'id' : 'required'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']



from django.contrib.auth.forms import AuthenticationForm
class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username)
                if not user.check_password(password):
                    raise forms.ValidationError(
                        "Please enter a correct username and password. Note that both fields may be case-sensitive",
                        code='invalid_login',
                    )
                if not user.is_active:
                    raise forms.ValidationError(
                        "Please activate your account first.",
                        code='inactive',
                    )
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "Please enter a correct username and password. Note that both fields may be case-sensitive",
                    code='invalid_login',
                )

        return super().clean()
