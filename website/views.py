from django.conf import settings

from website.forms import ChangePasswordForm, SignUpForm, LoginForm, EditAccountForm, ChoosePlanForm, CancelPlanForm, ResetPasswordForm
from website.models import Organization, Event

from django.views.generic.edit import CreateView, UpdateView, DeleteView #dont think this is needed anymore
from payments.tools.stripe_logic import *

from operator import itemgetter
import datetime

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext as _

from django.views import generic
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login, authenticate
from django.contrib import auth
from django.contrib import messages
from django.core.mail import send_mail



#class-based password reset views
from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_pk = settings.STRIPE_PUBLISHABLE_KEY
stripe_sk = settings.STRIPE_SECRET_KEY

#set up logging
import logging
logger = logging.getLogger('__name__')


# Create your views here.
def index(request):
    """View function for home page of site."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('surveys-dashboard'))

    context = {}

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def privacy_policy_view(request):
    ''' displays the sites privacy policy'''
    return render(request, 'privacy_policy_template.html')

def terms_view(request):
    ''' displays the sites terms and conditions'''
    return render(request, 'terms_template.html')

@login_required
def change_password(request):
    """View function for changing ones password."""

    form = ChangePasswordForm(user=request.user)
    context = {
        'form': form,
        'submit_button_text': _('Update password'),
        'back_button_text': _('Cancel'),
        'show_back_button': True,
    }
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = ChangePasswordForm(request.POST, user=request.user)
        context.update({'form': form})
        # Check if the form is valid:
        if form.is_valid():
            user = request.user
            if not user.check_password(form.cleaned_data['old_password']):
                messages.error(request, _('Password was not changed! You typed your old password in incorrectly, please try again.'), extra_tags='alert alert-warning')
            else:
                # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, request.user)
                # redirect to a new URL:
                messages.success(request, _('Your password was changed.'), extra_tags='alert alert-success')
            form = ChangePasswordForm(user=request.user)
            context.update({'form': form})
            return render(request, 'change_password_form.html', context)


    return render(request, 'change_password_form.html', context)

class PasswordResetRequestView(auth_views.PasswordResetView):
    email_template_name = 'account/reset_password_email.html'
    subject_template_name = 'account/password_reset_subject.txt'
    success_url = reverse_lazy('password-reset-request-received')
    template_name = 'account/password_reset_request_form.html'
    from_email = 'support@motpanel.com'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in variables
        context['submit_button_text'] = _('Send password reset link')
        return context

class PasswordResetRequestReceivedView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_request_received.html'


class PasswordResetView(SuccessMessageMixin, auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('password-reset-complete')
    template_name = 'account/password_reset_form.html'

class PasswordResetCompleteView(auth_views.PasswordChangeDoneView):
    template_name = ''

def password_reset_complete_view(request):
    #messages.success(request, 'Your password was changed. You can now use the new password to log in.', extra_tags='alert alert-success')
    return render(request, 'account/password_reset_complete.html')


def sign_up(request):
    """View function for signing up."""
    #logged in users are redirected
    if request.user.is_authenticated:
        messages.error(request, _('You are already signed in, and can\'t make a new account until you sign out.'), extra_tags='alert alert-warning')
        return render(request, 'you_did_something.html')

    #mark an event - someone visited this site
    event = Event(category='visited_sign_up_view')
    event.save()

    #create the form
    form = SignUpForm
    context = {
        'form': form,
        'submit_button_text': _('Sign up',)
    }
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = SignUpForm(request.POST)
        context.update({'form': form})
        # Check if the form is valid:
        if form.is_valid():
            
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['username'], form.cleaned_data['password'])
            user.save()
            organization = Organization(
                owner=user,
                phone = form.cleaned_data['phone'],
                name = form.cleaned_data['name'],
                address_line_1 = form.cleaned_data['address_line_1'],
                address_line_2 = form.cleaned_data['address_line_2'],
                zip_code = form.cleaned_data['zip_code'],
                city = form.cleaned_data['city'],
                country = form.cleaned_data['country'],
                accepted_terms_and_conditions = form.cleaned_data['accepted_terms_and_conditions'],
                )
            organization.save()
            messages.success(request, _("Welcome aboard. Let's start by adding some employees to survey!"), extra_tags='alert alert-success')
            send_mail(
                '[www] New user: %s!'%(user.username),
                'User: %s has signed up!'%(user.username),
                'sales@motpanel.com',
                ['sales@motpanel.com'],
                fail_silently=True,
            )
            if user is not None:
                auth.login(request, user)

            #mark an event - someone signed up successfully
            event = Event(category='completed_sign_up', user=user)
            event.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('surveys-dashboard'))
        else:
            #mark an event - someone failed to sign up
            comment = ""
            for field in form.visible_fields():
                if field.field.label != _("Choose a password") and field.field.label != _("Confirm password"):
                    field_data = "%s: %s \n"%(field.field.label, field.data)
                    comment+=(field_data)
            event = Event(category='failed_sign_up', comment=comment)
            event.save()
    return render(request, 'sign_up_form.html', context)

def login_view(request):
    """View function for logging in."""
    #is user already logged in?
    if request.user.is_authenticated:
        messages.error(request, _('You are already logged in.'), extra_tags='alert alert-warning')
        return HttpResponseRedirect(request.GET.get('next', reverse('surveys-dashboard')))

    #If we receive POST data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding it):
        form = LoginForm(request.POST)
        context = {
            'submit_button_text': _('Login'),
            'back_button_text': _('Cancel'),
            'show_back_button': False,
            'form': form,
            }
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                request.user.organization.update_subscription_paid_until()
                messages.success(request, _('You have logged in.'), extra_tags='alert alert-success')
                #mark an event - user logged in
                event = Event(category='completed_log_in', user=request.user, comment=None)
                event.save()

                return HttpResponseRedirect(request.GET.get('next', '/'))
    else:
        #make context
        form = LoginForm
        context = {
            'submit_button_text': _('Login'),
            'back_button_text': _('Cancel'),
            'show_back_button': False,
            'form': form,
            }
    return render(request, 'login_form.html', context)

def logout_view(request):
    """View function that logs userout and shows success message after logout."""
    auth.logout(request)
    messages.info(request, _('You have logged out successfully.'), extra_tags='alert alert-info')
    return render(request, 'logout_complete.html')

@login_required
def edit_account_view(request):
    """View function for editing account"""
    if request.user.is_authenticated:
        print(request.user.organization.phone)
        form = EditAccountForm(initial={
                #User model
                'username': request.user,
                # Organization model
                'name': request.user.organization.name,
                'phone': request.user.organization.phone,
                'address_line_1': request.user.organization.address_line_1,
                'address_line_2': request.user.organization.address_line_2,
                'zip_code' : request.user.organization.zip_code,
                'city': request.user.organization.city,
                'country': request.user.organization.country,
                },
            user=request.user
            )

        #If we receive POST data
        context = {
            'form': form,
            'submit_button_text': _('Update account details')
        }
        if request.method == 'POST':
            # Create a form instance and populate it with data from the request (binding):
            form = EditAccountForm(request.POST, user=request.user)
            context.update({'form': form})
            # Check if the form is valid:
            if form.is_valid():
                request.user.username = form.cleaned_data['username']
                request.user.email = form.cleaned_data['username']
                request.user.organization.name = form.cleaned_data['name']
                request.user.organization.phone = form.cleaned_data['phone']
                request.user.organization.address_line_1 = form.cleaned_data['address_line_1']
                request.user.organization.address_line_2 = form.cleaned_data['address_line_2']
                request.user.organization.zip_code = form.cleaned_data['zip_code']
                request.user.organization.city = form.cleaned_data['city']
                request.user.organization.country = form.cleaned_data['country']

                request.user.save()
                request.user.organization.save()
                messages.success(request, _('Your profile details was updated.'), extra_tags='alert alert-success')

        return render(request, 'edit_account_form.html', context)
    #if user not authenticated
    else:
        #this should never occcur
        logger.warning("%s %s: %s tried to edit someone else's account"%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
        messages.error(request, _("Can't edit profile when you are not logged in."), extra_tags='alert alert-danger')
        return HttpResponseRedirect(reverse('loginc'))
