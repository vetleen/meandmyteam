from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email

from django.contrib import messages

class SignUpForm(forms.Form):
    username = forms.EmailField(max_length = 150, label="Email address", widget=forms.TextInput(attrs={'type':'input'}))
    password = forms.CharField(max_length = 20, label="Choose a password", widget=forms.PasswordInput(attrs={'type':'password'}))
    confirm_password = forms.CharField(max_length = 20, label="Confirm password", widget=forms.PasswordInput(attrs={'type':'password'}))

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(
                "A user with the email already exist (%(taken_email)s).",
                code='invalid',
                params={'taken_email': self.cleaned_data['username']}
            )
        return self.cleaned_data['username']

    def clean_password(self):
        #logic to validate password. Length and comp?
        if len(self.cleaned_data['password']) < 3:
           raise forms.ValidationError(
                "The password must be atleast 3 characters long. Please try again.",
               code='invalid',
                )
        return self.cleaned_data['password']

    def clean_confirm_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
           raise forms.ValidationError(
                "The second password you entered did not match the first. Please try again.",
               code='invalid',
                )
        return self.cleaned_data['confirm_password']

class ChangePasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
         self.user = kwargs.pop('user',None)
         super(ChangePasswordForm, self).__init__(*args, **kwargs)

    old_password = forms.CharField(max_length = 20, label="Current password",widget=forms.PasswordInput(attrs={'type':'password', 'placeholder':'Old Password'}))
    new_password = forms.CharField(max_length = 20, label="Enter a new password",widget=forms.PasswordInput(attrs={'type':'password', 'placeholder':'New Password'}))
    confirm_new_password = forms.CharField(max_length = 20, label="Confirm new password", widget=forms.PasswordInput(attrs={'type':'password', 'placeholder':'Confirm New Password'}))

    def clean_old_password(self):
        if not self.user.check_password(self.cleaned_data['old_password']):
            raise forms.ValidationError(
                "Wrong password.", #I think the benefit in user-friendlyness of this error message outweights the potential security risk
                code='invalid',
                params={}
            )
        return self.cleaned_data['old_password']

    def clean_new_password(self):
        #same validation here as in that other form?
        return self.cleaned_data['new_password']

    def clean_confirm_new_password(self):
        if 'new_password' in self.cleaned_data and 'confirm_new_password' in self.cleaned_data:
            if self.cleaned_data['new_password'] != self.cleaned_data['confirm_new_password']:
                raise forms.ValidationError(
                    "The second new password you entered did not match the first. Please try again.",
                    code='invalid',
                    )
        return self.cleaned_data['confirm_new_password']

class LoginForm(forms.Form):
    username = forms.EmailField(max_length = 150, label="Email address", widget=forms.TextInput(attrs={'type':'input'}))
    password = forms.CharField(max_length = 20, label="Password", widget=forms.PasswordInput(attrs={'type':'password'}))

    def clean_username(self):
        if not User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(
                "There is no user with that email (%(attempted)s).", #I think the benefit in user-friendlyness of this error message outweights the potential security risk
                code='invalid',
                params={'attempted': self.cleaned_data['username']}
            )
        return self.cleaned_data['username']

    def clean_password(self):
        try:
            if not User.objects.get(username=self.cleaned_data['username']).check_password(self.cleaned_data['password']):
                raise forms.ValidationError(
                    "Wrong password.", #I think the benefit in user-friendlyness of this error message outweights the potential security risk
                    code='invalid',
                    params={}
                )
        except:
            raise forms.ValidationError(
                "Please enter the password again.", #this means that there was no user to test password against
                code='invalid',
                params={}
            )

        #logic here once I figure out how to access User object here. Suspect it has something to do with ___init__ of the form...
        return self.cleaned_data['password']

    def clean(self):
        return self.cleaned_data

class EditAccountForm(forms.Form):
    def __init__(self, *args, **kwargs):
         self.user = kwargs.pop('user',None)
         super(EditAccountForm, self).__init__(*args, **kwargs)

    username = forms.EmailField(max_length = 150, label="Email address", help_text="Your email is also your username.", widget=forms.TextInput(attrs={'type':'email'}))

    def clean_username(self):
        #once i figure out how to check User object from here i will also add a separate validation error for trying to change to ones own existing.
        if self.cleaned_data['username'] == self.user.username:
            raise forms.ValidationError(
                "Your email is already set to %(existing_email)s.", #user-friendlyness outweights potential security concern
                code='invalid',
                params={'existing_email': self.cleaned_data['username']}
            )
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(
                "A user with the email already exist (%(taken_email)s).", #user-friendlyness outweights potential security concern
                code='invalid',
                params={'taken_email': self.cleaned_data['username']}
            )
        return self.cleaned_data['username']
