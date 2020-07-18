from django.conf import settings
from django.db import models, IntegrityError
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.crypto import salted_hmac
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

#third party
from polymorphic.models import PolymorphicModel #https://django-polymorphic.readthedocs.io/en/latest/quickstart.html

#my stuff
from website.models import Organization


# Create your models here.

#Product components (Scale(s), Instrument, Dimension, Item)
class Scale(PolymorphicModel):
    '''
    The base class for scales. There can be many scales, such as a yes/no scale,
    or a 1-5 scale. This class handles all the commonalities, and then specific
    scales, such as RatioScale, will inherit from this to implement its
    peculiarities.
    '''
    name = models.CharField(max_length=255, unique=True, help_text='')
    instruction = models.CharField(max_length=255, blank=True, null=True, help_text='')
    opt_out = models.BooleanField(default=True, help_text='')

    def save(self, *args, **kwargs):
        if self.pk:
            original_self=Scale.objects.get(id=self.id)
            if original_self.name != self.name:
                raise IntegrityError(
                   "You may not change the 'name' of an existing %s object."%(self._meta.model_name)
               )
        super(Scale, self).save(*args, **kwargs)

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return self.name

class RatioScale(Scale):
    '''
    A scale or numbers where it makes sense to look at ratios, such as a 1-5
    scale of level of agreement. Averages makes sense and so on.
    '''
    min_value = models.SmallIntegerField(default=0, help_text='')
    max_value = models.SmallIntegerField(default=0, help_text='')
    min_value_description = models.CharField(max_length=255, blank=True, null=True, help_text='')
    max_value_description = models.CharField(max_length=255, blank=True, null=True, help_text='')

    def save(self, *args, **kwargs):
        if self.pk:
            original_self=Scale.objects.get(id=self.id)
            if original_self.min_value != self.min_value:
                raise IntegrityError(
                   "You may not change the 'min_value' of an existing %s object."%(self._meta.model_name)
               )
            if original_self.max_value != self.max_value:
                raise IntegrityError(
                   "You may not change the 'max_value' of an existing %s object."%(self._meta.model_name)
               )
        super(RatioScale, self).save(*args, **kwargs)

class Instrument(models.Model):
    '''
    Represents a scientific instrument to measure a particular object of
    interest, for example Employee Engagement. Instruments are the base products
    that customers choose to activate.
    '''
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, help_text='')
    slug_name = models.CharField(max_length=255, unique=True, blank=True, null=True, help_text='')
    description = models.CharField(max_length=255, blank=True, null=True, help_text='')

    def get_items(self):
        items = []
        for d in self.dimension_set.all():
            for i in d.item_set.all():
                items.append(i)
        return items

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return '(' + self.name + ')'

class Dimension(models.Model):
    '''
    A Dimension of a phonomenon of interest, measured by an Instrument. For
    example, the Employee Engagement Instrument may have the dimensions Vigor,
    Absorption and Dedication.
    '''
    instrument = models.ForeignKey(Instrument, blank=True, null=True, on_delete=models.SET_NULL, help_text='') #enables instrument.dimension_set.all()
    name = models.CharField(max_length=255, help_text='')
    description = models.TextField(blank=True, null=True, help_text='')

    #to make FK to Scale work, since there are different kinds of Scales
    content_type = models.ForeignKey(ContentType, blank=True, null=True, default=None, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField( blank=True, null=True, default=None)
    scale = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        ##Ensure some parameters cannot be changed
        if self.pk:
            original_self=Dimension.objects.get(id=self.id)
            if original_self.scale != self.scale:
                raise IntegrityError(
                   "You may not change the scale of an existing %s object, because existing SurveyItems may be using it."%(self._meta.model_name)
               )
            if original_self.name != self.name:
                raise IntegrityError(
                   "You may not change the name of an existing %s object, because self.name is used together with self.scale and self.instrument in product_configuration to see if a new Dimension needs to be made and attached to Instrument."%(self._meta.model_name)
               )
            if original_self.instrument != self.instrument:
                raise IntegrityError(
                   "You may not change the instrument of an %s object"%(self._meta.model_name)
               )
        #Ensure the GenericForeignKey for scale received a Scale or subclass thereof
        if not isinstance(self.scale, Scale):
            raise ValidationError(
                "The parameter 'scale' for a new Dimension must be an instance of Scale or one of it's subclasses, got (%(wrong_type)s).",
                code='invalid',
                params={'wrong_type': type(self.scale)}
            )
        #Ensure dimension names are unique per instrument
        if not self.pk:
            try:
                existing_d = Dimension.objects.get(instrument=self.instrument, name=self.name)
            except Dimension.DoesNotExist:
                existing_d = None
            if existing_d is not None:
                raise IntegrityError(
                   "You may not create a %s object called %s for the instrument %s. It already exists!"%(self._meta.model_name, self.name, self.instrument)
               )
        super(Dimension, self).save(*args, **kwargs)

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return '(' + self.name + ' in ' + self.instrument.name + ')'

class Item(models.Model):
    '''
    A concrete question or statement for Respondents to react to by scoring it.
    '''
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE, help_text='')
    formulation = models.TextField(help_text='')
    active = models.BooleanField(default=True, help_text='')
    inverted = models.BooleanField(default=False, help_text='')

    def save(self, *args, **kwargs):
        if self.pk:
            raise IntegrityError("You may not edit an existing %s object. Instead make a new one and attach that for future use" % self._meta.model_name)
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""

        return '%s: %s.'%(self.dimension.name, self.formulation)

#Someone to fill in the surveys
class Respondent(models.Model):
    '''
    A Respondent that has been added by the organization.owner, presumably  to
    fill out Surveys.
    '''
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, help_text='Organization where this Respondent is employed')
    first_name = models.CharField(max_length=255, blank=True, null=True, help_text='First name of Employee')
    last_name = models.CharField(max_length=255, blank=True, null=True, help_text='Last name of Respondent')
    email = models.EmailField(max_length=254, help_text='Email of Respondent')
    receives_surveys = models.BooleanField(default=True, help_text='This Respondent should receive surveys from the Organization')

    def uidb64(self):
        return urlsafe_base64_encode(force_bytes(self.pk))

    def __str__(self):
        """String for representing the Respondent object (in Admin site etc.)."""
        return self.email

#SURVEY COMPONENTS (Survey, SurveyItem(s))
class Survey(models.Model):
    '''
    A Survey object is created for an Organization based on a Product blueprint,
    and  Survey Instances are created for each Respondent the organization has
    set up to receive the Survey. At the end of a Survey, Survey Instances are
    closed for editing and final results are calculated. These results should be
    available to the Organization in the future.
    '''
    owner = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, help_text='Organization that owns this survey')
    #instrument =  models.ManyToManyField(Instrument, on_delete=Protect) #dont need this, we just need to know when we make it!
    date_open = models.DateField(auto_now=False, auto_now_add=False, help_text='The date from which this Survey may be answered')
    date_close = models.DateField(auto_now=False, auto_now_add=False, help_text='The date until which this Survey may be answered')
    n_invited = models.IntegerField(default=0, help_text='Number of respondents')
    n_completed = models.IntegerField(default=0, help_text='')
    n_incomplete = models.IntegerField(default=0, help_text='')
    n_not_started = models.IntegerField(default=0, help_text='')
    is_closed = models.BooleanField(default=False, help_text='This survey is finished forever')

    def get_items(self):
        '''
        As different kinds of items are implemented, just update this, and
        si.items() will always return all items of all kinds.
        '''
        ratio_items = RatioSurveyItem.objects.filter(survey=self)
        return [i for i in ratio_items]

    def uidb64(self):
        return urlsafe_base64_encode(force_bytes(self.pk))

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return '%s (%s to %s)'%(self.owner.name, self.date_open, self.date_close)

#Settings for surveys for a particular Organization
class SurveySetting(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, help_text='Organization this setting applies to')
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, help_text='Instruments this organization is using')
    is_active = models.BooleanField(default=False, help_text='This instrument is active for this organization')
    survey_interval = models.SmallIntegerField(default=90, help_text='How many days between each survey', validators=[MinValueValidator(0), MaxValueValidator(730)])
    surveys_remain_open_days = models.SmallIntegerField(default=7, help_text='How many days should surveys be open for this organization', validators=[MinValueValidator(0), MaxValueValidator(365)])
    last_survey_open = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Last opening date of survey with this product/prganization combo')
    last_survey_close = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Last closing date of survey with this product/prganization combo')
    surveys =  models.ManyToManyField(Survey, blank=True, help_text='')

    def check_last_survey_dates(self):
        last_open_survey = self.surveys.order_by('-date_open')[:1]
        last_close_survey = self.surveys.order_by('-date_close')[:1]
        if len(last_open_survey) > 0:
            self.last_survey_open = last_open_survey[0].date_open
        if len(last_close_survey) > 0:
            self.last_survey_close = last_close_survey[0].date_close
        self.save()

    def __str__(self):
        """String for representing the SurveySetting object (in Admin site etc.)."""
        return '(%s - %s)'%(self.organization, self.instrument)

    def save(self, *args, **kwargs):
        #Ensure SS is unique per organization and instrument
        if not self.pk:
            try:
                existing_ss = SurveySetting.objects.get(instrument=self.instrument, organization=self.organization)
            except SurveySetting.DoesNotExist:
                existing_ss = None
            if existing_ss is not None:
                raise IntegrityError(
                   "You may not create a %s object for the instrument %s, and organization %s. It already exists!"
                   %(self._meta.model_name, self.instrument, self.organization)
               )
        super(SurveySetting, self).save(*args, **kwargs)

class SurveyItem(PolymorphicModel):
    '''
    A SurveyItem is a question as it was (or should be) asked in a concrete
    Survey. It should be possible to interpret a SI even after the product is
    deleted.

    A SUBCLASS SHOULD ALWAYS BE USED!
    '''
    #common to all kinds of SurveyItems
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, null=True, help_text='Organization that owns this survey')
    item_formulation = models.TextField(blank=True, null=True,  help_text='A question or statement to confront Respondents with')
    item_inverted = models.BooleanField(default=False, help_text='')
    item_dimension = models.ForeignKey(Dimension, blank=True, null=True, on_delete=models.PROTECT, help_text='')
    n_answered = models.IntegerField(default=0, help_text='Number of respondents')

    def n_invited(self):
        return self.survey.n_invited

    def scale(self):
        return self.item_dimension.scale

    def save(self, *args, **kwargs):
        if self.pk:
            original_self = SurveyItem.objects.get(id=self.id)
            if original_self.survey != self.survey:
                raise IntegrityError(
                   "You may not change the 'survey' of an existing %s object."%(self._meta.model_name)
               )
            if original_self.item_formulation != self.item_formulation:
                raise IntegrityError(
                   "You may not change the 'item_formulation' of an existing %s object."%(self._meta.model_name)
               )
            if original_self.item_inverted != self.item_inverted:
                raise IntegrityError(
                   "You may not change the 'item_inverted' of an existing %s object."%(self._meta.model_name)
               )
            if original_self.item_dimension != self.item_dimension:
                raise IntegrityError(
                   "You may not change the 'item_dimension' of an existing %s object."%(self._meta.model_name)
               )
        super(SurveyItem, self).save(*args, **kwargs)

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return '((%s): (This is an instance of the SurveyItem base class, which shouldn\'t be used))'%(self.survey)

class RatioSurveyItem(SurveyItem):
    '''
    SurveyItems on a ratio scale, e.g. 1-7 or 1-100. These parameters allow
    interpretation and back tracking, even if scales where changed right after
    the survey was created.
    '''
    #Specific to ratio scaled SurveyItems
    average = models.FloatField(default=None, blank=True, null=True, help_text='Average of scores for this item in this survey')

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return '(%s): %s)'%(self.survey, self.item_formulation)

class DimensionResult(PolymorphicModel):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, null=True, help_text='Organization that owns this survey')
    dimension = models.ForeignKey(Dimension, on_delete=models.PROTECT, help_text='')
    n_completed = models.IntegerField(default=0, help_text='')

    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return 'Result of %s in %s'%(self.dimension, self.survey)

    def save(self, *args, **kwargs):
        ##Ensure some parameters cannot be changed
        if self.pk:
            original_self = DimensionResult.objects.get(id=self.id)
            if original_self.survey != self.survey:
                raise IntegrityError(
                   "You may not change the 'survey' of an existing %s object."%(self._meta.model_name)
               )
            if original_self.dimension != self.dimension:
                raise IntegrityError(
                   "You may not change the 'dimension' of an existing %s object."%(self._meta.model_name)
               )
        super(DimensionResult, self).save(*args, **kwargs)

class RatioScaleDimensionResult(DimensionResult):
    average = models.FloatField(default=None, blank=True, null=True, help_text='Average of scores for this dimension in this survey')


#SURVEY INSTANCE COMPONENTS (SurveyInstance, SurveyInstanceItem(s))
class SurveyInstance(models.Model):
    respondent = models.ForeignKey(Respondent, blank=True, null=True, on_delete=models.SET_NULL, help_text='')
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, help_text='')
    completed = models.BooleanField(default=False, help_text='')
    started = models.BooleanField(default=False, help_text='')


    def get_items(self):
        '''
        As different kinds of items are implemented, just update this, and
        si.items() will always return all items of all kinds.
        '''
        ratio_items = RatioSurveyInstanceItem.objects.filter(survey_instance=self)
        return [i for i in ratio_items]

    def check_completed(self):
        #was this already settled?
        if self.completed == True:
            return True

        #calculate if we must
        items = self.get_items()
        was_completed = True
        for item in items:
            if item.answered == False:
                was_completed = False
                break

        self.completed = was_completed
        self.save()

        #return answer
        return was_completed

    def get_hash_string(self):
        
        hash_string = salted_hmac(
            "django.contrib.auth.tokens.PasswordResetTokenGenerator",
            urlsafe_base64_encode(force_bytes(10*self.respondent.email+str(self.pk+self.survey.pk+self.survey.owner.pk)+self.respondent.email)),
            settings.SECRET_KEY,
        ).hexdigest()[::2]
        return hash_string

    def get_url_token(self):
        si = urlsafe_base64_encode(force_bytes(self.pk))
        s = urlsafe_base64_encode(force_bytes(self.pk))
        hash_string = self.get_hash_string()
        return "%s-%s"%(si, hash_string)

    def save(self, *args, **kwargs):
        ##Ensure some parameters cannot be changed
        if self.pk:
            original_self = SurveyInstance.objects.get(id=self.id)
            if original_self.respondent != self.respondent:
                raise IntegrityError(
                   "You may not change the 'respondent' of an existing %s object."%(self._meta.model_name)
               )
            if original_self.survey != self.survey:
                raise IntegrityError(
                   "You may not change the 'survey' of an existing %s object."%(self._meta.model_name)
               )
            if original_self.completed != self.completed and original_self.completed == True:
                print(self.completed)
                raise IntegrityError(
                   "You may not change the 'completed' attribute of an existing %s object back to False."%(self._meta.model_name)
               )
        super(SurveyInstance, self).save(*args, **kwargs)


class SurveyInstanceItem(PolymorphicModel):
    survey_instance = models.ForeignKey(SurveyInstance, on_delete=models.PROTECT, help_text='')
    answered = models.BooleanField(default=False, help_text='')

    def survey(self):
        return self.survey_instance.survey

    def respondent(self):
        return self.survey_instance.respondent

    def save(self, *args, **kwargs):
        ##Ensure some parameters cannot be changed
        if self.pk:
            original_self = SurveyInstanceItem.objects.get(id=self.id)
            if original_self.survey_instance != self.survey_instance:
                raise IntegrityError(
                   "You may not change the 'survey_instances' to which an existing %s object belongs."%(self._meta.model_name)
               )
        super(SurveyInstanceItem, self).save(*args, **kwargs)


class RatioSurveyInstanceItem(SurveyInstanceItem):
    survey_item = models.ForeignKey(RatioSurveyItem, on_delete=models.PROTECT, help_text='')
    answer =  models.SmallIntegerField(default=None, blank=True, null=True, help_text='')

    def formulation(self):
        return self.survey_item.item_formulation

    def dimension(self):
        return self.survey_item.item_dimension

    def answer_item(self, value):
        #answer the item
        self.answer = value
        self.answered = True
        self.save()
        #update status of survey_instance
        self.survey_instance.check_completed()
        if self.survey_instance.started == False:
            self.survey_instance.started == True
            self.survey_instance.save()

    def save(self, *args, **kwargs):
        ##Ensure some parameters cannot be changed
        if self.pk:
            original_self = RatioSurveyInstanceItem.objects.get(id=self.id)
            if original_self.survey_item != self.survey_item:
                raise IntegrityError(
                   "You may not change the 'survey_item' of an existing %s object."%(self._meta.model_name)
               )
        super(RatioSurveyInstanceItem, self).save(*args, **kwargs)

class RespondentEmail(models.Model):
    survey_instance = models.ForeignKey(SurveyInstance,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=''
    )
    email_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        blank=True,
        null=True,
        help_text=''
    )
    ALLOWED_CATEGORIES = ['initial', 'reminder', 'last_chance', 'failure']
    category = models.CharField(
        max_length=255,
        help_text=''
    )
    error_message = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=''
    )
    def save(self, *args, **kwargs):
        #Ensure type is always an ALLOWED_TYPE
        if self.category not in self.ALLOWED_CATEGORIES:
            raise ValueError(
               "'type' must be on of %s, but was %s."%(ALLOWED_CATEGORIES, self.type)
            )
        super(RespondentEmail, self).save(*args, **kwargs)
