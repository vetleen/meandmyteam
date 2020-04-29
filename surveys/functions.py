from surveys.models import Organization, Employee, Survey, SurveyInstance, IntAnswer, TextAnswer, Question, Product, ProductSetting
from datetime import date, timedelta
from django.core.mail import send_mail

def configure_product(organization, product, **kwargs):
    #make sure we have a ProductSetting object to work with or exit
    ps = ProductSetting.objects.filter(organization=organization, product=product)
    if ps.count() == 1:
        ps=ps[0]
    elif ps.count() == 0:
        ps = ProductSetting(organization=organization, product=product)
        ps.save()
    else:
        return
    #look for kwargs and update accordingly
    if 'is_active' in kwargs:
        ps.is_active = kwargs.get('is_active', None)
    if 'survey_interval' in kwargs:
        ps.survey_interval = kwargs.get('survey_interval', None)
    if 'last_survey_open' in kwargs:
        ps.last_survey_open = kwargs.get('last_survey_open', None)
    if 'last_survey_close' in kwargs:
        ps.last_survey_close = kwargs.get('last_survey_close', None)
    #save all changes
    ps.save()
    return ps
'''
def check_when_next_survey(organization, product):
    pass
    #if surveys exist, find last to open, add intervall time to it and return it as date
    #else, return tomorrow
    #return date

def close_existing_survey_now(survey):
    survey.date_close = date.today() + timedelta(days=-1)
    survey.save()
    ps = configure_product(organization, product, last_survey_close=date_close)

def open_existing_survey(survey, days_open):
    survey.date_open = date.today()
    survey.date_close = date.today() + timedelta(days=days_open)
    survey.save()
    ps = configure_product(organization, product, last_survey_open=date_open, last_survey_close=date_close)
'''
def create_survey(organization, product, date_open=date.today()):
    date_close = date_open + timedelta(days=organization.surveys_remain_open_days)
    s = Survey(
        product = product,
        owner = organization,
        date_open = date_open,
        date_close = date_close
    )
    ps = configure_product(organization, product, last_survey_open=date_open, last_survey_close=date_close)
    s.save()

def make_surveys_for_active_products(organization):
    ''' A function that cycles through an organzixations active products and makes surveys if needed '''

    active_products = organization.active_products.all()

    #If no active products, go do something else
    if active_products.count() == 0:
        return

    #But if active products, look at each product and do things
    for product in active_products:
        #make sure it's configured and we have the config available
        ps = configure_product(organization=organization, product=product)

        #get existing surveys
        surveys = Survey.objects.filter(owner=organization, product=product)
        if surveys.count() == 0:
            create_survey(organization, product) #this also sets the last open and close dates in ProductSettings
        else:
            time_for_next_survey = ps.last_survey_open + timedelta(days=ps.survey_interval)
            if time_for_next_survey < date.today():
                create_survey(organization, product) #this also sets the last open and close dates in ProductSettings


def make_survey_instances_for_active_surveys(organization):
    #Filter surveys that are supposed to be active
    surveys = Survey.objects.filter(owner=organization, date_open__lte=date.today(), date_close__gt=date.today()) #will return surveys for all products!

    #find list of employees for organization
    employees = Employee.objects.filter(organization=organization, receives_surveys=True)

    #for each active survey
    for survey in surveys:
        #for each employee
        for employee in employees:
            #see if there is a survey instance, if not make and send SI, if there is:
            if SurveyInstance.objects.filter(survey=survey, respondent=employee).count() < 1:
                si = SurveyInstance(survey=survey, respondent=employee)
                si.save()

                #should make answers??

# Function to Check if any survey instances should be sent out, do so and check as done
def send_out_survey_instance_emails(organization):
    #find all SurveyInstances
    sis = SurveyInstance.objects.filter(survey__owner=organization, survey__date_close__gt=date.today())
    for si in sis:

        if not si.sent_initial:
            send_mail(
                subject='Initial request to answer survey',
                message='Hi! \n Please answer! \n BR motpanel',
                from_email='surveys@motpanel.com',
                recipient_list=[si.respondent.email],
                fail_silently=True,
            )
            si.sent_initial = True
            si.last_reminder = date.today()
            si.save()
        elif si.last_reminder < (date.today() + timedelta(days=-7)):
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
            pass

def daily_survey_maintenance():
    #get all organiaztions, and for eacH:
    organizations = Organization.objects.all()
    for org in organizations:
        make_surveys_for_active_products(org)
        make_survey_instances_for_active_surveys(org)
        send_out_survey_instance_emails(org)
