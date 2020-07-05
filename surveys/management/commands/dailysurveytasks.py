from django.core.management.base import BaseCommand, CommandError
from surveys.functions import daily_survey_maintenance

#my stuff
from surveys.core import survey_logic

#third party
import datetime

class Command(BaseCommand):
    help = 'Creates surveys for active products, instances of surveys for each coworker, and sends emails if it\'s time'

    def handle(*args, **kwargs):
        print('running daily survey tasks...')

        #check for surveys that need to be opened, open them
        organization_list = Organization.objects.all()
        for organization in organization_list:
            survey_logic.create_survey_if_due(organization)

        #check for surveys that need to be closed, close them
        survey_list = Survey.objects.filter(is_closed==False, date_close__lt=datetime.date.today())
        for survey in survey_list:
            survey_logic.close_survey_if_date_close_has_passed(survey)

        #create survey instances for new surveys, and if new employees have been added
        survey_list = Survey.objects.filter(is_closed==False)
        for survey in survey_list:
            survey_instances_from_survey(survey)

        #send out invitations to SurveyInstancesws where that hasn't been done

        #send out reminders for SurveyInstances that are due for reminders

        print('Done!')
