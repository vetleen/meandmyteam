from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError
from io import StringIO
from django.core.management import call_command

#my stuff
from website.models import Organization
from surveys.models import *
from surveys.tests.testdata import create_test_data
from surveys.core import setup_instrument
from surveys.core import survey_logic
#third party
import datetime



#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.
class SurveyLogicTest(TestCase):
    ''' TESTS THAT THE ANSWER SURVEY VIEW BEHAVES PROPERLY '''
    def setUp(self):
        pass

    def test_createtestsurveydata(self):
        out = StringIO()
        call_command('createtestsurveydata', stdout=out)
        #self.assertIn("Creating someone to test on...", out.getvalue())

        #print(out.getvalue())
