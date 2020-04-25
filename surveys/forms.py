from django import forms
from django.contrib.auth.models import User
from surveys.models import Organization, Employee


class CreateOrganizationForm(forms.Form):
    def __init__(self, *args, **kwargs):
         self.user = kwargs.pop('user',None)
         super(CreateOrganizationForm, self).__init__(*args, **kwargs)

    name = forms.CharField(max_length = 255, label="Organization name", widget=forms.TextInput(attrs={}))
    address_line_1 = forms.CharField(max_length = 255, label="Address", required=False,widget=forms.TextInput(attrs={}))
    address_line_2 =forms.CharField(max_length = 255, label="Address contd.", required=False, widget=forms.TextInput(attrs={}))
    zip_code = forms.CharField(max_length = 20, label="Zip", widget=forms.TextInput(attrs={}))
    city = forms.CharField(max_length = 255, label="City", required=False, widget=forms.TextInput(attrs={}))
    country = forms.CharField(max_length = 255, label="Country", widget=forms.TextInput(attrs={}))

    def clean_name(self):
        if Organization.objects.filter(name=self.cleaned_data['name']).exists():
            raise forms.ValidationError(
                "An organization with that name already exists (%(taken_name)s).",
                code='invalid',
                params={'taken_name': self.cleaned_data['name']}
            )
        return self.cleaned_data['name']

class AddEmployeeForm(forms.Form):
    email = forms.EmailField(max_length = 150, label="Email address", widget=forms.TextInput(attrs={'placeholder': 'Required'}))
    first_name = forms.CharField(max_length = 255, label="First name", required=False, widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    last_name = forms.CharField(max_length = 255, label="Last name", required=False, widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    #receives_surveys = forms.BooleanField(label="Send surveys to this employee", required=False, widget=forms.CheckboxInput(attrs={'default': 'true'}))

    def clean_email(self):
        if Employee.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(
                "A coworker with that email already exists (%(taken_email)s).",
                code='invalid',
                params={'taken_email': self.cleaned_data['email']}
            )
        return self.cleaned_data['email']
