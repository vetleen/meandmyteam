from django.core.management.base import BaseCommand, CommandError

from surveys.models import *
from website.models import Organization
from django.db import IntegrityError
from datetime import date, timedelta


from surveys.tests.testdata import create_test_data
from surveys.core import setup_instrument
from surveys.core import employee_engagement_instrument
from surveys.core import survey_logic
import random

class Command(BaseCommand):
    help = 'Creates a few surveys and so on so ...'

    def handle(*args, **kwargs):
        print("\nCreating someone to test on...")
        #create a test organization (after running this command, you can log in with these credentials)
        tuser=User.objects.create_user(
            username="testuser1@aa.aa",
            email="testuser1@aa.aa",
            password="we567¥½ksjh0",
        )
        tuser.save()
        print("...created user: %s."%(tuser))

        torganization = Organization(
            owner=tuser,
            name="Test Organization #1",
            phone=None,
            address_line_1="Test street",
            address_line_2="",
            zip_code="9999",
            city="Testcity",
            country="NO"
        )
        torganization.save()
        print("...created organization: %s."%(torganization))

        #create little employees
        for e in range(20):
            email = "testemployee" + str(e+1) + "@aa.aa"
            temployee = Respondent(organization=torganization, email=email)
            temployee.save()
            print("...created employee: %s."%(temployee))

        #create an instrument
        print("Ensuring there is an instrument in place...")
        if len(Instrument.objects.all()) > 0:
            tinstrument= Instrument.objects.get(id=1)
            print("...there is already one: %s"%(tinstrument))
        else:
            ri = employee_engagement_instrument.employee_engagement_instrument
            setup_instrument.setup_instrument(ri)
            tinstrument= Instrument.objects.get(id=1)

            print("...there wasn't already one, so I made one: %s"%(tinstrument))

        #create a survey
        print("Creating a survey for the test-organization...")
        tsurvey_setting = survey_logic.configure_survey_setting(
            organization=torganization,
            instrument=tinstrument,
            is_active=True
        )

        print("...created survey settings: %s"%(tsurvey_setting))

        tsurvey = survey_logic.create_survey(owner=torganization, instrument_list=[tinstrument, ])
        print("...created a survey: %s"%(tsurvey))

        tsurvey_instance_list = survey_logic.survey_instances_from_survey(tsurvey)
        print("...created %s survey instances."%(len(tsurvey_instance_list)))

        #answer survey
        print("Creating answers to the survey...")
        for tsinstance in tsurvey_instance_list:
            print("...answering survey for %s."%(tsinstance.respondent))
            for titem in tsinstance.get_items():
                answer_value = random.randint(titem.survey_item.item_dimension.scale.min_value, titem.survey_item.item_dimension.scale.max_value)
                titem = survey_logic.answer_item(titem, answer_value)

        #close survey
        print("Closing survey....")
        tsurvey = survey_logic.close_survey(tsurvey)
        print("...done!")

        print("All done!")
