from io import StringIO

from django.test import TestCase
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.management import call_command
from django.core import mail


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
'''
class SurveyLogicTest(TestCase):

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
        self.assertEqual(ss.surveys_remain_open_days, 7)
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
        self.assertEqual(len(ss.surveys.all()), 0)

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
        self.assertEqual(len(ss.surveys.all()), 1)

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

    def test_get_results_from_survey_and_get_results_from_instrument(self):
        i = Instrument.objects.get(id=1)

        #check startconditions
        self.assertEqual(len(Instrument.objects.all()), 1) #Note, a new instrument WILL NOT be created by the createtestsurveydata-command!
        self.assertEqual(len(Dimension.objects.all()), 3)
        self.assertEqual(len(Survey.objects.all()), 0)

        #create, answer and close survey
        out = StringIO()
        call_command('createtestsurveydata', stdout=out)

        #Check that it worked as excpected
        self.assertEqual(len(Survey.objects.all()), 3)

        #test get_results_from_survey()
        tsurvey = Survey.objects.get(id=1)
        data = survey_logic.get_results_from_survey(tsurvey, i)

        instruments = Instrument.objects.all()
        self.assertEqual(data['instrument'], i)
        self.assertEqual(data['survey'], tsurvey)
        self.assertIn('dimension_results', data)
        self.assertIn('item_results', data)
        for dr in data['dimension_results']:
            self.assertIn('dimension', dr)
            self.assertIn('scale', dr)
            self.assertIn('n_completed', dr)
            self.assertIn('average', dr)
        for ir in data['item_results']:
            self.assertIn('formulation', ir)
            self.assertIn('dimension', ir)
            self.assertIn('scale', ir)
            self.assertIn('n_answered', ir)
            self.assertIn('average', ir)
            self.assertIn('inverted', ir)


        #test get_results_from_instrument()
        gfrs_data = data
        data = survey_logic.get_results_from_instrument(instrument=i, organization=tsurvey.owner, depth=3)

        self.assertEqual(data['instrument'], i)
        self.assertEqual(len(data['surveys']), 3)

        self.assertEqual(data['surveys'][0], gfrs_data)
'''

class SurveyLogicTest_dailytaskfunctions(TestCase):
    ''' TESTS THAT THE ANSWER SURVEY VIEW BEHAVES PROPERLY '''
    def setUp(self):
        rti = create_test_data(1)
        setup_instrument.setup_instrument(rti)
        i=Instrument.objects.get(id=1)
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
        ss = survey_logic.configure_survey_setting(organization=o, instrument=i, is_active=True)
        ss.save()


    def test_create_survey_if_due(self):
        pass
        '''
        o=Organization.objects.get(id=1)
        i=Instrument.objects.get(id=1)
        ss=SurveySetting.objects.get(id=1)

        #test all is calm to set things off
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 0)
        self.assertEqual(ss.last_survey_open, None)
        self.assertEqual(ss.last_survey_close, None)
        self.assertEqual(len(ss.surveys.all()), 0)

        #run it once, creating a survey
        survey = survey_logic.create_survey_if_due(organization=o)

        #Test that it worked, creating 1 survey
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 1)
        self.assertIsInstance(survey, Survey)
        self.assertEqual(survey.date_open, datetime.date.today())
        self.assertEqual(survey.date_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))
        ss=SurveySetting.objects.get(id=1)
        self.assertEqual(ss.last_survey_open, datetime.date.today())
        self.assertEqual(ss.last_survey_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))
        self.assertEqual(len(ss.surveys.all()), 1)

        #run it again, NOT creating a survey
        survey2 = survey_logic.create_survey_if_due(organization=o)
        survey3 = survey_logic.create_survey_if_due(organization=o)
        survey4 = survey_logic.create_survey_if_due(organization=o)
        survey5 = survey_logic.create_survey_if_due(organization=o)

        #Test that it didnt create more surveys
        self.assertIsInstance(survey, Survey)
        self.assertEqual(survey2, None)
        self.assertEqual(survey3, None)
        self.assertEqual(survey4, None)
        self.assertEqual(survey5, None)
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 1)

        #Move date_open and _close back in time so it a survey becomes due again
        survey.date_open = datetime.date.today()+datetime.timedelta(days=-100)
        survey.date_close = datetime.date.today()+datetime.timedelta(days=-93)
        survey.save()
        ss.last_survey_open = datetime.date.today()+datetime.timedelta(days=-100)
        ss.last_survey_close = datetime.date.today()+datetime.timedelta(days=-93)
        ss.save()
        survey_logic.close_survey(survey)

        #run it once, creating a new survey
        survey6 = survey_logic.create_survey_if_due(organization=o)

        #Test that it worked, creating 1 additional survey
        self.assertIsInstance(survey6, Survey)
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 2)

        #add another instrument
        rti = create_test_data(2)
        rti['instrument']['name'] = "Another instrument"
        rti['scales'][0]['name'] = "Another Scale"
        setup_instrument.setup_instrument(rti)
        i2=Instrument.objects.get(id=2)

        #run it once, ensure no new Surveys are made
        survey7 = survey_logic.create_survey_if_due(organization=o)
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 2)

        #Move date_open and _close back in time so it a survey becomes due again
        survey6.date_open = datetime.date.today()+datetime.timedelta(days=-100)
        survey6.date_close = datetime.date.today()+datetime.timedelta(days=-93)
        survey6.save()
        ss.last_survey_open = datetime.date.today()+datetime.timedelta(days=-100)
        ss.last_survey_close = datetime.date.today()+datetime.timedelta(days=-93)
        ss.save()
        survey_logic.close_survey(survey6)

        #configure new instrument
        ss2 = survey_logic.configure_survey_setting(organization=o, instrument=i2, is_active=True)
        ss2.save()

        #run it once, 1 new survey should be made
        survey8 = survey_logic.create_survey_if_due(organization=o)

        #check that 1 was made
        self.assertIsInstance(survey8, Survey)
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 3)

        #check that both instruments were included
        dr_list8 = survey8.dimensionresult_set.all()
        self.assertEqual(len(dr_list8), 6)
        #while in the old one, only 1 instrument
        dr_list6 = survey6.dimensionresult_set.all()
        self.assertEqual(len(dr_list6), 3)

        #Move date_open and _close back in time so it a survey becomes due again
        survey8.date_open = datetime.date.today()+datetime.timedelta(days=-100)
        survey8.date_close = datetime.date.today()+datetime.timedelta(days=-93)
        survey8.save()
        ss.last_survey_open = datetime.date.today()+datetime.timedelta(days=-100)
        ss.last_survey_close = datetime.date.today()+datetime.timedelta(days=-93)
        ss.save()
        ss2.last_survey_open = datetime.date.today()+datetime.timedelta(days=-100)
        ss2.last_survey_close = datetime.date.today()+datetime.timedelta(days=-93)
        ss2.save()
        survey_logic.close_survey(survey8)

        #deactive the first product
        ss = survey_logic.configure_survey_setting(organization=o, instrument=i, is_active=False)
        ss.save()

        #surveys are due again
        survey9 = survey_logic.create_survey_if_due(organization=o)

        #only one instrument should be included
        dr_list9 = survey9.dimensionresult_set.all()
        self.assertEqual(len(dr_list9), 3)

        #Move date_open and _close back in time so it becomes not due, but still in the timewindow to be included with anopther instrument
        survey9.date_open = datetime.date.today()+datetime.timedelta(days=-75)
        survey9.date_close = datetime.date.today()+datetime.timedelta(days=-70)
        survey9.save()
        ss2.last_survey_open = datetime.date.today()+datetime.timedelta(days=-75)
        ss2.last_survey_close = datetime.date.today()+datetime.timedelta(days=-70)
        ss2.save()
        survey_logic.close_survey(survey9)

        #Run it again, nothing happens... it not due...
        survey10 = survey_logic.create_survey_if_due(organization=o)
        self.assertEqual(survey10, None)

        #Activate first product again
        ss = survey_logic.configure_survey_setting(organization=o, instrument=i, is_active=True)
        ss.save()

        #check that everything is in order befoe the big finale
        self.assertEqual(ss.last_survey_open, datetime.date.today()+datetime.timedelta(days=-100)) #is due
        self.assertEqual(ss.last_survey_close, datetime.date.today()+datetime.timedelta(days=-93))
        self.assertEqual(ss2.last_survey_open, datetime.date.today()+datetime.timedelta(days=-75)) #is not due, but close enough
        self.assertEqual(ss2.last_survey_close, datetime.date.today()+datetime.timedelta(days=-70))

        #Run it again, both should be included, product 1 because it's so lojng ago, and product 2 it get's dragged in because it's due within 60 days and 1/3 of 90 days
        survey11 = survey_logic.create_survey_if_due(organization=o)

        #Both should be included
        dr_list11 = survey11.dimensionresult_set.all()
        self.assertEqual(len(dr_list11), 6)

        #and dates are now aligned so that in the future, they fire at the same time
        ss = survey_logic.configure_survey_setting(organization=o, instrument=i)
        self.assertEqual(ss.last_survey_open, datetime.date.today())
        self.assertEqual(ss.last_survey_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))
        ss2 = survey_logic.configure_survey_setting(organization=o, instrument=i2)
        self.assertEqual(ss2.last_survey_open, datetime.date.today())
        self.assertEqual(ss2.last_survey_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))

        #Move date_open and _close back in time so it a survey becomes due again
        survey11.date_open = datetime.date.today()+datetime.timedelta(days=-100)
        survey11.date_close = datetime.date.today()+datetime.timedelta(days=-93)
        survey11.save()
        ss.last_survey_open = datetime.date.today()+datetime.timedelta(days=-100)
        ss.last_survey_close = datetime.date.today()+datetime.timedelta(days=-93)
        ss.save()
        ss2.last_survey_open = datetime.date.today()+datetime.timedelta(days=-100)
        ss2.last_survey_close = datetime.date.today()+datetime.timedelta(days=-93)
        ss2.save()
        survey_logic.close_survey(survey11)
        '''
    def test_close_survey_if_date_close_has_passed(self):
        pass
        '''
        o=Organization.objects.get(id=1)
        i=Instrument.objects.get(id=1)
        ss=SurveySetting.objects.get(id=1)

        #test all is calm to set things off
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 0)
        self.assertEqual(ss.last_survey_open, None)
        self.assertEqual(ss.last_survey_close, None)
        self.assertEqual(len(ss.surveys.all()), 0)

        #Create a survey
        survey = survey_logic.create_survey_if_due(organization=o)

        #run the close-if-date-closed-has-passed function
        def try_close_w_future_date_close():
            survey_logic.close_survey_if_date_close_has_passed(survey)

        #check that trying to close it raises assertion error
        self.assertRaises(AssertionError, try_close_w_future_date_close)

        #Move date_open and _close back in time so the survey should be closed
        survey.date_open = datetime.date.today()+datetime.timedelta(days=-100)
        survey.date_close = datetime.date.today()+datetime.timedelta(days=-93)
        survey.save()
        ss.last_survey_open = datetime.date.today()+datetime.timedelta(days=-100)
        ss.last_survey_close = datetime.date.today()+datetime.timedelta(days=-93)
        ss.save()

        #precheck
        survey_list = Survey.objects.filter(is_closed=True)
        self.assertEqual(len(survey_list), 0)

        #run the close-if-date-closed-has-passed fdunction
        survey = survey_logic.close_survey_if_date_close_has_passed(survey)

        #Check that the survey was closed
        survey_list = Survey.objects.filter(is_closed=True)
        self.assertEqual(len(survey_list), 1)

        #run the close-if-date-closed-has-passed function
        def try_close_w_is_close_true():
            survey_logic.close_survey_if_date_close_has_passed(survey)

        #check that trying to close it AGAIN raises assertion error
        self.assertRaises(AssertionError, try_close_w_is_close_true)
        '''

    def test_send_email_for_survey_instance(self):
        o=Organization.objects.get(id=1)
        i=Instrument.objects.get(id=1)
        ss=SurveySetting.objects.get(id=1)

        #test all is calm to set things off
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 0)
        self.assertEqual(len(mail.outbox), 0)

        #Create things we need
        survey = survey_logic.create_survey_if_due(organization=o)
        respondent = Respondent(organization=o, email="testrespondent@aa.aa")
        respondent.save()
        si_list = survey_logic.survey_instances_from_survey(survey)

        #everything was created successfully
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 1)
        respondent_list = Respondent.objects.all()
        self.assertEqual(len(respondent_list), 1)
        self.assertEqual(len(si_list), 1)

        #run the function that we are testing

        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertIsInstance(respondent_email, RespondentEmail)
            self.assertEqual(respondent_email.category, 'initial')
            self.assertEqual(len(mail.outbox), 1)
            #print(dir(mail.outbox))
            for m in mail.outbox:
                print(m.message())
                pass




        #send_email_for_survey_instance(survey_instance)
