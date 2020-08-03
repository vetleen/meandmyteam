from django.conf import settings
from django.http import HttpRequest
#from django.utils.translation import gettext as _

#make sure we have the GA_KEY variable available in all templates 
def google_analytics(request: HttpRequest): 
    return {
        'GA_KEY': settings.GOOGLE_ANALYTICS_KEY,
    }
#Get the page title
def page_title(request: HttpRequest): 
    return {
        'PAGE_TITLE': settings.PAGE_TITLE,
    }