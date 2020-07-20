import math
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils.encoding import DjangoUnicodeDecodeError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

#from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text


#my stuff
from surveys.models import *
from surveys.core import survey_logic
from payments.tools import stripe_logic

#custom forms and models
from surveys.forms import AddRespondentForm, EditRespondentForm, EditSurveySettingsForm, AnswerSurveyForm
from surveys.models import Respondent


import datetime

#set up logging
import logging
logger = logging.getLogger('__name__')

# Create your views here.
@login_required
def add_or_remove_employee_view(request):
    """View function for adding employees."""

    #Prepare a normal GET view that will be shown no matter what:
    organization = request.user.organization
    employee_list = organization.respondent_set.all()
    form = AddRespondentForm()
    context = {
        'form': form,
        'submit_button_text': 'Add employee',
        'employee_list': employee_list,
    }
    # If this is a POST request, then process the Form bfore showing the view
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = AddRespondentForm(request.POST)
        context.update({'form': form})
        # Check if the form is valid:
        if form.is_valid():
            r = Respondent(
                organization = organization,
                email = form.cleaned_data['email'],
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name']
            )
            r.save()

            #also update stripe subscription quantity
            q = request.user.organization.update_stripe_subscription_quantity()

            #declare success and make a new form for the next employee
            messages.success(request, 'You have added a coworker (%s)! You can continue to add more below.'%(form.cleaned_data['email']), extra_tags='alert alert-success')
            form = AddRespondentForm()
            context.update({'form': form})
    #finally, return the prepared view
    return render(request, 'add_or_remove_employees.html', context)

@login_required
def edit_employee_view(request, **kwargs):
    #find the Respondent we are trying to edit
    try:
        uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64', None)))
        respondent = Respondent.objects.get(pk=uid)
    except Exception as err:
        logger.exception("%s %s: edit_employee_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        raise Http404("We couldn't find the employee you were looking for.")

    #check that User is allowed to change this Respondent
    if not request.user == respondent.organization.owner:
        return HttpResponseForbidden()

    #Prepare form that will be shown if this request is not a valid POST-ed form:
    data ={
        'email': respondent.email,
        'first_name': respondent.first_name,
        'last_name': respondent.last_name
    }
    form = EditRespondentForm(initial=data)
    context = {
        'form': form,
        'submit_button_text': 'Update',
        }

    #Check if POST, and deal with it:
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = EditRespondentForm(request.POST, respondent_id=respondent.pk)
        context.update({'form': form})
        # Check if the form is valid:
        if form.is_valid():
            respondent.email = form.cleaned_data['email']
            respondent.first_name = form.cleaned_data['first_name']
            respondent.last_name = form.cleaned_data['last_name']
            respondent.save()
            messages.success(request, 'Employee was updated.', extra_tags='alert alert-success')
            #no point hanging arouhnd here if it worked
            return HttpResponseRedirect(request.GET.get('next', reverse('surveys-add-or-remove-employees')))

    #return the form (blank or invalid), ready for input
    return render(request, 'edit_employee.html', context)

@login_required
def delete_employee_view(request, **kwargs):
    #find the Respondent we are trying to delete
    try:
        uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64', None)))
        respondent = Respondent.objects.get(pk=uid)
    except (Respondent.DoesNotExist, DjangoUnicodeDecodeError) as err:
        logger.exception("%s %s: edit_employee_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        raise Http404("We couldn't find the employee you were looking for.")


    #check that User is allowed to change this Respondent
    if not request.user == respondent.organization.owner:
        return HttpResponseForbidden()

    else:
        messages.info(request, '%s was permanently deleted, and will not receive future surveys.'%(respondent.email), extra_tags='alert alert-warning')
        respondent.delete()
        #also update stripe subscription quantity
        q = request.user.organization.update_stripe_subscription_quantity()
        return HttpResponseRedirect(request.GET.get('next', reverse('surveys-add-or-remove-employees')))

@login_required
def dashboard_view(request):
    """View function for the dashboard"""

    #grab employee list, and count them
    employee_list = request.user.organization.respondent_set.all()
    employee_count = employee_list.count()

    #get the Stripe subscription
    stripe_subscription = None
    if request.user.organization.stripe_subscription_id is not None:
            stripe_subscription = stripe_logic.retrieve_stripe_subscription(request.user.organization.stripe_subscription_id)

    #find list of active instruments
    active_instrument_list = []
    instrument_settings_list = SurveySetting.objects.filter(organization=request.user.organization)
    for isetting in instrument_settings_list:
        if isetting.is_active == True:
            active_instrument_list.append(isetting.instrument)
    print(active_instrument_list)

    #find inactive_instrument_list
    inactive_instrument_list = [i for i in Instrument.objects.all() if i not in active_instrument_list]

    #get latest data for active instruments
    active_instrument_data = None
    if len(active_instrument_list) > 0:
        active_instrument_data = []
        for instrument in active_instrument_list:
            #get data
            latest_instrument_data = survey_logic.get_results_from_instrument(
                instrument=instrument,
                organization=request.user.organization,
                depth=10)
            #sort out open surveys
            open_survey=None
            closed_surveys=None
            if latest_instrument_data is not None:
                for survey_data_point in latest_instrument_data['surveys']:
                    if survey_data_point['survey'].is_closed == False:
                        open_survey=survey_data_point['survey']

                    else:
                        if closed_surveys is None:
                            closed_surveys = []
                        closed_surveys.append(survey_data_point)

                #append data
                active_instrument_data.append({
                    'instrument':instrument,
                    'closed_surveys': closed_surveys,
                    'open_survey': open_survey
                })
            else:
                active_instrument_data.append({
                    'instrument':instrument,
                    'closed_surveys': None,
                    'open_survey': None
                })

    #collect all the info that the dashboard needs (and maybe then some?)
    context = {
        'todays_date': datetime.date.today(),
        'employee_count': employee_count,
        'employee_list': employee_list,
        'stripe_subscription': stripe_subscription,
        'inactive_instrument_list': inactive_instrument_list,
        'active_instrument_data': active_instrument_data,
    }

    return render(request, 'dashboard.html', context)

@login_required
def setup_instrument_view(request, **kwargs):
    #get the Instrument to be configured
    instrument_slug_name = kwargs.get('instrument', None)
    instrument = get_object_or_404(Instrument, slug_name=instrument_slug_name)

    #get the SurveySetting to be configured
    try:
        survey_setting = SurveySetting.objects.get(organization=request.user.organization, instrument=instrument)
    except SurveySetting.DoesNotExist as err:
        survey_setting = survey_logic.configure_survey_setting(organization=request.user.organization, instrument=instrument)
        survey_setting.save()

    #prepare a form in case it's a get request
    data={
        'is_active':  survey_setting.is_active,
        'survey_interval': survey_setting.survey_interval,
        'surveys_remain_open_days': survey_setting.surveys_remain_open_days,
    }
    form = EditSurveySettingsForm(initial=data)

    #if post, validate form and save, redirect to dashboard
    if request.method == 'POST':
        form=EditSurveySettingsForm(request.POST)
        if form.is_valid():
            #update settings
            survey_setting.is_active = form.cleaned_data['is_active']
            survey_setting.survey_interval = form.cleaned_data['survey_interval']
            survey_setting.surveys_remain_open_days = form.cleaned_data['surveys_remain_open_days']
            survey_setting.save()
            #report back
            if survey_setting.is_active == True:
                success_string = "Your settings were updated successfully, %s tracking is ACTIVE!"%(survey_setting.instrument.name)
                messages.success(request, success_string, extra_tags='alert alert-success')
            else:
                success_string = "Your settings were updated successfully, %s tracking is INACTIVE!"%(survey_setting.instrument.name)
                messages.success(request, success_string, extra_tags='alert alert-warning')

            #redirect to dashboard
            return HttpResponseRedirect(reverse('surveys-dashboard'))

    #if get, make form, return form,

    context={
        'form': form,
        'instrument': instrument,
        'submit_button_text': "Update settings"
    }
    return render(request, 'setup_instrument.html', context)

@login_required
def survey_details_view(request, **kwargs):
    #get the relevant survey
    try:
        uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64', None)))
        survey = Survey.objects.get(pk=uid)
        assert survey.is_closed == True, \
            "Cannot view details of a survey that is not closed."
    except (Survey.DoesNotExist, DjangoUnicodeDecodeError, AssertionError) as err:
        logger.exception("%s %s: edit_employee_view: (user: %s) %s: %s."\
            %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        raise Http404("We couldn't find the survey you were looking for.")

    #check that User is allowed to view this survey
    try:
        assert request.user == survey.owner.owner, \
            "This survey does not belong to the user that is requesting it."
    except AssertionError as err:
        logger.exception("%s %s: edit_employee_view: (user: %s) %s: %s."\
            %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        return HttpResponseForbidden()

    #get the Instrument that we want to view the results for
    try:
        instrument_slug_name = kwargs.get('instrument', None)
        instrument = Instrument.objects.get(slug_name=instrument_slug_name)
    except Instrument.DoesNotExist as err:
        logger.exception("%s %s: edit_employee_view: (user: %s) %s: %s."\
            %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        raise Http404("We couldn't find that instrument you were looking for.")

    #get the survey_data
    survey_data = survey_logic.get_results_from_survey(survey=survey, instrument=instrument)

    context = {
        'survey_data': survey_data,
        'instrument': instrument
    }

    return render(request, 'instrument_report.html', context)

def answer_survey_view(request, **kwargs):
    #Validate link and get the correct survey_instance or 404
    try:
        #get the si-id and token from the url, and check that it's format is correct
        url_token = kwargs.get('token', None)
        url_token_args = url_token.split("-")
        assert len(url_token_args) == 2, \
            "Faulty link (wrong link format)"
        #get the associated SurveyInstance
        si_id = int(force_text(urlsafe_base64_decode(url_token_args[0])))
        survey_instance = SurveyInstance.objects.get(id=si_id)
        #ensure the url_token matches the SurveyInstance
        assert survey_instance.get_hash_string() == url_token_args[1], \
            "Faulty link (invalid hash)"
        #ensure the Survey that the SurveyInstance belongs to is still open
        assert survey_instance.survey.date_close >= datetime.date.today(), \
            "This survey has already closed, closed %s."%(survey_instance.survey.date_close)

    except (AssertionError, SurveyInstance.DoesNotExist, DjangoUnicodeDecodeError) as err:
        logger.exception("%s %s: answer_survey_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        raise Http404("The survey you asked for does not exist. If you pasted a link, make sure you got the entire link.")

    #get the page argument, to see if we should be inn the paginated pages, and if so, which one
    page=kwargs.get('page', None)
    if page is not None:
        page = int(page)

    # make the context
    context = {
        'survey_instance': survey_instance,
        'page': page,
        'submit_button_text': 'Continue',

    }

    #set how many questions will be shown per page
    page_size = 5

    #if this view was requested without a page argument, we can skip forward a bit
    if page is None:
        #Go directly to first unanswered item if survey was started but not completed:
        if survey_instance.check_completed() == False and survey_instance.started == True:
            items = survey_instance.surveyinstanceitem_set.all().order_by('pk')
            answered_item_counter = 0
            for item in items:
                answered_item_counter+=1
                if item.answered == False:
                    current_page = math.ceil((answered_item_counter/page_size))
                    messages.info(request, "Welcome back! We saved your place, so you can continue where you left off.", extra_tags='alert alert-info')
                    return HttpResponseRedirect(reverse('surveys-answer-survey-pages', args=(url_token, current_page)))

        #otherwise show a pretty plain view
        return render(request, 'answer_survey.html', context)

    #Show questions now that we know we are in the paginated part
    #make a list 'item_list' containing exactly the items the user should be asked
    all_survey_instance_items_list=survey_instance.surveyinstanceitem_set.all().order_by('pk')
    item_list = []
    last_item_id = page*page_size
    for count, item in enumerate(all_survey_instance_items_list):
        if count < last_item_id and count >= (last_item_id-page_size):
            item_list.append(item)

    #add the progress so the progress bar may be shown
    progress = last_item_id/len(all_survey_instance_items_list)*100
    if progress > 100:
        progress = 100
    context.update({'progress': progress})

    #make the form, including previous answers if any
    data={}
    #get previous answers for the questions in qlist and add them to the dict
    for i in item_list:
        if i.answered == True:
            a = i.answer
            data.update({'item_%s'%(i.pk): a})
    form=AnswerSurveyForm(items=item_list, initial=data)
    context.update({'form': form})

    #did the user POST something?
    if request.method == 'POST':

        #overwrite the existing form with the values POSTED
        posted_form=AnswerSurveyForm(request.POST, items=item_list)
        context.update({'form': posted_form})

        #deal with data if it's valid
        if posted_form.is_valid():
            for answer in posted_form.cleaned_data:
                # identify the question that has been answered
                item_id = int(answer.replace('item_', ''))
                item = SurveyInstanceItem.objects.get(id=item_id)
                #make sure it's in the item_list
                try:
                    assert item in item_list, \
                        "An answer was submitted for an unexpected item with the id %s, but expected one of %s."%\
                        (item.id, [item.id for item in item_list])
                except AssertionError as err:
                    logger.exception(
                        "%s %s: answer_survey_view: (user: %s) %s: %s."\
                        %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
                    return HttpResponseForbidden()

                # find the value that has been provided as the answer
                if isinstance(item, RatioSurveyInstanceItem):
                    value=int(posted_form.cleaned_data[answer])

                #elif other types of scales
                else:
                    logger.warning(
                        "%s %s: %s: tried answer a SurveyInstanceItem, but its subclass (%s) was not recognized:\n---\"%s\""\
                        %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, type(item), item)
                    )
                    value=None

                # use the answer method of the question to create answer objects for this si
                if value is not None:
                    item.answer_item(value=value)

            #if there are more questions, send them to the next page
            if len(all_survey_instance_items_list) > int(page)*page_size:
                return HttpResponseRedirect(reverse('surveys-answer-survey-pages', args=(url_token, page+1)))

            #else, we are done answering, and redirect to thank you message
            return HttpResponseRedirect(reverse('surveys-answer-survey', args=(url_token, )))

    return render(request, 'answer_survey.html', context)
