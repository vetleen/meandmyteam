from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = ''

    def handle(*args, **kwargs):
        print(settings.SECRET_KEY == '2#q*c)!_g3tw2vj_p%7+rjyq+taizilidc*lvc0m$y)$7@^09!')
