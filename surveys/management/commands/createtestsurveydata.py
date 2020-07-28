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

#set up logging
import logging
logger = logging.getLogger('__name__')


class Command(BaseCommand):
    help = 'Creates a few surveys and so on so ...'

    def handle(*args, **kwargs):
        logger.warning("\nCreating someone to test on...")
        #create a test organization (after running this command, you can log in with these credentials)
        tusername = "testuser@aa.aa"
        tuser = None
        try:
            tuser = User.objects.get(username=tusername)
        except User.DoesNotExist as err:
            tuser=User.objects.create_user(
                username=tusername,
                email=tusername,
                password="we567¥½ksjh0",
            )
            tuser.save()
            logger.warning("...created user: %s."%(tuser))
        assert tuser is not None, "tuser was None"

        torganization = None
        try:
            torganization = Organization.objects.get(owner=tuser)
        except Organization.DoesNotExist as err:
            torganization = Organization(
                owner=tuser,
                name="Test Organization #4",
                phone=None,
                address_line_1="Test street",
                address_line_2="",
                zip_code="9999",
                city="Testcity",
                country="NO"
            )
            torganization.save()
            logger.warning("...created organization: %s."%(torganization))
        assert torganization is not None, "torganization was None"

        #create little employees
        employee_target = 7
        existing_employees = Respondent.objects.filter(organization=torganization)
        if len(existing_employees) < employee_target:
            for e in range(employee_target-len(existing_employees)):
                email = "testemployee" + str(e+1+len(existing_employees)) + "@aa.aa"
                temployee = Respondent(organization=torganization, email=email)
                temployee.save()
                logger.warning("...created employee: %s."%(temployee))

        #create an instrument
        logger.warning("Ensuring there is an instrument in place...")
        if len(Instrument.objects.all()) > 0:
            tinstrument = Instrument.objects.get(id=1)
            logger.warning("...there is already one: %s"%(tinstrument))
        else:
            ri = employee_engagement_instrument.employee_engagement_instrument
            setup_instrument.setup_instrument(ri)
            tinstrument= Instrument.objects.get(id=1)

            logger.warning("...there wasn't already one, so I made one: %s"%(tinstrument))

        #configure surveys
        tsurvey_setting = survey_logic.configure_survey_setting(
            organization=torganization,
            instrument=tinstrument,
            is_active=True
        )

        logger.warning("...created survey settings: %s"%(tsurvey_setting))

        #create surveys
        logger.warning("Closing existing surveys....")
        open_surveys = Survey.objects.filter(owner=torganization, is_closed=False)
        for survey in open_surveys:
            survey_logic.close_survey(survey)
            ("... closed a survey with id %s!"%(survey.id))
        logger.warning("... done!")
        surveys_target = 5
        survey_list = []
        current_date = date.today()
        for i in range(surveys_target):
            logger.warning("Creating a survey (number %s) for the test-organization..."%(i))

            tsurvey = survey_logic.create_survey(owner=torganization, instrument_list=[tinstrument, ])
            survey_list.append(tsurvey)
            logger.warning("...created a survey: %s"%(tsurvey))

            tsurvey_instance_list = survey_logic.survey_instances_from_survey(tsurvey)
            logger.warning("...created %s survey instances."%(len(tsurvey_instance_list)))

            #send emails:
            #for survey_instance in tsurvey_instance_list:
            #    survey_logic.send_email_for_survey_instance(survey_instance)
            #    logger.warning("... sent an email to %s"%(survey_instance.respondent))

            #answer survey
            logger.warning("... answering this survey...")
            for tsinstance in tsurvey_instance_list:
                logger.warning("... ...  %s is answering..."%(tsinstance.respondent))
                for titem in tsinstance.get_items():
                    answer_value = random.randint(titem.survey_item.item_dimension.scale.min_value, titem.survey_item.item_dimension.scale.max_value)
                    titem.answer_item(answer_value)
                tsinstance.check_completed()

            #close survey
            logger.warning("...moving survey back in time")

            current_date += timedelta(days=-90)
            tsurvey.date_close = current_date
            tsurvey.date_open = current_date + timedelta(days=-10)
            tsurvey.save()
            logger.warning("...done.")
            logger.warning("...closing survey with id %s"%(tsurvey.id))
            survey_logic.close_survey_if_date_close_has_passed(tsurvey)
            logger.warning("...done.")

        #update survey setting
        tsurvey_setting.check_last_survey_dates()

        logger.warning("All done!")
