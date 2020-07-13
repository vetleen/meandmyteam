from django import forms
from django.contrib.auth.models import User
from surveys.models import Respondent
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from surveys.models import SurveyInstanceItem, RatioSurveyInstanceItem



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

class EditSurveySettingsForm(forms.Form):

    is_active = forms.BooleanField(
        label="Activate tracking?",
        required=False,
        widget=forms.CheckboxInput(attrs={'default': 'true'})
    )
    survey_interval = forms.ChoiceField(
        label="How often should employees in your organization be surveyed?",
        required=True,
        choices=(
            (90, 'Every 3 months (reccomended)'),
            (180, 'Every 6 months'),
            (365, 'Every year'),
            )
    )
    surveys_remain_open_days = forms.ChoiceField(
        label="How much time should employees be given to answer a survey?",
        required=True,
        choices=(
            (7, 'One week (recommended)'),
            (14, 'Two weeks'),
            (21, 'Three weeks'),
            (30, 'One month'),
            )
    )
class CustomChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.min_value_description = kwargs.pop('min_value_description', 'Disagree')
        self.max_value_description = kwargs.pop('max_value_description', 'Agree')
        super(CustomChoiceField, self).__init__(*args, **kwargs)

class AnswerSurveyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        #self.user = kwargs.pop('user',None)
        self.items = kwargs.pop('items', None)

        assert self.items is not None, \
            "tried to instantiate AnswerSurveyForm without providing 'items'"
        assert isinstance(self.items, list), \
            "the 'items' variable provdided to AnswerSurveyForm must be a list but was %s."%(type(self.items))

        for item in self.items:
            assert isinstance(item, SurveyInstanceItem), \
                "survey_instance_items in 'items' provdided to AnswerSurveyForm must be of the type SurveyInstanceItem but at least one was %s:\n --- \"%s\"."\
                %(type(item), item)


        super(AnswerSurveyForm, self).__init__(*args, **kwargs)

        for item in self.items:
            field_name = 'item_%s'%(item.pk)
            if isinstance(item, RatioSurveyInstanceItem):
                CHOICES = [(number, str(number)) for number in range (item.survey_item.item_dimension.scale.min_value, item.survey_item.item_dimension.scale.max_value)]
                self.fields[field_name] = CustomChoiceField(
                    min_value_description = item.survey_item.item_dimension.scale.min_value_description,
                    max_value_description = item.survey_item.item_dimension.scale.max_value_description,
                    label=item.survey_item.item_formulation,
                    choices=CHOICES,
                    help_text=item.survey_item.item_dimension.scale.instruction,
                    label_suffix='',
                    widget=forms.RadioSelect(attrs={
                        'class': 'form-check-input'
                    })
                )

            #elif other types of scales
            else:
                logger.warning(
                    "%s %s: %s: tried to make a form field for the supplied item, but its subclass (%s) was not recognized:\n---\"%s\""\
                    %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, type(item), item)
                )
