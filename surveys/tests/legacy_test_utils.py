from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

#my stuff
from website.models import Organization
from surveys.models import *
from surveys.core import utils

#third party
from datetime import date, timedelta



#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.
class UtilsTest(TestCase):
    ''' TESTS THAT THE ANSWER SURVEY VIEW BEHAVES PROPERLY '''
    def setUp(self):
        u = User (username="testuser@tt.tt", email="testuser@tt.tt", password="password")
        u.save()
        o = Organization(
                owner=u,
                name="TestOrg",
                phone=None,
                #active_products = models.ManyToManyField(Product, blank=True, help_text='Products this organization is currently using')
                address_line_1="Test st. 77",
                address_line_2=None,
                zip_code="7777",
                city="Test Town",
                country='NO'
            )
        o.save()
        r = Respondent(
                organization=o,
                first_name=None,
                last_name=None,
                email="testrespondent@tt.tt",
                receives_surveys=True
            )
        r.save()

        #instrument to test on
        id=1
        name = "Test Instrument"
        description = "A Description for Test Instrument"
        inst = utils.create_instrument(id, name, description)

        #Scale to test on
        name = "Test Scale"
        instruction="Test instructions for test scale"
        opt_out=False
        min_value=1
        max_value=9
        min_value_description = "No!"
        max_value_description = "Yes!"
        scale = utils.create_ratio_scale(
                name=name,
                instruction=instruction,
                opt_out=opt_out,
                min_value=min_value,
                max_value=max_value,
                min_value_description=min_value_description,
                max_value_description=max_value_description
            )
        #Dimension to test on
        name = "Testyness"
        description = "A Dimension to test"
        dim = utils.create_dimension(inst, name, scale)



    def test_create_instrument(self):
        id=2
        name = "Test Create Instrument"
        description = "A Description for TestCreate Instrument"
        inst = utils.create_instrument(id, name, description)
        self.assertIsInstance(inst, Instrument)
        self.assertEqual(inst.id, id)
        self.assertEqual(inst.name, name)
        self.assertEqual(inst.description, description)

    def test_create_ratio_scale(self):
        name = "TestScale2"
        rs = utils.create_ratio_scale(
                name=name,
                            )

        self.assertIsInstance(rs, RatioScale)
        self.assertIsInstance(rs, Scale)
        self.assertEqual(rs.name, name)
        self.assertEqual(rs.instruction, None)
        self.assertEqual(rs.opt_out, True)
        self.assertEqual(rs.min_value, 0)
        self.assertEqual(rs.max_value, 0)
        self.assertEqual(rs.min_value_description, None)
        self.assertEqual(rs.max_value_description, None)

        name = "Test Scale"
        instruction="Test instructions for test scale"
        opt_out=False
        min_value=1
        max_value=9
        min_value_description = "No!"
        max_value_description = "Yes!"
        rs = utils.create_ratio_scale(
                name=name,
                instruction=instruction,
                opt_out=opt_out,
                min_value=min_value,
                max_value=max_value,
                min_value_description=min_value_description,
                max_value_description=max_value_description
            )

        self.assertIsInstance(rs, RatioScale)
        self.assertEqual(rs.name, name)
        self.assertEqual(rs.instruction, instruction)
        self.assertEqual(rs.opt_out, opt_out)
        self.assertEqual(rs.min_value, min_value)
        self.assertEqual(rs.max_value, max_value)
        self.assertEqual(rs.min_value_description, min_value_description)
        self.assertEqual(rs.max_value_description, max_value_description)

    def test_create_dimension(self):
        inst = Instrument.objects.get(id=1)
        scale = Scale.objects.get(id=1)
        name = "Testyness2"
        description = "A Dimension2 to test"

        d1 = utils.create_dimension(inst, name, scale)
        self.assertIsInstance(d1, Dimension)
        d2 = utils.create_dimension(inst, name, scale, description)
        self.assertIsInstance(d2, Dimension)
        self.assertEqual(d2.instrument, inst)
        self.assertEqual(d2.name, name)
        self.assertEqual(d2.scale, scale)
        self.assertEqual(d2.description, description)

    def test_create_item(self):
        d = Dimension.objects.get(id=1)
        formulation = "You up?"

        i = utils.create_item(
                dimension = d,
                formulation = formulation,
                active = True,
                inverted = False
            )
        self.assertIsInstance(i, Item)
        self.assertEqual(i.dimension, d)
        self.assertEqual(i.formulation, formulation)
        self.assertEqual(i.active, True)
        self.assertEqual(i.inverted, False)
