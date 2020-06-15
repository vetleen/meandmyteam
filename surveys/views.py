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


#from payments.utils.stripe_logic import *
from datetime import date, datetime

#custom forms and models
from surveys.forms import AddRespondentForm, EditRespondentForm
from surveys.models import Respondent

#set up logging
import logging
import datetime
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
