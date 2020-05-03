from surveys.models import Organization, Employee, Survey, SurveyInstance, IntAnswer, TextAnswer, ProductSetting
from datetime import date, timedelta
from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string



def configure_product(organization, product, **kwargs):
    #make sure we have a ProductSetting object to work with or exit
    if not isinstance(organization, Organization):
        raise TypeError('configure_product() takes an argument organization that must be an instance of models.Organziation, was %s'%(type(organization)))
    if not isinstance(product, Product):
        raise TypeError('configure_product() takes an argument product that must be an instance of models.Product, was %s'%(type(product)))

    ps = ProductSetting.objects.filter(organization=organization, product=product)
    if ps.count() == 0:
        ps = ProductSetting(organization=organization, product=product)
        ps.save()
    else:
        ps=ps[0]
    #look for kwargs and update accordingly
    #if 'is_active' in kwargs:
    #    ps.is_active = kwargs.get('is_active', None)
    if 'survey_interval' in kwargs:
        ps.survey_interval = kwargs.get('survey_interval', None)
    if 'last_survey_open' in kwargs:
        ps.last_survey_open = kwargs.get('last_survey_open', None)
    if 'last_survey_close' in kwargs:
        ps.last_survey_close = kwargs.get('last_survey_close', None)
    if 'surveys_remain_open_days' in kwargs:
        ps.surveys_remain_open_days = kwargs.get('surveys_remain_open_days', None)
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
    ps=configure_product(organization, product)
    if ps.last_survey_open is not None and ps.last_survey_open > date_open:
        raise NotImplementedError('The create_survey() function does not yet support creating a new survey when the passed date_open (%s) is before the pre-existing ProductSetting.last_survey_open (%s).'%(date_open, ps.last_survey_open))
    date_close = date_open + timedelta(days=ps.surveys_remain_open_days)
    s = Survey(
        product = product,
        owner = organization,
        date_open = date_open,
        date_close = date_close
    )
    #notice that this may not deal with cases where a previously created survey is set in the future. This should not be a problem if functions are called in order
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
def send_email_about_survey_instance(si, email_txt_template, email_html_template, subject_template):

    #from django.shortcuts import render

    si_idb64 = si.si_idb64
    contact_person = si.survey.owner.owner.email
    if si.survey.owner.owner.first_name is not None and si.survey.owner.owner.last_name is not None:
        contact_person = '%s %s'%(si.survey.owner.owner.first_name, si.survey.owner.owner.last_name)


    context={
            'si_idb64':si_idb64,
            'organization': si.survey.owner.name,
            'contact_person': contact_person
            }
    #content for the email
    subject=render_to_string(subject_template, context).rstrip("\n\r")
    text_content=render_to_string(email_txt_template, context)
    html_content=render_to_string(email_html_template, context)
    from_email='surveys@motpanel.com'
    to=[si.respondent.email]

    #make and send email
    email_message = EmailMultiAlternatives(subject, text_content, from_email, to)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()
    si.sent_initial = True
    si.last_reminder = date.today()
    si.save()


def send_out_survey_instance_emails(organization):
    #find all SurveyInstances
    sis = SurveyInstance.objects.filter(survey__owner=organization, survey__date_close__gt=date.today())
    for si in sis:

        if not si.sent_initial:
            send_email_about_survey_instance(
                si,
                email_txt_template='emails/new_survey_instance_email_txt.html',
                email_html_template='emails/new_survey_instance_email_html.html',
                subject_template='emails/new_survey_subject.txt'
            )
        elif si.last_reminder < (date.today() + timedelta(days=-7)):
            send_email_about_survey_instance(
                si,
                email_txt_template='emails/remind_survey_instance_email_txt.html',
                email_html_template='emails/remind_survey_instance_email_html.html',
                subject_template='emails/remind_survey_subject.txt'
            )
        else:
            pass

def daily_survey_maintenance():
    #get all organiaztions, and for eacH:
    organizations = Organization.objects.all()
    for org in organizations:
        make_surveys_for_active_products(org)
        make_survey_instances_for_active_surveys(org)
        send_out_survey_instance_emails(org)
