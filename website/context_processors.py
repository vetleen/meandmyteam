from django.conf import settings
from django.http import HttpRequest
 
#make sure we have the GA_KEY variable available in all templates 
def google_analytics(request: HttpRequest): 
    return {
        'GA_KEY': settings.GOOGLE_ANALYTICS_KEY,
    }