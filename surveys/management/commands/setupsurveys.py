from django.core.management.base import BaseCommand, CommandError
from surveys.models import *

class Command(BaseCommand):
    help = 'Creates Instruments and the Scales, Dimensions and Items that go with them, and saves them to the DB'
    print("Creating Instruments")

    def handle(*args, **kwargs):
        pass
