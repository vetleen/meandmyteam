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
            if not Organization.objects.get(name=self.cleaned_data['name']).owner == self.user:
                print ('Compared %s with %s'%(Organization.objects.get(name=self.cleaned_data['name']).owner, self.user))
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

class EditEmployeeForm(forms.Form):
    email = forms.EmailField(max_length = 150, label="Email address", widget=forms.TextInput(attrs={'placeholder': 'Required'}))
    first_name = forms.CharField(max_length = 255, label="First name", required=False, widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    last_name = forms.CharField(max_length = 255, label="Last name", required=False, widget=forms.TextInput(attrs={'placeholder': 'Optional'}))
    #receives_surveys = forms.BooleanField(label="Send surveys to this employee", required=False, widget=forms.CheckboxInput(attrs={'default': 'true'}))

    def clean_email(self):
        return self.cleaned_data['email']

class ConfigureEmployeeSatisfactionTrackingForm(forms.Form):
    is_active = forms.BooleanField(label="Co-worker satisfaction tracking ON?", required=False, widget=forms.CheckboxInput(attrs={'default': 'true'}))
    INTERVAL_CHOICES = (
        (90, 'Every 3 months'),
        (180, 'Every 6 months'),
        (365, 'Every year'),

            )
    survey_interval = forms.ChoiceField(label="How often should co-workers in your organization be surveyed?", required=True, choices=INTERVAL_CHOICES)
    #surveys_remain_open_days =

class AnswerQuestionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        #self.user = kwargs.pop('user',None)
        self.questions = kwargs.pop('questions',None)
        super(AnswerQuestionsForm, self).__init__(*args, **kwargs)

        CHOICES = [
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')]

        for q in self.questions:
            field_name= 'question_%s'%(q.pk)
            self.fields[field_name] = forms.ChoiceField(
                label=q.question_string,
                choices=CHOICES,
                help_text=q.instruction_string,
                widget=forms.RadioSelect(attrs={
                    'class': 'form-check-input'
                })
            )
