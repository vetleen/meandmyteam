from django.core.management.base import BaseCommand, CommandError

#my stuff
from surveys.core import survey_logic
from surveys.models import *

#third party
import datetime


#set up logging
import logging
logger = logging.getLogger('__name__')

class Command(BaseCommand):
    help = "Creates surveys for active products, instances of surveys for each coworker, and sends emails if it's appropriate"

    def handle(*args, **kwargs):
        logger.warning("Running daily survey tasks...")
        #check for surveys that need to be closed, close them
        logger.warning("... closing due surveys.")
        survey_list = Survey.objects.filter(is_closed=False, date_close__lt=datetime.date.today())
        for survey in survey_list:
            survey_logic.close_survey_if_date_close_has_passed(survey)
        logger.warning("... done.")

        #check for surveys that need to be opened, open them
        logger.warning("... opening surveys.")
        organization_list = Organization.objects.all()
        for organization in organization_list:
            survey_logic.create_survey_if_due(organization)
        logger.warning("... done.")

        #create survey instances for new surveys, and if new employees have been added
        logger.warning("... creating survey instances.")
        survey_list = Survey.objects.filter(is_closed=False)
        for survey in survey_list:
            survey_logic.survey_instances_from_survey(survey)
        logger.warning("... done.")

        #send out invitations to SurveyInstances where that hasn't been done
        logger.warning("... sending emails.")
        for survey in survey_list:
            survey_instance_list = survey.surveyinstance_set.all()
            for survey_instance in survey_instance_list:
                try:
                    survey_logic.send_email_for_survey_instance(survey_instance)
                except AssertionError as err:
                    print("tried to send emails for survey instance with id #%s, belonging to organization %s. Got error: %s."%(survey_instance, survey_instance.owner, err))
        #
        logger.warning("... done.")
        logger.warning("All done.")
