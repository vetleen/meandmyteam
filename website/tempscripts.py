import datetime
from website.models import Plan, Subscriber
u = Subscriber.objects.get(pk=1)
u.is_active()


#import website.tempscripts
