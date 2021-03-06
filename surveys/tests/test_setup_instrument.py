from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

#my stuff
from website.models import Organization
from surveys.models import *
from surveys.core import setup_instrument
from surveys.tests.testdata import create_test_data
#third party
from datetime import date, timedelta

#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.
#FIRST, SOME DATA TO TEST ON!
#instrument

#set up logging
import logging
logger = logging.getLogger('__name__')
logging.disable(logging.CRITICAL)
#logging.disable(logging.NOTSET)

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
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti)

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
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti)

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
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti)

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

        #Try change name -> should work fine
        new_instrument = {
            'id': 1, #THIS IS THE FOREIGN KEY, SO THAT WE HAVE TIGHT CONTROL OVER INSTRUMENTS
            'name': "Employee Engagement 2",
            'slug_name': "employee_engagement_2",
            'description': "An instrument that measures employee engagement",
            'name_nb': "Employee Engagement 2",
            'slug_name_nb': "employee_engagement_2",
            'description_nb': "An instrument that measures employee engagement"
        }
        rti2 =create_test_data(1)
        rti2.update({'instrument': new_instrument})
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti2)

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
            'slug_name': "employee_engagement_2",
            'description': "An instrument that measures employee engagement 2",
            'name_nb': "Employee Engagement 2",
            'slug_name_nb': "employee_engagement_2",
            'description_nb': "An instrument that measures employee engagement 2"
        }
        rti2 =create_test_data(1)
        rti2.update({'instrument': new_instrument})
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti2)

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
        rti2['scales'][0]['name'] = "How often? Scale of One to Five (2)"
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti2)

        ##check that it's fine
        self.assertEqual(len (Instrument.objects.all()), 2)

        i2 = Instrument.objects.get(id=2)
        self.assertEqual(i2.name, rti2['instrument']['name'] )
        self.assertEqual(i2.description, rti2['instrument']['description'] )

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 2)
        self.assertEqual(len (Scale.objects.all()), 2) #gotta have it's own scale
        self.assertEqual(len (Dimension.objects.all()), 6)
        self.assertEqual(len (Item.objects.all()), 12)

        #Try change id of existing instrument in settings
        def try_different_instrument_ids():
            rti2 = create_test_data(2)
            rti2['instrument'].update({'id': 3, 'name': "a new name"})
            test_instrument = setup_instrument.setup_instrument(raw_instrument=rti2)
        self.assertRaises(AssertionError, try_different_instrument_ids)

    def test_setup_instrument_and_then_try_change_scale(self):
        #check that all is calm
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)
        self.assertEqual(len (Item.objects.all()), 0)

        #do the thing
        rti = create_test_data(1)
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti)

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

        #Try change the scale -> you should never change name, min or max value...
        def try_change_scale():
            rti2 = create_test_data(1)
            scale002 = {
                'type': "RatioScale",
                'name':"How often? Scale of One to Six",
                'instruction':"Please indicate how frequently the following occurs on a scale from one (Never) to six (always) the following:",
                'opt_out': True,
                'min_value': 1,
                'max_value': 6,
                'min_value_description':"never",
                'max_value_description':"always",
                'instruction_nb':"Please indicate how frequently the following occurs on a scale from one (Never) to six (always) the following:",
                'min_value_description_nb':"never",
                'max_value_description_nb':"always",
            }
            self.assertNotEqual(rti2['scales'][0], scale002)
            rti2['scales'][0] = scale002
            self.assertEqual(rti2['scales'][0], scale002)

            setup_instrument.setup_instrument(raw_instrument=rti2)

        self.assertRaises(IntegrityError, try_change_scale)

        i = Instrument.objects.get(id=1)
        self.assertEqual(i.id, 1)
        ds = i.dimension_set.all()
        self.assertEqual(len(ds), 3)

        allds = Dimension.objects.all()

        #check totals
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

    def test_setup_instrument_and_then_try_change_dimensions(self):
        #check that all is calm
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)
        self.assertEqual(len (Item.objects.all()), 0)

        #make a product
        rti = create_test_data(1)
        test_instrument = setup_instrument.setup_instrument(raw_instrument=rti)

        #check that it worked
        self.assertEqual(len (Instrument.objects.all()), 1)
        self.assertEqual(len (Scale.objects.all()), 1)
        self.assertEqual(len (Dimension.objects.all()), 3)
        self.assertEqual(len (Item.objects.all()), 6)

        #Try change the dimension in varying ways:

        #change name and description, this should NOT work
        rti2 = create_test_data(1)
        td_vigor = {
            'instrument_id': 1,
            'name': "Vigor 2",
            'description': "Vigor 2 is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
            'scale_location': 0,
            'name_nb': "Vigor 2",
            'description_nb': "Vigor 2 is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
        }

        self.assertNotEqual(rti2['dimensions'][0], td_vigor)
        rti2['dimensions'][0] = td_vigor
        self.assertEqual(rti2['dimensions'][0], td_vigor)
        setup_instrument.setup_instrument(raw_instrument=rti2)
        test_instrument = Instrument.objects.get(id=1)

        tidimensions = test_instrument.dimension_set.all()
        tidimension_names = [d.name for d in tidimensions]

        self.assertNotIn(td_vigor['name'], tidimension_names)


        #change instrument - should give assertion error, since it will be different from the id supplied in rti['instrument']['id']
        rti3 = create_test_data(1)
        td_vigor = {
            'instrument_id': 2,
            'name': "Vigor 2",
            'description': "Vigor 2 is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
            'scale_location': 0,
            'name_nb': "Vigor 2",
            'description_nb': "Vigor 2 is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
        }

        self.assertNotEqual(rti3['dimensions'][0], td_vigor)
        rti3['dimensions'][0] = td_vigor
        self.assertEqual(rti3['dimensions'][0], td_vigor)
        def try_change_instrument_id():
            test_instrument = setup_instrument.setup_instrument(raw_instrument=rti3)
        self.assertRaises(AssertionError, try_change_instrument_id)

        #change scale -
        rti4 = create_test_data(1)
        #new scales to change it up
        td_scale001 = {
            'type': "RatioScale",
            'name':"How often? Scale of One to Five",
            'instruction':"Please indicate how frequently the following occurs on a scale from one (Never) to five (always) the following:",
            'opt_out': True,
            'min_value': 1,
            'max_value': 5,
            'min_value_description':"never",
            'max_value_description':"always",
            'instruction_nb':"Please indicate how frequently the following occurs on a scale from one (Never) to five (always) the following:",
            'min_value_description_nb':"never",
            'max_value_description_nb':"always",
        }
        td_scale002 = {
            'type': "RatioScale",
            'name':"How often? Scale of One to 2",
            'instruction':"One or Two??",
            'opt_out': True,
            'min_value': 1,
            'max_value': 2,
            'min_value_description':"1 - One",
            'max_value_description':"2 - Two",
            'instruction_nb':"One or Two??",
            'min_value_description_nb':"1 - One",
            'max_value_description_nb':"2 - Two",
        }
        td_scale003 = {
            'type': "RatioScale",
            'name':"How often? Scale of One to Five (no opt out)",
            'instruction':"Please indicate how frequently the following occurs on a scale from one (Never) to five (always) the following:",
            'opt_out': False,
            'min_value': 1,
            'max_value': 5,
            'min_value_description':"never",
            'max_value_description':"always",
            'instruction_nb':"Please indicate how frequently the following occurs on a scale from one (Never) to five (always) the following:",
            'min_value_description_nb':"never",
            'max_value_description_nb':"always",
        }
        td_scales = [td_scale001, td_scale002, td_scale003]

        #new Dimensions using new scales
        td_vigor = {
            'instrument_id': 1,
            'name': "Vigor",
            'description': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
            'scale_location': 0, #index of the scales-variable (list) where the scale is located
            'name_nb': "Vigor",
            'description_nb': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
        }
        

        td_dedication = {
            'instrument_id': 1,
            'name': "Dedication",
            'description': "Dedication is characterized by a sense of significance, enthusiasm, inspiration, pride, and challenge, and is sometimes also called \"Involvement\".",
            'scale_location': 1, #index of the scales-variable (list) where the scale is located
            'name_nb': "Dedication",
            'description_nb': "Dedication is characterized by a sense of significance, enthusiasm, inspiration, pride, and challenge, and is sometimes also called \"Involvement\".",
        }
        td_absorption = {
            'instrument_id': 1,
            'name': "Absorption",
            'description': "Absorption, is characterized by being fully concentrated and deeply engrossed in one’s work, whereby time passes quickly and one has difficulties with detaching oneself from work. Being fully absorbed in one’s work comes close to what has been called ‘flow’, a state of optimal experience that is characterized by focused attention, clear mind, mind and body unison, effortless concentration, complete control, loss of self-consciousness, distortion of time, and intrinsic enjoyment.",
            'scale_location': 2, #index of the scales-variable (list) where the scale is located
            'name_nb': "Absorption",
            'description_nb': "Absorption, is characterized by being fully concentrated and deeply engrossed in one’s work, whereby time passes quickly and one has difficulties with detaching oneself from work. Being fully absorbed in one’s work comes close to what has been called ‘flow’, a state of optimal experience that is characterized by focused attention, clear mind, mind and body unison, effortless concentration, complete control, loss of self-consciousness, distortion of time, and intrinsic enjoyment.",
        }
        td_dimensions = [td_vigor, td_dedication, td_absorption]

        self.assertNotEqual(rti4['scales'], td_scales)
        self.assertNotEqual(rti4['dimensions'], td_dimensions)
        rti4['dimensions'] = td_dimensions
        rti4['scales'] = td_scales
        self.assertEqual(rti4['scales'], td_scales)
        self.assertEqual(rti4['dimensions'], td_dimensions)

        def try_change_scale_raw_data():
            test_instrument = setup_instrument.setup_instrument(raw_instrument=rti4)

        self.assertRaises(IntegrityError, try_change_scale_raw_data)



        #final one where we try to supply a out of range scale:
        rti5 = create_test_data(1)
        td_vigor = {
            'instrument_id': 1,
            'name': "Vigor",
            'description': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
            'scale_location': 5, #index of the scales-variable (list) where the scale is located
            'name_nb': "Vigor",
            'description_nb': "Vigor is characterized by high levels of energy and mental resilience while working, the willingness to invest effort in one’s work, and persistence even in the face of difficulties.",
        }
        self.assertNotEqual(rti5['dimensions'][0], td_vigor)
        rti5['dimensions'][0] = td_vigor
        self.assertEqual(rti5['dimensions'][0], td_vigor)

        def set_unviable_scale():
            test_instrument = setup_instrument.setup_instrument(raw_instrument=rti5)
        self.assertRaises(AssertionError, set_unviable_scale)

    def test_setup_instrument_with_faulty_data(self):
        #check that all is calm
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)
        self.assertEqual(len (Item.objects.all()), 0)

        #No instrument? No problem:
        def try_missing_instrument():
            rti = create_test_data(1)
            missing_instrument = rti.pop('instrument')
            test_instrument = setup_instrument.setup_instrument(raw_instrument=rti)
        self.assertRaises(AssertionError, try_missing_instrument)
        #No scales? No problem:
        def try_missing_scales():
            rti = create_test_data(1)
            missing_scales = rti.pop('scales')
            test_scales = setup_instrument.setup_instrument(raw_instrument=rti)
        self.assertRaises(AssertionError, try_missing_scales)
        #No dimensions? No problem:
        def try_missing_dimensions():
            rti = create_test_data(1)
            missing_dimensions = rti.pop('dimensions')
            test_dimensions = setup_instrument.setup_instrument(raw_instrument=rti)
        self.assertRaises(AssertionError, try_missing_dimensions)
        #No items? No problem:
        def try_missing_items():
            rti = create_test_data(1)
            missing_items = rti.pop('items')
            test_items = setup_instrument.setup_instrument(raw_instrument=rti)
        self.assertRaises(AssertionError, try_missing_items)

        #check that nothing was made
        self.assertEqual(len (Instrument.objects.all()), 0)
        self.assertEqual(len (Scale.objects.all()), 0)
        self.assertEqual(len (Dimension.objects.all()), 0)
        self.assertEqual(len (Item.objects.all()), 0)
