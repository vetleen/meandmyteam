from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

#my stuff
from website.models import Organization
from surveys.models import *
from surveys.core import setup_instrument

#third party
from datetime import date, timedelta

from surveys.core import employee_engagement_instrument
#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.

def print_rti(rti):
    print('#########################')
    print('###### INSTRUMENT #######')
    print (rti['instrument'])
    print('#########################')
    print('######## SCALES #########')
    for s in rti['scales']:
        print(s)
    print('#########################')
    print('###### DIMENSIONS #######')
    for d in rti['dimensions']:
        print(d)
    print('#########################')
    print('######### ITEMS #########')
    for i in rti['items']:
        print(i)

class SetupInstrumentTest(TestCase):
    ''' TESTS THAT ... '''
    def setUp(self):
        pass


    def test_setup_works_for_emplyee_engagement_instrument(self):
        #check totals
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)
        self.assertEqual(len (Item.objects.all()), 0)

        #do the thing
        setup_instrument.setup_instrument(raw_instrument=employee_engagement_instrument.employee_engagement_instrument)

        #check that it worked
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 17)

        #do it again
        for i in range(10):
            setup_instrument.setup_instrument(raw_instrument=employee_engagement_instrument.employee_engagement_instrument)

        #check that it didnt get created more times
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 17)


class EmployeeEngagementTest(TestCase):
    ''' TESTS THAT ... '''
    def setUp(self):
        setup_instrument.setup_instrument(raw_instrument=employee_engagement_instrument.employee_engagement_instrument)


    def test_emplyee_engagement_instrument(self):

        #check that we have data to test with
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 17)
