from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import password_validation

from website.models import Organization

from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.validators import validate_international_phonenumber

class SignUpForm(forms.Form):
    #User
    username = forms.EmailField(max_length = 150, label="Email address", widget=forms.TextInput(attrs={'type':'input'}))
    password = forms.CharField(max_length = 20, label="Choose a password", widget=forms.PasswordInput(attrs={'type':'password'}))
    confirm_password = forms.CharField(max_length = 20, label="Confirm password", widget=forms.PasswordInput(attrs={'type':'password'}))

    #Organization
    name = forms.CharField(max_length = 255, label="Organization name*", widget=forms.TextInput(attrs={}))
    phone = PhoneNumberField(max_length=30, required=False, label="Phone incl.country code (e.g. +01 for USA)", widget=forms.TextInput(attrs={'placeholder':'[+][country code][your number]'}))
    address_line_1 = forms.CharField(max_length = 255, label="Street address*", widget=forms.TextInput(attrs={}))
    address_line_2 =forms.CharField(max_length = 255, label="", required=False, widget=forms.TextInput(attrs={}))
    zip_code = forms.CharField(max_length = 20, label="Zip*", widget=forms.TextInput(attrs={}))
    city = forms.CharField(max_length = 255, label="City", required=False, widget=forms.TextInput(attrs={}))
    country = CountryField(blank_label='(Select country)').formfield(label="Country*")
    accepted_terms_and_conditions = forms.BooleanField(
        label="I accept the terms and conditions and the privacy policy.",
        required=False,
        widget=forms.CheckboxInput(attrs={'default': 'false'})
    )

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(
                "A user with the email already exist (%(taken_email)s).",
                code='invalid',
                params={'taken_email': self.cleaned_data['username']}
            )
        return self.cleaned_data['username']

    def clean_password(self):
        #clean password
        try:
            password_validation.validate_password(self.cleaned_data['password'])
        except ValidationError as err:
            raise forms.ValidationError(err)
        return self.cleaned_data['password']

    def clean_confirm_password(self):
        if self.data.get('password') != self.cleaned_data['confirm_password']:
           raise forms.ValidationError(
                "The second password you entered did not match the first. Please try again.",
               code='invalid',
                )
        return self.cleaned_data['confirm_password']

    def clean_name(self):
        if Organization.objects.filter(name=self.cleaned_data['name']).exists():
            raise forms.ValidationError(
                "An organization with that name already exists (%(taken_name)s).",
                code='invalid',
                params={'taken_name': self.cleaned_data['name']}
            )
        return self.cleaned_data['name']

    def clean_phone(self):
        try:
            validate_international_phonenumber(self.cleaned_data['phone'])
        except ValidationError as err:
            raise forms.ValidationError(err)
        return self.cleaned_data['phone']

    def clean_accepted_terms_and_conditions(self):
        if self.cleaned_data['accepted_terms_and_conditions'] != True:
            raise forms.ValidationError(
                "Please indicate that you accept the terms and conditions.",
                code='invalid',
                params={'accepted_terms_and_conditions': self.cleaned_data['accepted_terms_and_conditions']}
            )
        return self.cleaned_data['accepted_terms_and_conditions']




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

class ResetPasswordForm(forms.Form):
    username = forms.EmailField(max_length = 150, label="Email address", widget=forms.TextInput(attrs={'type':'input'}))

    def clean_username(self):
        if not User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(
                "There is no user with that email (%(attempted)s).", #I think the benefit in user-friendlyness of this error message outweights the potential security risk
                code='invalid',
                params={'attempted': self.cleaned_data['username']}
            )
        return self.cleaned_data['username']

    def clean(self):
        return self.cleaned_data

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
        return self.cleaned_data['password']

    def clean(self):
        return self.cleaned_data

class EditAccountForm(forms.Form):
    def __init__(self, *args, **kwargs):
         self.user = kwargs.pop('user',None)
         super(EditAccountForm, self).__init__(*args, **kwargs)
    #User
    username = forms.EmailField(max_length = 150, label="Email address", help_text="Your email is also your username.", widget=forms.TextInput(attrs={'type':'email'}))

    #Organization
    name = forms.CharField(max_length = 255, label="Organization name", widget=forms.TextInput(attrs={}))
    phone = PhoneNumberField(max_length=30, required=False, label="Phone incl.country code (e.g. +01)", widget=forms.TextInput(attrs={'placeholder':'Example: +12125552368'})) # widget=PhoneNumberPrefixWidget(attrs={})

    address_line_1 = forms.CharField(max_length = 255, label="Street address", widget=forms.TextInput(attrs={}))
    address_line_2 =forms.CharField(max_length = 255, label="", required=False, widget=forms.TextInput(attrs={}))
    zip_code = forms.CharField(max_length = 20, label="Zip", widget=forms.TextInput(attrs={}))
    city = forms.CharField(max_length = 255, label="City", required=False, widget=forms.TextInput(attrs={}))
    country = CountryField(blank_label='(Select country)').formfield(label="Country")

    def clean_name(self):
        pre_existing_org = None
        try:
            pre_existing_org = Organization.objects.get(name=self.cleaned_data['name'])
        except Organization.DoesNotExist as err:
            pass
        if pre_existing_org is not None:
            if pre_existing_org.owner != self.user:
                #print ('Compared %s with %s'%(pre_existing_org.owner, self.user))
                raise forms.ValidationError(
                    "An organization with that name already exists (%(taken_name)s).",
                    code='invalid',
                    params={'taken_name': self.cleaned_data['name']}
                )
        return self.cleaned_data['name']

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists() and self.cleaned_data['username'] != self.user.username:
            raise forms.ValidationError(
                "A user with the email already exist (%(taken_email)s).", #user-friendlyness outweights potential security concern
                code='invalid',
                params={'taken_email': self.cleaned_data['username']}
            )
        return self.cleaned_data['username']


class ChoosePlanForm(forms.Form):
    chosen_plan = forms.CharField(max_length = 50)

    def clean_chosen_plan(self):
        return self.cleaned_data['chosen_plan']
class CancelPlanForm(forms.Form):
    cancel_plan = forms.BooleanField(required=True)

    def clean_cancel_plan(self):
        return self.cleaned_data['cancel_plan']
