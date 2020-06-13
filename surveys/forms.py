from django import forms
from django.contrib.auth.models import User
from surveys.models import Respondent
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField



class AddRespondentForm(forms.Form):
    email = forms.EmailField(max_length = 150, label="Email address", widget=forms.TextInput(attrs={'placeholder': 'Required'}))
    first_name = forms.CharField(max_length = 255, label="First name", required=False, widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    last_name = forms.CharField(max_length = 255, label="Last name", required=False, widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    #receives_surveys = forms.BooleanField(label="Send surveys to this employee", required=False, widget=forms.CheckboxInput(attrs={'default': 'true'}))

    def clean_email(self):
        if Respondent.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(
                "An employee with that email already exists (%(taken_email)s).",
                code='invalid',
                params={'taken_email': self.cleaned_data['email']}
            )
        return self.cleaned_data['email']


class EditRespondentForm(AddRespondentForm):
    def __init__(self, *args, **kwargs):
         self.respondent_id = kwargs.pop('respondent_id', None)
         super(EditRespondentForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        if Respondent.objects.filter(email=self.cleaned_data['email']).exists():
            existing_respondent = Respondent.objects.get(email=self.cleaned_data['email'])
            if  existing_respondent.id != self.respondent_id:
                raise forms.ValidationError(
                    "An employee with that email already exists (%(taken_email)s).",
                    code='invalid',
                    params={'taken_email': self.cleaned_data['email']}
                )
        return self.cleaned_data['email']
