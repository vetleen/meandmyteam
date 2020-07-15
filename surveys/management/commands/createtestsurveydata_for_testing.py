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
        logger.info("\nCreating someone to test on...")
        #create a test organization (after running this command, you can log in with these credentials)
        tusername = "testuser1@aa.aa"
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
            logger.info("...created user: %s."%(tuser))
        assert tuser is not None, "tuser was None"

        torganization = None
        try:
            torganization = Organization.objects.get(owner=tuser)
        except Organization.DoesNotExist as err:
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
            logger.info("...created organization: %s."%(torganization))
        assert torganization is not None, "torganization was None"

        #create little employees
        employee_target = 5
        existing_employees = Respondent.objects.filter(organization=torganization)
        if len(existing_employees) < employee_target:
            for e in range(employee_target-len(existing_employees)):
                email = "testemployee" + str(e+1+len(existing_employees)) + "@aa.aa"
                temployee = Respondent(organization=torganization, email=email)
                temployee.save()
                logger.info("...created employee: %s."%(temployee))

        #create an instrument
        logger.info("Ensuring there is an instrument in place...")
        if len(Instrument.objects.all()) > 0:
            tinstrument = Instrument.objects.get(id=1)
            logger.info("...there is already one: %s"%(tinstrument))
        else:
            ri = employee_engagement_instrument.employee_engagement_instrument
            setup_instrument.setup_instrument(ri)
            tinstrument= Instrument.objects.get(id=1)

            logger.info("...there wasn't already one, so I made one: %s"%(tinstrument))

        #configure surveys
        tsurvey_setting = survey_logic.configure_survey_setting(
            organization=torganization,
            instrument=tinstrument,
            is_active=True
        )

        logger.info("...created survey settings: %s"%(tsurvey_setting))

        #create surveys
        logger.info("Closing existing surveys....")
        open_surveys = Survey.objects.filter(owner=torganization, is_closed=False)
        for survey in open_surveys:
            survey_logic.close_survey(survey)
        logger.info("... done!")
        surveys_target = 3
        survey_list = []
        for i in range(surveys_target):
            logger.info("Creating a survey for the test-organization...")

            tsurvey = survey_logic.create_survey(owner=torganization, instrument_list=[tinstrument, ])
            survey_list.append(tsurvey)
            logger.info("...created a survey: %s"%(tsurvey))

            tsurvey_instance_list = survey_logic.survey_instances_from_survey(tsurvey)
            logger.info("...created %s survey instances."%(len(tsurvey_instance_list)))

            #send emails:
            for survey_instance in tsurvey_instance_list:
                survey_logic.send_email_for_survey_instance(survey_instance)

                #answer survey
                logger.info("... answering this survey...")
                for tsinstance in tsurvey_instance_list:
                    logger.info("... ...  %s is answering..."%(tsinstance.respondent))
                    for titem in tsinstance.get_items():
                        answer_value = random.randint(titem.survey_item.item_dimension.scale.min_value, titem.survey_item.item_dimension.scale.max_value)
                        titem = survey_logic.answer_item(titem, answer_value)
                survey_instance.check_completed()

            #close survey
            logger.info("Closing survey....")
            tsurvey = survey_logic.close_survey(tsurvey)
            logger.info("...done!")

        #move them back in time
        #survey.date_close

        logger.info("All done!")
