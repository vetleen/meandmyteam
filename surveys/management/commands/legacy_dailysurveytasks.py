from django.core.management.base import BaseCommand, CommandError
from surveys.functions import daily_survey_maintenance

class Command(BaseCommand):
    help = 'Creates surveys for active products, instances of surveys for each coworker, and sends emails if it\'s time'

    def handle(*args, **kwargs):
        print('running daily survey tasks...')
        daily_survey_maintenance()
        print('Done!')
