from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

#my stuff
from website.models import Organization
from surveys.models import *
from surveys.core import setup
from surveys.core import employee_engagement_instrument

#third party
from datetime import date, timedelta



#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.

rti = employee_engagement_instrument.employee_engagement_instrument

class SetupInstrumentTest(TestCase):
    ''' TESTS THAT ... '''
    def setUp(self):
        pass


    def test_setup_instrument_with_never_changing_data(self):
        #check that all is calm
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)

        #do the thing
        test_instrument = setup.setup_instrument(raw_instrument=rti)

        #check that all is still calm
        ##INSTRUMENT
        self.assertEqual(len (Instrument.objects.all()), 1)
        i = Instrument.objects.get(id=1)
        self.assertEqual(i.name, rti['instrument']['name'] )
        self.assertEqual(i.description, rti['instrument']['description'] )
        ##SCALE
        ss = Scale.objects.all()
        self.assertEqual(len (ss), 1)
        for n, s in enumerate(ss):
            self.assertEqual(s.name, rti['scales'][n]['name'])
            self.assertEqual(s.instruction, rti['scales'][n]['instruction'])
            self.assertEqual(s.opt_out, rti['scales'][n]['opt_out'])
            self.assertEqual(s.min_value, rti['scales'][n]['min_value'])
            self.assertEqual(s.max_value, rti['scales'][n]['max_value'])
            self.assertEqual(s.min_value_description, rti['scales'][n]['min_value_description'])
            self.assertEqual(s.max_value_description, rti['scales'][n]['max_value_description'])
        ##DIMENSION
        ds = Dimension.objects.all()
        self.assertEqual(len (ds), 3)
        for n, d in enumerate(ds):
            self.assertEqual(d.instrument.id, rti['dimensions'][n]['instrument_id'])
            self.assertEqual(d.name, rti['dimensions'][n]['name'])
            self.assertEqual(d.name, rti['dimensions'][n]['name'])
            aimed_for_scale = Scale.objects.get(id=1)
            self.assertEqual(d.scale, aimed_for_scale)


        #check calmness
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)

        #do it again
        test_instrument = setup.setup_instrument(raw_instrument=rti)

        #aaaand check that all is still calm
        ##INSTRUMENT
        self.assertEqual(len (Instrument.objects.all()), 1)
        i = Instrument.objects.get(id=1)
        self.assertEqual(i.name, rti['instrument']['name'] )
        self.assertEqual(i.description, rti['instrument']['description'] )
        ##SCALE
        ss = Scale.objects.all()
        self.assertEqual(len (ss), 1)
        for n, s in enumerate(ss):
            self.assertEqual(s.name, rti['scales'][n]['name'])
            self.assertEqual(s.instruction, rti['scales'][n]['instruction'])
            self.assertEqual(s.opt_out, rti['scales'][n]['opt_out'])
            self.assertEqual(s.min_value, rti['scales'][n]['min_value'])
            self.assertEqual(s.max_value, rti['scales'][n]['max_value'])
            self.assertEqual(s.min_value_description, rti['scales'][n]['min_value_description'])
            self.assertEqual(s.max_value_description, rti['scales'][n]['max_value_description'])
        ##DIMENSION
        ds = Dimension.objects.all()
        self.assertEqual(len (ds), 3)
        for n, d in enumerate(ds):
            self.assertEqual(d.instrument.id, rti['dimensions'][n]['instrument_id'])
            self.assertEqual(d.name, rti['dimensions'][n]['name'])
            self.assertEqual(d.name, rti['dimensions'][n]['name'])
            aimed_for_scale = Scale.objects.get(id=1)
            self.assertEqual(d.scale, aimed_for_scale)
