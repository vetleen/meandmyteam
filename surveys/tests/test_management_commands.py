from django.test import TestCase
#from django.test import SimpleTestCase
#from django.core.exceptions import ValidationError
#from django.contrib.auth.models import User
#from django.db import IntegrityError

from django.core.management import call_command
from django.core import mail
#my stuff
#from website.models import Organization
from surveys.models import *
#from surveys.tests.testdata import create_test_data
#from surveys.core import setup_instrument
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

# Create your tests here.
class ManagementCommandsTest(TestCase):
    ''' TESTS THAT THE ANSWER SURVEY VIEW BEHAVES PROPERLY '''
    def setUp(self):
        for u_i in range(15):
            u = User(username="testuser%s@tt.tt"%(u_i), email="testuser%s@tt.tt"%(u_i), password="password")
            u.save()
            o = Organization(
                    owner=u,
                    name="TestOrg%s"%(u_i),
                    phone=None,
                    address_line_1="Test st. %s"%(u_i),
                    address_line_2=None,
                    zip_code="7777",
                    city="Test Town",
                    country='NO'
                )
            o.save()

            for r_i in range(10):
                r = Respondent(
                        organization=o,
                        first_name=None,
                        last_name=None,
                        email="testrespondent%s@tt%s.tt"%(r_i, u_i),
                        receives_surveys=True
                    )
                r.save()

    def test_createtestsurveydata(self):
        pass

    def test_setupinstruments(self):
        logging.disable(logging.CRITICAL)

        instrument_list = Instrument.objects.all()
        dimension_list = Dimension.objects.all()
        scale_list = Scale.objects.all()
        item_list = Item.objects.all()

        #test starting condiditions
        self.assertEqual(len(instrument_list), 0)
        self.assertEqual(len(dimension_list), 0)
        self.assertEqual(len(scale_list), 0)
        self.assertEqual(len(item_list), 0)

        #test that running the command creates the expected items
        call_command('setupinstruments')

        instrument_list = Instrument.objects.all()
        dimension_list = Dimension.objects.all()
        scale_list = Scale.objects.all()
        item_list = Item.objects.all()

        self.assertEqual(len(instrument_list), 1)
        self.assertEqual(len(dimension_list), 3)
        self.assertEqual(len(scale_list), 1)
        self.assertEqual(len(item_list), 17)

        #test that running it again doesn't create any more DB entries
        call_command('setupinstruments')

        instrument_list = Instrument.objects.all()
        dimension_list = Dimension.objects.all()
        scale_list = Scale.objects.all()
        item_list = Item.objects.all()

        self.assertEqual(len(instrument_list), 1)
        self.assertEqual(len(dimension_list), 3)
        self.assertEqual(len(scale_list), 1)
        self.assertEqual(len(item_list), 17)

        logging.disable(logging.NOTSET)

    def test_dailysurveytasks(self):
        logging.disable(logging.CRITICAL)

        #some setup
        call_command('setupinstruments')
        instrument = Instrument.objects.get(id=1)
        user_list=User.objects.all()
        organization_list=Organization.objects.all()

        for organization in organization_list:
            survey_setting = survey_logic.configure_survey_setting(
                organization=organization,
                instrument=instrument,
                is_active=False
            )

        survey_setting_list = SurveySetting.objects.all()
        respondent_list = Respondent.objects.all()

        self.assertEqual(len(user_list), 15)
        self.assertEqual(len(organization_list), 15)
        self.assertEqual(len(respondent_list), 150)
        self.assertEqual(len(survey_setting_list), 15)

        #test that no surveys are sent when no organization has set an active product
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 0)
        si_list = SurveyInstance.objects.all()
        self.assertEqual(len(si_list), 0)
        call_command('dailysurveytasks')
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 0)
        si_list = SurveyInstance.objects.all()
        self.assertEqual(len(si_list), 0)
        self.assertEqual(len(RespondentEmail.objects.all()), 0)
        self.assertEqual(len(mail.outbox), 0)

        #test that a single survey is create with 10 instances when we change the setting of one org, and that 10 emails are sent
        active_org = Organization.objects.get(id=1)
        survey_setting = survey_logic.configure_survey_setting(
            organization=active_org,
            instrument=instrument,
            is_active=True
        )
        call_command('dailysurveytasks')
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 1)
        si_list = SurveyInstance.objects.all()
        self.assertEqual(len(si_list), 10)
        self.assertEqual(len(RespondentEmail.objects.all()), 10)
        self.assertEqual(len(mail.outbox), 10)

        #Test that it works when we activate two more orgs and check
        active_org = Organization.objects.get(id=2)
        survey_setting = survey_logic.configure_survey_setting(
            organization=active_org,
            instrument=instrument,
            is_active=True
        )
        active_org = Organization.objects.get(id=3)
        survey_setting = survey_logic.configure_survey_setting(
            organization=active_org,
            instrument=instrument,
            is_active=True
        )
        call_command('dailysurveytasks')
        survey_list = Survey.objects.all()
        self.assertEqual(len(survey_list), 3)
        si_list = SurveyInstance.objects.all()
        self.assertEqual(len(si_list), 30)
        self.assertEqual(len(RespondentEmail.objects.all()), 30)
        self.assertEqual(len(mail.outbox), 30)


        #test that due surveys are closed
        due_organization = Organization.objects.get(id=1)
        due_survey = Survey.objects.get(owner=due_organization)
        due_survey.date_close += datetime.timedelta(days=-360)
        due_survey.date_open += datetime.timedelta(days=-360)
        due_survey.save()
        due_survey_setting = SurveySetting.objects.get(organization=due_organization)
        due_survey_setting = survey_logic.configure_survey_setting(
            organization=due_organization,
            instrument=instrument,
            is_active=True
        )
        self.assertEqual(due_survey_setting.last_survey_close, due_survey.date_close)
        self.assertEqual(due_survey_setting.last_survey_open, due_survey.date_open)

        self.assertEqual(len(Survey.objects.filter(is_closed=True)), 0)
        call_command('dailysurveytasks')
        self.assertEqual(len(Survey.objects.filter(is_closed=True)), 1)

        logging.disable(logging.NOTSET)
