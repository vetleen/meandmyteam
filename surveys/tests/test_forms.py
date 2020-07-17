from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

#my stuff
from surveys.models import *
from surveys.forms import *
from surveys.core import survey_logic

#third party
from datetime import date, timedelta



#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.
class FormsTest(TestCase):
    ''' TESTS THAT THE ANSWER SURVEY VIEW BEHAVES PROPERLY '''
    def setUp(self):
        o = Organization(owner=None)
        o.save()
        r = Respondent(organization=o, email="uniqueemail@test.tt", receives_surveys=True)
        r.save()


    def test_AddRespondentForm(self):
        #test: make and test a simple valid form
        data = {
            'email': "valid@email.com",
            'first_name': None,
            'last_name': None
        }
        test_form = AddRespondentForm(data=data)
        #print(dir(test_form))
        self.assertTrue(test_form.is_valid())


        #Test: try a valid form with more data
        data2 = {
            'email': "valid@email.com",
            'first_name': "Valid",
            'last_name': "Nameson"
        }
        test_form2 = AddRespondentForm(data=data2)
        self.assertTrue(test_form2.is_valid())


        #Test: try an invalid form
        data3 = {
            'email': None,
            'first_name': "Valid",
            'last_name': "Nameson"
        }
        test_form3 = AddRespondentForm(data=data3)

        self.assertFalse(test_form3.is_valid())
        self.assertTrue(test_form3.has_error('email'))
        self.assertFalse(test_form3.has_error('first_name'))
        self.assertFalse(test_form3.has_error('last_name'))
        self.assertIn("This field is required.", test_form3.errors['email'])

        #print(dir(test_form3))

        #Test an invalid form where the email is already taken
        previous_r = Respondent.objects.get(id=1)

        data4 = {
            'email': previous_r.email,
            'first_name': None,
            'last_name': None
        }
        test_form4 = AddRespondentForm(data=data4)

        self.assertFalse(test_form4.is_valid())
        self.assertTrue(test_form4.has_error('email'))
        self.assertIn("An employee with that email already exists (%s)."%(previous_r.email), test_form4.errors['email'])

        #test a form that should be invalid because email must be an email-address
        data5 = {
            'email': "Beetlejuice",
            'first_name': None,
            'last_name': None
        }
        test_form5 = AddRespondentForm(data=data5)
        self.assertFalse(test_form5.is_valid())
        self.assertTrue(test_form5.has_error('email'))
        self.assertIn("Enter a valid email address.", test_form5.errors['email'])

    def test_EditRespondentForm(self):
        #test: make and test a simple valid form
        data = {
            'email': "valid@email.com",
            'first_name': None,
            'last_name': None
        }
        test_form = EditRespondentForm(data=data)
        self.assertTrue(test_form.is_valid())

        #test: should be invalid because no respondent_id is passed in, but the email is already taken
        previous_r = Respondent.objects.get(id=1)
        data2 = {
            'email': previous_r.email,
            'first_name': None,
            'last_name': None
        }
        test_form2 = EditRespondentForm(data=data2)
        self.assertFalse(test_form2.is_valid())
        self.assertIn("An employee with that email already exists (%s)."%(previous_r.email), test_form2.errors['email'])

        #test: should be valid with correct respondent_id
        previous_r = Respondent.objects.get(id=1)
        data3 = {
            'email': previous_r.email,
            'first_name': None,
            'last_name': None
        }
        test_form3 = EditRespondentForm(data=data3, respondent_id=1)
        self.assertTrue(test_form3.is_valid())

    def test_EditSurveySettingsForm(self):
        #test: make and test a simple valid form
        data = {
            'is_active': True,
            'survey_interval': 90,
            'surveys_remain_open_days': 7
        }
        test_form = EditSurveySettingsForm(data=data)
        self.assertTrue(test_form.is_valid())

        #test: invalid 'survey_interval'
        data2 = {
            'is_active': True,
            'survey_interval': 75,
            'surveys_remain_open_days': 7
        }
        test_form2 = EditSurveySettingsForm(data=data2)
        self.assertFalse(test_form2.is_valid())
        self.assertIn("Select a valid choice. 75 is not one of the available choices.", test_form2.errors['survey_interval'])

        #test: invalid 'surveys_remain_open_days'
        data3 = {
            'is_active': True,
            'survey_interval': 90,
            'surveys_remain_open_days': 17
        }
        test_form3 = EditSurveySettingsForm(data=data3)
        self.assertFalse(test_form3.is_valid())
        self.assertIn("Select a valid choice. 17 is not one of the available choices.", test_form3.errors['surveys_remain_open_days'])

        #test: invalid 'survey_interval'
        data4 = {
            'is_active': True,
            'survey_interval': "ever so often",
            'surveys_remain_open_days': 7
        }
        test_form4 = EditSurveySettingsForm(data=data4)
        self.assertFalse(test_form4.is_valid())
        self.assertIn("Select a valid choice. ever so often is not one of the available choices.", test_form4.errors['survey_interval'])

        #test: invalid 'surveys_remain_open_days'
        data5 = {
            'is_active': True,
            'survey_interval': 90,
            'surveys_remain_open_days': "Now and then"
        }
        test_form5 = EditSurveySettingsForm(data=data5)
        self.assertFalse(test_form5.is_valid())
        self.assertIn("Select a valid choice. Now and then is not one of the available choices.", test_form5.errors['surveys_remain_open_days'])


    def test_AnswerSurveyForm(self):
        #test: make and test a simple valid form
        pass
