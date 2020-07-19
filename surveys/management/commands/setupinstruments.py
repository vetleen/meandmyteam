from django.core.management.base import BaseCommand, CommandError
from surveys.models import *

from surveys.core import employee_engagement_instrument
from surveys.core import setup_instrument
#set up logging
import logging
logger = logging.getLogger('__name__')

class Command(BaseCommand):
    help = 'Creates Instruments and the Scales, Dimensions and Items that go with them, and saves them to the DB'

    def handle(*args, **kwargs):
        logger.warning("Creating instruments...")
        raw_instrument_list = [employee_engagement_instrument.employee_engagement_instrument]
        logger.warning("... found we should have %s instruments."%(len(raw_instrument_list)))
        logger.warning("... calling setup_instrument for ...")
        for raw_instrument in raw_instrument_list:
            logger.warning("... ... %s."%(raw_instrument['instrument']['name']))
            setup_instrument.setup_instrument(raw_instrument)
            logger.warning("... ...done!")
        logger.warning("... done!")
        logger.warning("All done!")
