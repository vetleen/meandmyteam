from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect

#from django.db import RelatedObjectDoesNotExist

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
from surveys.forms import AddRespondentForm, EditRespondentForm
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
    form = AddRespondentForm
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

            #decalare success and make a new form for the next employee
            messages.success(request, 'You have added a coworker (%s)! You can continue to add more below.'%(form.cleaned_data['email']), extra_tags='alert alert-success')
            form = AddRespondentForm
            context.update({'form': form})
    #finally, return the prepared view
    return render(request, 'add_or_remove_employees.html', context)

@login_required
def edit_employee_view(request, **kwargs):
    #find thje Respondent we are trying to edit
    uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64', None)))
    respondent = get_object_or_404(Respondent, pk=uid)

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
    uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64', None)))
    respondent = get_object_or_404(Respondent, pk=uid)
    if respondent.organization.owner == request.user:
        messages.info(request, '%s was permanently deleted, and will not receive future surveys.'%(respondent.email), extra_tags='alert alert-warning')
        respondent.delete()
        #also update stripe subscription quantity
        q = request.user.organization.update_stripe_subscription_quantity()
        return HttpResponseRedirect(request.GET.get('next', reverse('surveys-add-or-remove-employees')))
    else:
        return HttpResponseForbidden()

def dashboard_view(request):
    """View function for the dashboard"""

    #grab employee list, and count them
    employee_list = request.user.organization.respondent_set.all()
    employee_count = employee_list.count()

    #get the organization's closed surveys
    surveys_raw = Survey.objects.filter(owner=request.user.organization).order_by('-date_close') #the first item is the latest survey

    #find the open survey, if any
    open_surveys_list = [s for s in surveys_raw if s.is_closed == False]
    if len(open_surveys_list) > 1:
        logger.warning(
        "%s %s %s dashboard_view: Found 2 open surveys for organization: %s"\
        %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', __name__, request.user.organization))
    open_survey = None
    if len(open_surveys_list) > 0:
        open_survey=open_surveys_list[0]

    #make a list of closed surveys
    closed_surveys_list = [survey_logic.get_results_from_survey(s) for s in surveys_raw if s.is_closed == True]

    #pop out the latest one
    latest_survey = None
    if len(closed_surveys_list) > 0:
        latest_survey = closed_surveys_list.pop(-1)

    #set closed_surveys_list to None if there are no surveys in it
    if len(closed_surveys_list) < 1:
        closed_surveys_list = None

    #get the subscription and pass that in in there
    stripe_subscription = None
    if request.user.organization.stripe_subscription_id is not None:
            stripe_subscription = stripe_logic.retrieve_stripe_subscription(request.user.organization.stripe_subscription_id)

    #find list of active instruments
    active_instrument_list = []
    instrument_settings_list = SurveySetting.objects.filter(organization=request.user.organization)
    for isetting in instrument_settings_list:
        active_instrument_list.append(isetting.instrument)

    #collect all the info that the dashboard needs (and maybe then some?)
    context = {
        'todays_date': datetime.date.today(),
        'employee_count': employee_count,
        'employee_list': employee_list,
        'stripe_subscription': stripe_subscription,
        'active_instrument_list': active_instrument_list,
        'open_survey': open_survey,
        'closed_surveys_list': closed_surveys_list,
        'latest_survey': latest_survey
    }

    return render(request, 'dashboard.html', context)
