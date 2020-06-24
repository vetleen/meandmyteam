from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError

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

        rti = create_test_data(1)
        setup_instrument.setup_instrument(rti)

    def test_configure_survey_setting(self):
        o=Organization.objects.get(id=1)
        o.save()
        i=Instrument.objects.get(id=1)
        i.save()

        #configure instrument for organization
        ss = survey_logic.configure_survey_setting(o, i)
        ss2 = SurveySetting.objects.get(id=1)

        #check that it worked
        self.assertEqual(ss, ss2)
        self.assertEqual(ss.instrument, i)
        self.assertEqual(ss.organization, o)
        self.assertEqual(ss.is_active, False)
        self.assertEqual(ss.survey_interval, 90)
        self.assertEqual(ss.surveys_remain_open_days, 10)
        self.assertEqual(ss.last_survey_open, None)
        self.assertEqual(ss.last_survey_close, None)

        #Do it again with **kwargs
        ss3 = survey_logic.configure_survey_setting(
            o,
            i,
            is_active=True,
            survey_interval=180,
            surveys_remain_open_days=15,
            last_survey_open=datetime.date.today(),
            last_survey_close=datetime.date.today()+datetime.timedelta(days=15)
        )

        #check that it worked
        ss4 = SurveySetting.objects.get(id=1)
        self.assertEqual(ss3, ss4)
        self.assertEqual(ss3.instrument, i)
        self.assertEqual(ss3.organization, o)
        self.assertEqual(ss3.is_active, True)
        self.assertEqual(ss3.survey_interval, 180)
        self.assertEqual(ss3.surveys_remain_open_days, 15)
        self.assertEqual(ss3.last_survey_open, datetime.date.today())
        self.assertEqual(ss3.last_survey_close, datetime.date.today()+datetime.timedelta(days=ss3.surveys_remain_open_days))

        #check that we cannot make a new SS for the same org and i
        def create_bad_ss():
            bad_ss = SurveySetting(organization=o, instrument=i)
            bad_ss.save()

        self.assertRaises(IntegrityError, create_bad_ss)

    def test_create_survey(self):
        o=Organization.objects.get(id=1)
        o.save()
        i=Instrument.objects.get(id=1)
        i.save()
        ss = survey_logic.configure_survey_setting(o, i, is_active=True)

        #pre-check
        self.assertEqual(ss.last_survey_open, None)
        self.assertEqual(ss.last_survey_close, None)

        #Make a survey
        survey = survey_logic.create_survey(o, [i, ])

        #Check that it worked as expected
        surveys = Survey.objects.all()
        self.assertEqual(len(surveys), 1)
        self.assertEqual(survey.owner, o)
        self.assertEqual(survey.date_open, datetime.date.today())
        self.assertEqual(survey.date_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))
        self.assertEqual(survey.n_invited, 0)
        self.assertEqual(survey.n_completed, 0)
        self.assertEqual(survey.n_incomplete, 0)
        self.assertEqual(survey.is_closed, False)

        surveyitems = SurveyItem.objects.all()
        self.assertEqual(len(surveyitems), 6)
        si_formulation_list = []
        for si in surveyitems:
            si_formulation_list.append(si.item_formulation)
        for item in i.get_items():
            self.assertIn(item.formulation, si_formulation_list)

        ss = SurveySetting.objects.get(id=1)
        self.assertEqual(ss.last_survey_open, datetime.date.today())
        self.assertEqual(ss.last_survey_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))

        rsdr_list = RatioScaleDimensionResult.objects.all()
        dimension_list = Dimension.objects.all()
        for rsdr in rsdr_list:
            self.assertEqual(rsdr.survey, survey)
            self.assertIsInstance(rsdr.dimension, Dimension)
            self.assertEqual(len(dimension_list), len(rsdr_list))

    def test_survey_instances_from_survey(self):
        o=Organization.objects.get(id=1)
        o.save()
        i=Instrument.objects.get(id=1)
        i.save()
        survey_settings = survey_logic.configure_survey_setting(o, i, is_active=True)
        survey = survey_logic.create_survey(o, [i, ])

        #pre-check
        survey_inst_list = SurveyInstance.objects.all()
        self.assertEqual(len(survey_inst_list), 0)
        self.assertEqual(survey.n_invited, 0)

        sii_list = SurveyInstanceItem.objects.all()
        self.assertEqual(len(sii_list), 0)

        #Make surveyinstances
        survey_logic.survey_instances_from_survey(survey)

        #Check that it worked as expected
        survey_inst_list = SurveyInstance.objects.all()
        self.assertEqual(len(survey_inst_list), 1)
        self.assertEqual(survey.n_invited, 1)

        sii_list = SurveyInstanceItem.objects.all()
        self.assertEqual(len(sii_list), 6)

        #Make surveyinstances AGAIN
        survey_logic.survey_instances_from_survey(survey)

        #Check that it worked as expected
        survey_inst_list = SurveyInstance.objects.all()
        self.assertEqual(len(survey_inst_list), 1)

        sii_list = SurveyInstanceItem.objects.all()
        self.assertEqual(len(sii_list), 6)

        #add another employee
        r2 = Respondent(
                organization=o,
                first_name=None,
                last_name=None,
                email="testrespondent2@tt.tt",
                receives_surveys=True
            )
        r2.save()
        survey_logic.survey_instances_from_survey(survey)

        #Check that it worked as expected
        survey_inst_list = SurveyInstance.objects.all()
        self.assertEqual(len(survey_inst_list), 2)
        self.assertEqual(survey.n_invited, 2)

        sii_list = SurveyInstanceItem.objects.all()
        self.assertEqual(len(sii_list), 12)
        instrument_item_formulations = [item.formulation for item in i.get_items()]
        for sii in SurveyInstance.objects.get(id=1).get_items():
            self.assertIn(sii.survey_item.item_formulation, instrument_item_formulations)

    def test_answer_item(self):
        o=Organization.objects.get(id=1)
        o.save()
        i=Instrument.objects.get(id=1)
        i.save()
        survey_settings = survey_logic.configure_survey_setting(o, i, is_active=True)
        survey = survey_logic.create_survey(o, [i, ])

        r2 = Respondent(
                organization=o,
                first_name=None,
                last_name=None,
                email="testrespondent2@tt.tt",
                receives_surveys=True
            )
        r2.save()


        #Make surveyinstances
        survey_logic.survey_instances_from_survey(survey)

        #Answer items
        survey_instances = SurveyInstance.objects.all()
        for si in survey_instances:
            items = si.get_items()
            for i in items:
                self.assertEqual(i.answer, None)
                self.assertEqual(i.answered, False)
                survey_logic.answer_item(i, 4)

        #check that it worked
        for si in survey_instances:
            items = si.get_items()
            for i in items:
                self.assertEqual(i.answer, 4)
                self.assertEqual(i.answered, True)

    def test_close_survey_w_all_filled(self):
        o=Organization.objects.get(id=1)
        o.save()
        i=Instrument.objects.get(id=1)
        i.save()
        survey_settings = survey_logic.configure_survey_setting(o, i, is_active=True)
        survey = survey_logic.create_survey(o, [i, ])

        r2 = Respondent(
                organization=o,
                first_name=None,
                last_name=None,
                email="testrespondent2@tt.tt",
                receives_surveys=True
            )
        r2.save()

        #answer
        survey_logic.survey_instances_from_survey(survey)
        survey_instances = SurveyInstance.objects.all()
        for si in survey_instances:
            self.assertEqual(si.started, False)
            self.assertEqual(si.completed, False)
            items = si.get_items()
            for i in items:
                self.assertEqual(i.answer, None)
                self.assertEqual(i.answered, False)
                survey_logic.answer_item(i, 3)

        #check that it worked
        survey_instances = SurveyInstance.objects.all()
        for si in survey_instances:
            self.assertEqual(si.started, True)
            self.assertEqual(si.completed, False)
            items = si.get_items()
            for i in items:
                self.assertEqual(i.answer, 3)
                self.assertEqual(i.answered, True)

        #close survey

        survey = survey_logic.close_survey(survey)


        #check that the survey was closed
        self.assertEqual(survey.date_open, datetime.date.today())
        self.assertEqual(survey.date_close, datetime.date.today()+datetime.timedelta(days=-1))
        self.assertEqual(survey.n_invited, 2)
        self.assertEqual(survey.n_completed, 2)
        self.assertEqual(survey.n_incomplete, 0)
        self.assertEqual(survey.n_not_started, 0)
        self.assertEqual(survey.is_closed, True)

        #check thaty the dimensions were closed
        i = Instrument.objects.get(id=1)
        dimension_list=[d for d in i.dimension_set.all()]
        dr_list = survey.dimensionresult_set.all()
        for dr in dr_list:
            self.assertIsInstance(dr, RatioScaleDimensionResult)
            self.assertEqual(dr.survey, survey)
            self.assertIn(dr.dimension, dimension_list)
            self.assertEqual(dr.n_completed, 2)
            self.assertEqual(dr.average, 3)


        #check that the items were closed
        si_list = survey.surveyitem_set.all()
        for si in si_list:
            self.assertEqual(si.n_answered, 2)
            self.assertEqual(si.average, 3)
