from django.db import models
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.validators import MaxValueValidator, MinValueValidator

import datetime
from django.contrib.auth.models import User
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255, help_text='Name of the Product')
    short_description = models.CharField(max_length=255, blank=True, null=True, help_text='Short description of Product')

    def __str__(self):
        """String for representing the Product object (in Admin site etc.)."""
        return self.name

class Organization(models.Model):
    owner = models.OneToOneField(User, blank=True, null=True, on_delete=models.PROTECT, help_text='User who owns this Organization')
    name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the Organization')
    active_products = models.ManyToManyField(Product, blank=True, help_text='Products this organization is currently using')
    address_line_1 = models.CharField(max_length=255, blank=True, null=True, help_text='Adress of the Organization')
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, help_text='Address contd.')
    zip_code =  models.CharField(max_length=255, blank=True, null=True, help_text='Zip code of the Organization')
    city =  models.CharField(max_length=255, blank=True, null=True, help_text='City where the Organization is located')
    country =  models.CharField(max_length=255, blank=True, null=True, help_text='Country where the Organization is located')
    surveys_remain_open_days = models.SmallIntegerField(default = 21, help_text='How many days should surveys be open for this organization', validators=[MinValueValidator(0), MaxValueValidator(365)])

    ##Todo
    #Add support for other Users than owner to be allowed to change organization
    def __str__(self):
        """String for representing the Organization object (in Admin site etc.)."""
        return self.name

class ProductSetting(models.Model):
    is_active = models.BooleanField(default=True, help_text='This product is active for this organization')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, help_text='Organization this setting applies to')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Product this setting applies to')
    survey_interval = models.SmallIntegerField(default=90, help_text='How many days between each survey', validators=[MinValueValidator(0), MaxValueValidator(730)])
    last_survey_open = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Last opening date of survey with this product/prganization combo')
    last_survey_close = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Last closing date of survey with this product/prganization combo')

class Employee(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, help_text='Organization where this Employee is employed')
    email = models.EmailField(max_length=254, help_text='Email of employee')
    first_name = models.CharField(max_length=255, blank=True, null=True, help_text='First name of Employee')
    last_name = models.CharField(max_length=255, blank=True, null=True, help_text='Last name of Employee')
    receives_surveys = models.BooleanField(default=True, help_text='This Employee should receive surveys from the Organization')

    def uidb64(self):
        return urlsafe_base64_encode(force_bytes(self.pk))

    def __str__(self):
        """String for representing the Employee object (in Admin site etc.)."""
        return self.email

class Survey(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, help_text='Questions asked in this survey')
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE, help_text='Organization that owns this survey')
    date_open = models.DateField(auto_now=False, auto_now_add=False, help_text='The date from which this Survey may be answered')
    date_close = models.DateField(auto_now=False, auto_now_add=False, help_text='The date until which this Survey may be answered')
    def __str__(self):
        """String for representing the Survey object (in Admin site etc.)."""
        return 'Survey: ' + self.product.name

class SurveyInstance(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, help_text='Survey that this instance is an instance of')
    respondent = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, help_text='Employee who answered this SurveyInstance')
    sent_initial = models.BooleanField(default=False, help_text='This SI has been sent once, the initial time')
    last_reminder = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Last reminder was sent')


    def __str__(self):
        """String for representing the SurveyInstance object (in Admin site etc.)."""
        return 'SurveyInstance of Product: %s for Organization: %s.'%(self.survey.product.name, self.survey.owner.name)

class Question(models.Model):
    ''' Base model of a question '''
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Product that asks this question')
    active = models.BooleanField(default=True, help_text='Question is included in new Surveys')
    question_string = models.TextField(help_text='The question as it appears to the respondent')
    dimension = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        default=None,
        help_text='The dimension or category for this Question',
    )

    def answer(value):
        print('Received and answer to a question')
        print('The answer if of type %s'%(type(value)))
        if type(value) == int:
            a=IntAnswer(value)
            a.save()
        elif type(value) == str:
            a=TextAnswer(value)
            a.save()
        else:
            raise TypeError('Answers must be strings or integers at this point')

    def __str__(self):
        """String for representing the Question object (in Admin site etc.)."""
        return self.question_string

class Answer(models.Model):
    survey_instance = models.ForeignKey(SurveyInstance, on_delete=models.PROTECT, help_text='The SurveyInstance where this answer given')
    question = models.ForeignKey(Question, on_delete=models.PROTECT, help_text='The Question this Answer answers')

    class Meta:
        abstract = True

    def __str__(self):
        """String for representing the Answer object (in Admin site etc.)."""
        return self.value

class IntAnswer(Answer):
    ''' Answer is an int'''
    value = models.IntegerField(help_text='The answer to the question (Integer)')

class TextAnswer(Answer):
    ''' Answer in a string of up to 10 000 characters'''
    value = models.TextField(help_text='The answer to the question (string of text)')
