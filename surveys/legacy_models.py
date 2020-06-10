from django.db import models
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.validators import MaxValueValidator, MinValueValidator

import datetime
from django_countries.fields import CountryField

from django.contrib.auth.models import User

from website.models import Organization

from django.conf import settings
from django.utils.crypto import salted_hmac
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255, help_text='Name of the Product')
    short_description = models.CharField(max_length=255, blank=True, null=True, help_text='Short description of Product')

    def __str__(self):
        """String for representing the Product object (in Admin site etc.)."""
        return self.name


class ProductSetting(models.Model):
    is_active = models.BooleanField(default=True, help_text='This product is active for this organization')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, help_text='Organization this setting applies to')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Product this setting applies to')
    survey_interval = models.SmallIntegerField(default=90, help_text='How many days between each survey', validators=[MinValueValidator(0), MaxValueValidator(730)])
    last_survey_open = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Last opening date of survey with this product/prganization combo')
    last_survey_close = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Last closing date of survey with this product/prganization combo')
    surveys_remain_open_days = models.SmallIntegerField(default = 21, help_text='How many days should surveys be open for this organization', validators=[MinValueValidator(0), MaxValueValidator(365)])

class Employee(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, help_text='Organization where this Employee is employed')
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
    owner = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, help_text='Organization that owns this survey')
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
    completed = models.BooleanField(default=False, help_text='This SI has been completed')

    #uniqe_link_token? Use ID like we already do? with survey.pk and respondent.pk to salt, dont need db?
    def get_hash_string(self):
        hash_string = salted_hmac(
            "django.contrib.auth.tokens.PasswordResetTokenGenerator",
            urlsafe_base64_encode(force_bytes(10*self.respondent.email+str(self.pk+self.survey.pk+self.survey.product.pk)+self.respondent.email)),
            settings.SECRET_KEY,
        ).hexdigest()[::2]
        return hash_string

    def get_url_token(self):
        si = urlsafe_base64_encode(force_bytes(self.pk))
        s = urlsafe_base64_encode(force_bytes(self.pk))
        hash_string = self.get_hash_string()
        return "%s-%s"%(si, hash_string)

    def get_owner(self):
        return self.survey.owner

    def __str__(self):
        """String for representing the SurveyInstance object (in Admin site etc.)."""
        return 'SurveyInstance of Product: %s for Organization: %s.'%(self.survey.product.name, self.survey.owner.name)

class Question(models.Model):
    ''' Base model of a question '''
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text='Product that asks this question')
    active = models.BooleanField(default=True, help_text='Question is included in new Surveys')
    question_string = models.TextField(help_text='The question as it appears to the respondent')
    instruction_string = models.CharField(max_length=255, blank=True, null=True, default=None, help_text="Short text instructing how to answer the question")
    dimension = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        default=None,
        help_text='The dimension or category for this Question',
    )

    def answer(self, value, survey_instance):

        #print('Received an answer to a question')
        #print('The answer if of type %s'%(type(value)))
        #print('can i print self? %s'%(self))
        #print('can i print value, %s? and si, %s?'%(value, survey_instance))
        #check if an answer already exists for this Q for this SI, if so update that, else make new answer
        int_answer_list = IntAnswer.objects.filter(survey_instance=survey_instance, question=self)
        #print('found %s previous answers'%(int_answer_list.count()))
        if int_answer_list.count() > 0:
            #print("there was already an intanswer for this question: %s."%(int_answer_list[0]))
            a = int_answer_list[0]
            a.value=value
            a.save()
            #print("now it's %s."%(a))
            return

        txt_answer_list = TextAnswer.objects.filter(survey_instance=survey_instance, question=self)
        if txt_answer_list.count() > 0:
            #print("there was already a txtanswer for this question")
            a = txt_answer_list[0]
            a.value=value
            a.save()
            return

        #print("there was no answer for this q, let's make one")
        if type(value) == int:
            a=IntAnswer(value=value, survey_instance=survey_instance, question=self)
            #print(a)
            a.save()
        elif type(value) == str:
            a=TextAnswer(value=value, survey_instance=survey_instance, question=self)
            #print(a)
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
        return 'AnswerObject: with value %s, to question %s'%(str(self.value), self.question)

class IntAnswer(Answer):
    ''' Answer is an int'''
    value = models.IntegerField(help_text='The answer to the question (Integer)')

class TextAnswer(Answer):
    ''' Answer in a string of up to 10 000 characters'''
    value = models.TextField(help_text='The answer to the question (string of text)')
