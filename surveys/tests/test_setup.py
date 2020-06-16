from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

#my stuff
from website.models import Organization
from surveys.models import *
from surveys.core import setup

#third party
from datetime import date, timedelta

#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.
#FIRST, SOME DATA TO TEST ON!
#instrument
def create_test_data(instrument_id):
    instrument = {
        'id': instrument_id, #THIS IS THE FOREIGN KEY, SO THAT WE HAVE TIGHT CONTROL OVER INSTRUMENTS
        'name': "Employee Engagement",
        'description': "An instrument that measures employee engagement"
    }

    #Scale
    scale001 = {
        'type': "RatioScale",
        'name':"How often? Scale of One to Five",
        'instruction':"Please indicate how frequently the following occurs on a scale from one (Never) to five (always) the following:",
        'opt_out': True,
        'min_value': 1,
        'max_value': 5,
        'min_value_description':"never",
        'max_value_description':"always",
    }
    scales = [scale001, ]

    #Dimensions
    vigor = {
        'instrument_id': instrument_id,
        'name': "Vigor",
        'description': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
        'scale_location': 0 #index of the scales-variable (list) where the scale is located
    }

    dedication = {
        'instrument_id': instrument_id,
        'name': "Dedication",
        'description': "Dedication is characterized by a sense of significance, enthusiasm, inspiration, pride, and challenge, and is sometimes also called \"Involvement\".",
        'scale_location': 0 #index of the scales-variable (list) where the scale is located
    }
    absorption = {
        'instrument_id': instrument_id,
        'name': "Absorption",
        'description': "Absorption, is characterized by being fully concentrated and deeply engrossed in one’s work, whereby time passes quickly and one has difficulties with detaching oneself from work. Being fully absorbed in one’s work comes close to what has been called ‘flow’, a state of optimal experience that is characterized by focused attention, clear mind, mind and body unison, effortless concentration, complete control, loss of self-consciousness, distortion of time, and intrinsic enjoyment.",
        'scale_location': 0 #index of the scales-variable (list) where the scale is located
    }
    dimensions = [vigor, dedication, absorption]

    #Items
    i001 = {
        'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
        'formulation': "When I get up in the morning, I feel like going to work.",
        'active': True,
        'inverted': False,
    }

    i002 = {
        'dimension_location': 0, #index of dimensions-variable(list) where the dimension is located
        'formulation': "At my work, I feel bursting with energy.",
        'active': True,
        'inverted': False,
    }

    i007 = {
        'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
        'formulation': "To me, my job is challenging.",
        'active': True,
        'inverted': False,
    }

    i008 = {
        'dimension_location': 1, #index of dimensions-variable(list) where the dimension is located
        'formulation': "My job inspires me.",
        'active': True,
        'inverted': False,
    }

    i012 = {
        'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
        'formulation': "When I am working, I forget everything else around me.",
        'active': True,
        'inverted': False,
    }

    i013 = {
        'dimension_location': 2, #index of dimensions-variable(list) where the dimension is located
        'formulation': "Time flies when I am working.",
        'active': True,
        'inverted': False,
    }

    items = [i001, i002, i007, i008, i012, i013]

    raw_test_instrument = {
        'instrument': instrument,
        'scales': scales,
        'dimensions': dimensions,
        'items': items,
    }
    return raw_test_instrument


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


    def test_setup_instrument_and_again_with_same_exact_data(self):
        #check totals
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)
        self.assertEqual(len (Item.objects.all()), 0)

        #do the thing
        rti = create_test_data(1)
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
        ##ITEM
        items = Item.objects.all()
        self.assertEqual(len(items), 6)
        for n, i in enumerate(items):
            aimed_for_dimension = Dimension.objects.get(id=rti['items'][n]['dimension_location']+1)
            self.assertEqual(i.dimension, aimed_for_dimension)
            self.assertEqual(i.formulation, rti['items'][n]['formulation'])
            self.assertEqual(i.active, rti['items'][n]['active'])
            self.assertEqual(i.inverted, rti['items'][n]['inverted'])


        #check total again
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

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
        ##ITEM
        items = Item.objects.all()
        self.assertEqual(len(items), 6)
        for n, i in enumerate(items):
            aimed_for_dimension = Dimension.objects.get(id=rti['items'][n]['dimension_location']+1)
            self.assertEqual(i.dimension, aimed_for_dimension)
            self.assertEqual(i.formulation, rti['items'][n]['formulation'])
            self.assertEqual(i.active, rti['items'][n]['active'])
            self.assertEqual(i.inverted, rti['items'][n]['inverted'])

        #check totals a final time
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

    def test_setup_instrument_and_then_change_instrument(self):
        #check that all is calm
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)
        self.assertEqual(len (Item.objects.all()), 0)

        #do the thing
        rti =create_test_data(1)
        test_instrument = setup.setup_instrument(raw_instrument=rti)

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

        #Try change name -> should work fine
        new_instrument = {
            'id': 1, #THIS IS THE FOREIGN KEY, SO THAT WE HAVE TIGHT CONTROL OVER INSTRUMENTS
            'name': "Employee Engagement 2",
            'description': "An instrument that measures employee engagement"
        }
        rti2 =create_test_data(1)
        rti2.update({'instrument': new_instrument})
        test_instrument = setup.setup_instrument(raw_instrument=rti2)

        ##check that it's fine
        self.assertEqual(len (Instrument.objects.all()), 1)
        i = Instrument.objects.get(id=1)
        self.assertEqual(i.name, rti2['instrument']['name'] )
        self.assertEqual(i.description, rti2['instrument']['description'] )

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

        #Try change description -> should work fine
        new_instrument = {
            'id': 1, #THIS IS THE FOREIGN KEY, SO THAT WE HAVE TIGHT CONTROL OVER INSTRUMENTS
            'name': "Employee Engagement 2",
            'description': "An instrument that measures employee engagement 2"
        }
        rti2 =create_test_data(1)
        rti2.update({'instrument': new_instrument})
        test_instrument = setup.setup_instrument(raw_instrument=rti2)

        ##check that it's fine
        self.assertEqual(len (Instrument.objects.all()), 1)
        i = Instrument.objects.get(id=1)
        self.assertEqual(i.name, rti2['instrument']['name'] )
        self.assertEqual(i.description, rti2['instrument']['description'] )

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

        #Try make an additonal Instrument -> now everything should be doubled
        rti2 = create_test_data(2)
        test_instrument = setup.setup_instrument(raw_instrument=rti2)

        ##check that it's fine
        self.assertEqual(len (Instrument.objects.all()), 2)

        i2 = Instrument.objects.get(id=2)
        self.assertEqual(i2.name, rti2['instrument']['name'] )
        self.assertEqual(i2.description, rti2['instrument']['description'] )

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 2)
        self.assertEqual(len (Scale.objects.all()), 1) #the same scale can be used,. because scales are immuteable, and these two scales would be completely the same
        self.assertEqual(len (Dimension.objects.all()), 6)
        self.assertEqual(len (Item.objects.all()), 12)

        #Try change id of existing instrument in settings
        def try_different_instrument_ids():
            rti2 = create_test_data(2)
            rti2['instrument'].update({'id': 3, 'name': "a new name"})
            test_instrument = setup.setup_instrument(raw_instrument=rti2)
        self.assertRaises(AssertionError, try_different_instrument_ids)
