from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from surveys.models import Respondent
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from surveys.models import SurveyInstanceItem, RatioSurveyInstanceItem


class AddRespondentForm(forms.Form):
    email = forms.EmailField(max_length = 150, label=_("Email address"), widget=forms.TextInput(attrs={'placeholder': _('Required')}))
    first_name = forms.CharField(max_length = 255, label=_("First name"), required=False, widget=forms.TextInput(attrs={'placeholder': _('Optional')}))
    last_name = forms.CharField(max_length = 255, label=_("Last name"), required=False, widget=forms.TextInput(attrs={'placeholder': _('Optional')}))
    #receives_surveys = forms.BooleanField(label="Send surveys to this employee", required=False, widget=forms.CheckboxInput(attrs={'default': 'true'}))

    def clean_email(self):
        if Respondent.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(
                _("An employee with that email already exists in our database (%(taken_email)s)."),
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
                    _("An employee with that email already exists in our database (%(taken_email)s)."),
                    code='invalid',
                    params={'taken_email': self.cleaned_data['email']}
                )
        return self.cleaned_data['email']

class EditSurveySettingsForm(forms.Form):

    is_active = forms.BooleanField(
        label=_("Activate tracking?"),
        required=False,
        widget=forms.CheckboxInput(attrs={'default': 'true'})
    )
    survey_interval = forms.ChoiceField(
        label=_("How often should employees in your organization be surveyed?"),
        required=True,
        choices=(
            (90, _('Every 3 months (reccomended)')),
            (180, _('Every 6 months')),
            (365, _('Every year')),
            )
    )
    surveys_remain_open_days = forms.ChoiceField(
        label=_("How much time should employees be given to answer a survey?"),
        required=True,
        choices=(
            (7, _('One week (recommended)')),
            (14, _('Two weeks')),
            (21, _('Three weeks')),
            (30, _('One month')),
            )
    )

class ConsentToAnswerForm(forms.Form):
    consent_to_answer = forms.BooleanField(
        label=_("I consent to the collection of information in this survey"),
        required=True,
        widget=forms.CheckboxInput(attrs={'default': 'false'})
    )
    def clean_consent_to_answer(self):
        if self.cleaned_data['consent_to_answer'] != True:
            raise forms.ValidationError(
                _("Please indicate that you consent to answer this survey to continue."),
                code='invalid',
                params={'consent_to_answer': self.cleaned_data['consent_to_answer']}
            )
        return self.cleaned_data['consent_to_answer']

class CustomChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.min_value_description = kwargs.pop('min_value_description', _('Disagree'))
        self.max_value_description = kwargs.pop('max_value_description', _('Agree'))
        self.opt_out = kwargs.pop('opt_out', False)
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
                CHOICES = [(number, str(number)) for number in range (item.survey_item.item_dimension.scale.min_value, item.survey_item.item_dimension.scale.max_value+1)]
                if item.survey_item.item_dimension.scale.opt_out == True:
                    CHOICES.append(("chose_to_not_answer", _("I don't know, or I don't want to answer")))
                
                self.fields[field_name] = CustomChoiceField(
                    min_value_description = item.survey_item.item_dimension.scale.min_value_description,
                    max_value_description = item.survey_item.item_dimension.scale.max_value_description,
                    opt_out = item.survey_item.item_dimension.scale.opt_out,
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
