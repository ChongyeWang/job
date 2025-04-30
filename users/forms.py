from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password(self):
        cd = self.cleaned_data
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        print(password2, password1)
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don’t match.')
        return password2
