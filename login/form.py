from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import authenticate, login, get_user_model, logout
from .models import UserProfilename
from django.contrib.auth.models import User


class UserLoginForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        # print (username, password)
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This User does not exit")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect Password")
            if not user.is_active:
                raise forms.ValidationError("This User is not active.")
        return super(UserLoginForm, self).clean()


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(label="Username")
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    email = forms.EmailField(label="Email")
    email2 = forms.EmailField(label="Confirm Email")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name', 
            'last_name',
            'email',
            'email2',
            'password',
            'confirm_password'
        ]

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email != email2:
            raise forms.ValidationError("Emails does not match")
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError("Email has already been registered")

        return super(UserRegisterForm, self).clean(*args, **kwargs)



class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )

# class OutputDocumentForm(forms.Form):
#     output_file = forms.FileField(
#         label='Select a file'
#     )
