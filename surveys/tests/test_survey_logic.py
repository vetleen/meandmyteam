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

#set up logging
import logging
logger = logging.getLogger('__name__')
logging.disable(logging.CRITICAL)
#logging.disable(logging.NOTSET)

# Create your tests here.

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

        #Test: try to configure instrument for organization
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
            surveys_remain_open_days=15
        )

        #check that it worked
        ss4 = SurveySetting.objects.get(id=1)
        self.assertEqual(ss3, ss4)
        self.assertEqual(ss3.instrument, i)
        self.assertEqual(ss3.organization, o)
        self.assertEqual(ss3.is_active, True)
        self.assertEqual(ss3.survey_interval, 180)
        self.assertEqual(ss3.surveys_remain_open_days, 15)

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
                i.answer_item(4)

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
                i.answer_item(3)

        #check that it worked
        survey_instances = SurveyInstance.objects.all()
        for si in survey_instances:
            #self.assertEqual(si.started, True) # -> removed the code that marks survey as started while answering questions, this is now handled by view
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
        call_command('createtestsurveydata_for_testing', stdout=out)

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
    

class SurveyLogicTest_dailytaskfunctions(TestCase):

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
        rti['instrument']['slug_name'] = "another_instrument"
        rti['instrument']['name_nb'] = "Another instrument"
        rti['instrument']['slug_name_nb'] = "another_instrument"
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

    def test_close_survey_if_date_close_has_passed(self):
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
        
    
    def test_close_survey_and_check_if_correct_sums(self):
        organization = Organization.objects.get(id=1)
        instrument = Instrument.objects.get(id=1)
        #create little employees
        employee_target = 7
        existing_employees = Respondent.objects.filter(organization=organization)
        if len(existing_employees) < employee_target:
            for e in range(employee_target-len(existing_employees)):
                email = "testemployee" + str(e+1+len(existing_employees)) + "@aa.aa"
                employee = Respondent(organization=organization, email=email)
                employee.save()
        self.assertEqual(len(Respondent.objects.all()), employee_target)

        #start a survey, make instances and answer
        # id #1  choses not to answer any questions
        # id #2 never opened the survey
        # id #3 only answered a few questions
        # the rest answers 3 to every question
        survey = survey_logic.create_survey(owner=organization, instrument_list=[instrument, ])
        survey_instance_list = survey_logic.survey_instances_from_survey(survey)
        for survey_instance in survey_instance_list:
                if survey_instance.id != 2:
                    for id, item in enumerate(survey_instance.get_items()):
                        answer_value = 3 #random.randint(titem.survey_item.item_dimension.scale.min_value, titem.survey_item.item_dimension.scale.max_value)
                        if survey_instance.id == 1:
                            answer_value = "chose_to_not_answer"
                        if survey_instance.id == 3:
                            if id == 1 or id == 2 or id == 3:
                                item.answer_item(answer_value)
                                #print("answered %s to question %s in survey_instance %s."%(answer_value, id, survey_instance.id))
                        else:
                            item.answer_item(answer_value)
                            #print("answered %s to question %s in survey_instance %s."%(answer_value, id, survey_instance.id))
                        item = SurveyInstanceItem.objects.get(id=item.id)
                survey_instance.check_completed()
                
        self.assertEqual(len(Survey.objects.all()), 1)
        self.assertEqual(len(SurveyInstance.objects.all()), employee_target)
        for survey_instance in survey_instance_list:
            if survey_instance.id != 2 and survey_instance.id != 3:
                for item in survey_instance.get_items():
                    self.assertEqual(item.answered, True)
                    if item.survey_instance.id == 1:
                        self.assertEqual(item.answer, None)
                    else:
                        self.assertEqual(item.answer, 3)
            elif survey_instance.id == 2:
                for item in survey_instance.get_items():
                    self.assertEqual(item.answered, False)
                    self.assertEqual(item.answer, None)
            elif survey_instance.id == 3:
                self.assertEqual(survey_instance.check_completed(), False)
                for item in survey_instance.get_items():
                    pass
        
        #close survey
        self.assertEqual(len(Survey.objects.filter(is_closed=True)), 0)
        survey_logic.close_survey(survey)
        self.assertEqual(len(Survey.objects.filter(is_closed=True)), 1)
        
        #test that the SurveyItems and DimensionResults were calculated correctly
        survey = Survey.objects.get(id=1)
        survey_items = survey.get_items()
        for item in survey_items:
            self.assertEqual(item.average, 3)
        for dimension_result in survey.dimensionresult_set.all():
            self.assertEqual(dimension_result.average, 3)
        
        #test that n-answered is correct
        self.assertEqual(survey.n_invited, 7)
        self.assertEqual(survey.n_completed, 5)
        self.assertEqual(survey.n_incomplete, 1)
        self.assertEqual(survey.n_not_started, 1)
                

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
            for email in mail.outbox:
                #print(email.message())
                for address in email.to:
                    self.assertIn(address, [r.email for r in respondent_list])
                self.assertEqual(email.from_email, "surveys@motpanel.com")
                self.assertIn("They would appreciate it if you took the time to fill out the survey at this link", email.body)
                self.assertIn("You have been invited by %s to participate in %s's survey"%(o.owner.email, o.name), email.body)
                self.assertEqual("Employee survey for %s"%(o.name), email.subject)

        #one day later...
        #refresh from db
        ss=SurveySetting.objects.get(id=1)
        survey = Survey.objects.get(owner=o)
        si_list = survey_logic.survey_instances_from_survey(survey)
        self.assertEqual(ss.last_survey_open, datetime.date.today())
        self.assertEqual(ss.last_survey_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))
        self.assertEqual(survey.date_open, datetime.date.today())
        self.assertEqual(survey.date_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days))


        #move time & save (DAY +1)
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            self.assertEqual(survey_instance.survey, survey)
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                self.assertEqual(email.email_date, datetime.date.today())
                email.email_date += datetime.timedelta(days=-1)
                email.save()
                self.assertEqual(email.email_date, datetime.date.today()+datetime.timedelta(days=-1))
        self.assertEqual(ss.last_survey_open, datetime.date.today()+datetime.timedelta(days=-1))
        self.assertEqual(ss.last_survey_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days)+datetime.timedelta(days=-1))
        self.assertEqual(survey.date_open, datetime.date.today()+datetime.timedelta(days=-1))
        self.assertEqual(survey.date_close, datetime.date.today()+datetime.timedelta(days=ss.surveys_remain_open_days)+datetime.timedelta(days=-1))

        #Test that no new emails are sent today
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertEqual(respondent_email, None)
        self.assertEqual(len(mail.outbox), 1)

        #move time & save (DAY +2)
        si_list = survey_logic.survey_instances_from_survey(survey)
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            self.assertEqual(survey_instance.survey, survey)
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                email.email_date += datetime.timedelta(days=-1)
                email.save()

        #Test that no new emails are sent today
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertEqual(respondent_email, None)
        self.assertEqual(len(mail.outbox), 1)

        #move time & save (DAY +3)
        si_list = survey_logic.survey_instances_from_survey(survey)
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                email.email_date += datetime.timedelta(days=-1)
                email.save()

        #Test that mails are sent today & that content is correct (reminder)
        #print("Day 3:")
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertIsInstance(respondent_email, RespondentEmail)
            self.assertEqual(respondent_email.category, 'reminder')
            self.assertEqual(len(mail.outbox), 2)

        for address in mail.outbox[1].to:
            self.assertIn(address, [r.email for r in respondent_list])
        self.assertEqual(mail.outbox[1].from_email, "surveys@motpanel.com")
        self.assertIn("A few days ago we sent you an email regarding %s's regular surveys to investigate"%(o.name), mail.outbox[1].body)
        self.assertEqual("Reminder: %s is conducting a survey among its employees - please take the time to fill it out "%(o.name), mail.outbox[1].subject)


        #move time & save (DAY +4)
        si_list = survey_logic.survey_instances_from_survey(survey)
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            self.assertEqual(survey_instance.survey, survey)
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                email.email_date += datetime.timedelta(days=-1)
                email.save()

        #Test that no new emails are sent today
        #print("Day 4:")
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertEqual(respondent_email, None)
        self.assertEqual(len(mail.outbox), 2)


        #move time & save (DAY +5)
        si_list = survey_logic.survey_instances_from_survey(survey)
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            self.assertEqual(survey_instance.survey, survey)
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                email.email_date += datetime.timedelta(days=-1)
                email.save()

        #Test that no new emails are sent today
        #print("Day 5:")
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertEqual(respondent_email, None)
        self.assertEqual(len(mail.outbox), 2)

        #move time & save (DAY +6)
        si_list = survey_logic.survey_instances_from_survey(survey)
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            self.assertEqual(survey_instance.survey, survey)
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                email.email_date += datetime.timedelta(days=-1)
                email.save()

        #Test that mails are sent today & that content is correct (reminder)
        #print("Day 6:")
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertIsInstance(respondent_email, RespondentEmail)
            self.assertEqual(respondent_email.category, 'last_chance')
            self.assertEqual(len(mail.outbox), 3)

        for address in mail.outbox[2].to:
            self.assertIn(address, [r.email for r in respondent_list])
        self.assertEqual(mail.outbox[2].from_email, "surveys@motpanel.com")
        self.assertIn("This is your last chance!", mail.outbox[2].body)
        self.assertEqual("Last chance to answer %s's employee survey! - it's closing today"%(o.name), mail.outbox[2].subject)


        #move time & save (DAY +7)
        si_list = survey_logic.survey_instances_from_survey(survey)
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            self.assertEqual(survey_instance.survey, survey)
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                email.email_date += datetime.timedelta(days=-1)
                email.save()

        #Test that no new emails are sent today
        #print("Day 7:")
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertEqual(respondent_email, None)
        self.assertEqual(len(mail.outbox), 3)

        #move time & save (DAY +8)
        si_list = survey_logic.survey_instances_from_survey(survey)
        #print("Day 8:")
        survey.date_open += datetime.timedelta(days=-1)
        survey.date_close += datetime.timedelta(days=-1)
        survey.save()
        ss.check_last_survey_dates()
        for survey_instance in si_list:
            self.assertEqual(survey_instance.survey, survey)
            email_list = survey_instance.respondentemail_set.all().order_by('-email_date').exclude(category='failure')
            for email in email_list:
                email.email_date += datetime.timedelta(days=-1)
                email.save()

        #Test that no new emails are sent today
        for survey_instance in si_list:
            respondent_email = survey_logic.send_email_for_survey_instance(survey_instance)
            self.assertEqual(respondent_email, None)
        self.assertEqual(len(mail.outbox), 3)
