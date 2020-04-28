from surveys.models import Organization, Employee, Survey, SurveyInstance, IntAnswer, TextAnswer, Question, Product, ProductSetting
from datetime import date, timedelta
from django.core.mail import send_mail

def configure_product(organziation, product, **kwargs):
    #make sure we have a ProductSetting object to work with or exit
    ps = ProductSetting.objects.filter(organziation=organziation, product=product)
    if ps.count() > 1:
        print('Oh no! There must be only 1 setting for each product, for each organization, but for %s and %s, we found %s.'%(organization, product, product_setting.count()))
        return
    elif ps.count() == 0:
        ps = ProductSetting(organziation=organziation, product=product)
        return ps

    #look for kwargs and update accordingly
    if 'is_active' in kwargs:
        ps.is_active = kwargs.get['is_active']
    if 'survey_interval' in kwargs:
        ps.survey_interval = kwargs.get['survey_interval']
    if 'last_survey_open' in kwargs:
        ps.last_survey_open = kwargs.get['last_survey_open']
    if 'last_survey_close' in kwargs:
        ps.last_survey_close = kwargs.get['last_survey_close']
    #save all changes
    ps.save()
    print ('setting has been through configure function and is now %s'%(ps))
    return ps

def check_when_next_survey(organization, product):
    pass
    #if surveys exist, find last to open, add intervall time to it and return it as date
    #else, return tomorrow
    #return date

def close_existing_survey_now(survey):
    survey.date_close = date.today() + timedelta(days=-1)
    survey.save()
    ps = configure_product(organziation, product, last_survey_close=date_close)

def open_existing_survey(survey, days_open):
    survey.date_open = date.today()
    survey.date_close = date.today() + timedelta(days=days_open)
    survey.save()
    ps = configure_product(organziation, product, last_survey_open=date_open, last_survey_close=date_close)

def create_survey(organization, product):
    print('called create_survey with %s and %s.'%(organization, product))
    s = Survey(
        product = product,
        owner = organization,
        date_open = date.today(),
        date_close = date_open + timedelta(days=organization.surveys_remain_open_days)
    )
    ps = configure_product(organziation, product, last_survey_open=date_open, last_survey_close=date_close)
    s.save()
    print('tried to make a survey, result was: %s, a %s.'%(s, type(s)))

def make_surveys_for_active_products(organization):
    print('running maintain_surveys on org.: %s.'%(organization))

    #some initial setup
    try:
        active_products = organization.active_products.all()
        active_products_count =  active_products.count()

    except Organization.DoesNotExist:
        print ('didn\'t find an organization')
        active_products_count = 0

    if active_products_count == 0:
        print ('exiting because 0 active products')
        return

    #We have active products, now let's make some surveys if it's time:
    else:
        print('dealing with %s active products.'%(active_products_count))
        #Look at each product and do this
        for product in active_products:
            ps = ProductSetting(organziation=organziation, product=product)
            print('looking at active product %s.'%(product))
            surveys = Survey.objects.filter(owner=organization, product=product)
            if surveys.count() == 0:
                print('found no preexisting surveys, so should make one')
                create_survey(organization, product) #this also sets the last open and close dates in ProductSettings
                #ps = ProductSetting(organziation=organziation, product=product)
            else:
                print('found preexisting surveys, so checking if it\'s time to make more')
                time_for_next_survey = ps.last_survey_open + timedelta(days=ps.survey_interval)
                if time_for_next_survey < date.today():
                    print('time to open a new survey because %s < todays date, %s'%(time_for_next_survey, date.today()))
                    create_survey(organization, product) #this also sets the last open and close dates in ProductSettings
                else:
                    print('not yet time to open a new survey because %s > todays date, %s'%(time_for_next_survey, date.today()))
                    #Do nothing

def make_survey_instances_for_active_surveys(organization):
    print('making survey instances for active surveys')
    #Filter surveys that close in the future
    surveys = Survey.objects.filter(owner=organization, date_close__gt=date.today()) #will return surveys for all products!
    #find list of employees for organization
    employees = Employee.objects.filter(organization=organization, receives_surveys=True)
    #for each active survey
    for survey in surveys:
        #for each employee
        for employee in employees:
            #see if there is a survey instance, if not make and send SI, if there is:
            if SurveyInstance.objects.filter(survey=survey, repondent=employee).count() < 1:
                si = SurveyInstance(survey=survey, repondent=employee)
                si.save()
                #should make answers??

# Function to Check if any survey instances should be sent out, do so and check as done
def send_out_survey_instance_emails(organization):
    #find all SurveyInstances
    sis = SurveyInstance.objects.filter(survey__owner=organization, survey__date_close__gt=date.today())
    for si in sis:
        if not si.sent_initial:
            print('Gotta send initial email for this SurveyInstance')
            send_mail(
                subject='Initial request to answer survey',
                message='Hi! \n Please answer! \n BR motpanel',
                from_email='surveys@motpanel.com',
                recipient_list=[si.respondent.email],
                fail_silently=True,
            )
            si.last_reminder = date.today()
            si.save()
        elif si.last_reminder < (date.today() + timedelta(days=-7)):
            print('Gotta send reminder for this SurveyInstance')
            send_mail(
                subject='Reminder to answer survey',
                message='Hi! \n Please answer! \n BR motpanel',
                from_email='surveys@motpanel.com',
                recipient_list=[si.respondent.email],
                fail_silently=True,
            )
            si.last_reminder = date.today()
            si.save()
        else:
            print('no emails to send for this SurveyInstance')

def daily_survey_maintenance():
    #get all organiaztions, and for eacH:
    print ('running daily_survey_maintenance...')
    organizations = Organization.objects.all()
    print('found %s organizations to maintain'%(organizations.count()))
    for org in organizations:
        print('maintaining %s...'%(org))
        make_surveys_for_active_products(org)
        make_survey_instances_for_active_surveys(org)
        send_out_survey_instance_emails(org)
