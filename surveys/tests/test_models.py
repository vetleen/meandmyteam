from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

#my stuff
from website.models import Organization
from surveys.models import *

#third party
from datetime import date, timedelta



#from django.urls import reverse
#from django.test import Client
#from django.contrib.auth.models import AnonymousUser, User
#from django.contrib import auth

# Create your tests here.
class ModelsTest(TestCase):
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
        test_ratio_scale = RatioScale(
                name="testscale_onetofive",
                instruction="Indicate on a scale form 1 to five ...",
                opt_out=False,
                min_value=1,
                max_value=5,
                min_value_description="Don't agree",
                max_value_description="Agree"
            )
        test_ratio_scale.save()
        test_ratio_scale2 = RatioScale(
                name="testscale_2222222222onetofive",
                instruction="Indicate on22222222222 a scale form 1 to five ...",
                opt_out=False,
                min_value=1,
                max_value=2,
                min_value_description="Don't agree 2",
                max_value_description="Agree 2"
            )
        test_ratio_scale2.save()

        #TEST-INSTRUMENT
        test_employee_engagement_instrument = Instrument(
                id = 1,
                name = "test_Employee Engagement",
                description = "a test instrument for EE",
            )
        test_employee_engagement_instrument.save()

        #TEST-DIMENSIONS
        test_vigor = Dimension(
                instrument=test_employee_engagement_instrument,
                name="Vigor",
                description="vigor: a dimension of EE",
                scale=test_ratio_scale
            )
        test_vigor.save()


        #TEST-ITEMS
        test_vigor_item_01 = Item(
                formulation="When I get up in the morning, I feel like going to work.",
                dimension=test_vigor
            )
        test_vigor_item_01.save()



        sur = Survey(
        owner=o,
        date_open=date.today(),
        date_close =date.today() + timedelta(days=10)
        )
        sur.save()

        rsi = RatioSurveyItem(
            survey = sur,
            item_formulation = test_vigor_item_01.formulation,
            item_inverted = test_vigor_item_01.inverted,
            item_dimension = test_vigor_item_01.dimension,
            n_answered = 0,
            average = None

        )
        rsi.save()

        sinst = SurveyInstance(respondent=r, survey=sur)
        sinst.save()
        rsii = RatioSurveyInstanceItem(
                survey_instance = sinst,
                survey_item = rsi
        )
        rsii.save()

    def test_RatioScale_(self):
        #Test RatioScale
        ts = RatioScale.objects.get(id=1)
        self.assertIsInstance(ts, RatioScale)
        self.assertEqual(ts.name, "testscale_onetofive")
        self.assertEqual(ts.instruction, "Indicate on a scale form 1 to five ...")
        self.assertEqual(ts.opt_out, False)
        self.assertEqual(ts.min_value, 1)
        self.assertEqual(ts.max_value, 5)
        self.assertEqual(ts.min_value_description, "Don't agree")
        self.assertEqual(ts.max_value_description, "Agree")
        def try_save_ratioscale_item():
            ts.max_value=6
            ts.save() #OH NO! Someone forgot that Scales should not be changed after they are made!
        self.assertRaises(IntegrityError, try_save_ratioscale_item)
        ts = RatioScale.objects.get(id=1)
        self.assertEqual(ts.max_value, 5)

    def test_Instrument(self):
        i = Instrument.objects.get(id=1)
        self.assertIsInstance(i, Instrument)
        self.assertEqual(i.name, "test_Employee Engagement")
        self.assertEqual(i.description, "a test instrument for EE")

    def test_Dimension(self):
        #test that it works as expected
        d = Dimension.objects.get(id=1)
        self.assertIsInstance(d, Dimension)
        self.assertIsInstance(d.instrument, Instrument)
        self.assertEqual(d.name, "Vigor")
        self.assertEqual(d.description, "vigor: a dimension of EE")
        self.assertIsInstance(d.scale, Scale)

        #test that it doesn't work unexpectedly
        ds = Dimension.objects.all()
        self.assertEqual(len(ds), 1)
        def try_invalid_input_to_scale():
            i= Instrument.objects.get(id=1)
            test_absorption = Dimension(
                    instrument=i,
                    name="Absorption",
                    description="absorption: a dimension of EE",
                    scale=d #Oh no, someone tried to set a Dimension object as a Scale, what a loon!
                )
            test_absorption.save()
        self.assertRaises(ValidationError, try_invalid_input_to_scale) #notice the lack of paranthesis after the function name, means don't test the return value, test the callable
        ds = Dimension.objects.all()
        self.assertEqual(len(ds), 1)
        def try_save_dimension_item():
            d.scale=Scale.objects.get(id=2) #Oh no! but what about the items whee thsi scale already is in use?
            d.save()
        self.assertRaises(IntegrityError, try_save_dimension_item)
        def try_save_dimension_item2():
            d.name="A New Name" #OH NO! With a new name, who will I be?
            d.save()
        self.assertRaises(IntegrityError, try_save_dimension_item2)
        d = Dimension.objects.get(id=1)
        def create_duplicate_dimension():
            d2 = Dimension(
                instrument = d.instrument,
                name = d.name,
                description = "a mad attempt at making a dimension with same name and instrument as an exsiting one",
                scale = d.scale
            )
            d2.save()
        self.assertRaises(IntegrityError, create_duplicate_dimension)
        d.instrument=None #OH NO! With a new name, who will I be?
        d.save()
        d = Dimension.objects.get(id=1)
        self.assertEqual(d.instrument, None)


    def test_Item(self):
        #test that it works as expected
        i = Item.objects.get(id=1)
        self.assertIsInstance(i, Item)
        self.assertEqual(i.formulation, "When I get up in the morning, I feel like going to work.")
        d = Dimension.objects.get(id=1)
        self.assertEqual(i.dimension, d)

    def test_Respondent(self):
        u = User.objects.get(id=1)
        o = Organization.objects.get(id=1)
        r = Respondent.objects.get(id=1)
        self.assertIsInstance(r, Respondent)
        self.assertEqual(r.organization, o)
        self.assertEqual(r.first_name, None)
        self.assertEqual(r.last_name, None)
        self.assertEqual(r.email, "testrespondent@tt.tt")
        self.assertEqual(r.receives_surveys, True)

    def test_Survey(self):
        u = User.objects.get(id=1)
        o = Organization.objects.get(id=1)
        s = Survey.objects.get(id=1)
        self.assertIsInstance(s, Survey)
        self.assertEqual(s.owner, o)
        self.assertEqual(s.date_open, date.today())
        self.assertEqual(s.date_close, (date.today() + timedelta(days=10)))

    def test_SurveyItems(self):
        su = Survey.objects.get(id=1)
        i = Item.objects.get(id=1)
        si = RatioSurveyItem.objects.get(id=1)
        d = Dimension.objects.get(id=1)
        rs = RatioScale.objects.get(id=1)
        self.assertIsInstance(si, RatioSurveyItem)
        self.assertIsInstance(si, SurveyItem)
        self.assertEqual(si.survey, su)
        self.assertEqual(si.item_formulation, i.formulation)
        self.assertEqual(si.item_inverted, i.inverted)
        self.assertEqual(si.item_dimension, i.dimension)
        self.assertEqual(si.item_dimension, d)
        self.assertEqual(si.n_answered, 0)
        self.assertEqual(si.average, None)
        self.assertEqual(si.scale(), d.scale)
        self.assertEqual(si.n_invited(), 0)

    def test_SurveyInstance(self):
        su = Survey.objects.get(id=1)
        r = Respondent.objects.get(id=1)
        si = SurveyInstance.objects.get(id=1)

        self.assertIsInstance(si, SurveyInstance)
        self.assertEqual(si.respondent, r)
        self.assertEqual(si.survey, su)
        self.assertEqual(len(si.items()), 1)


    def test_RatioSurveyInstanceItem(self):
        sinst = SurveyInstance.objects.get(id=1)
        sitem = RatioSurveyItem.objects.get(id=1)
        rsii = RatioSurveyInstanceItem.objects.get(id=1)
        self.assertIsInstance(rsii, RatioSurveyInstanceItem)
        self.assertEqual(rsii.survey_instance, sinst)
        self.assertEqual(rsii.survey_item, sitem)

        su = Survey.objects.get(id=1)
        r = Respondent.objects.get(id=1)
        self.assertEqual(rsii.survey(), su)
        self.assertEqual(rsii.respondent(), r)
        self.assertEqual(rsii.formulation(), sitem.item_formulation)
        self.assertEqual(rsii.dimension(), sitem.item_dimension)
