from django.conf import settings

from website.forms import ChangePasswordForm, SignUpForm, LoginForm, EditAccountForm, ChoosePlanForm, CancelPlanForm, ResetPasswordForm
from website.models import Subscriber
from surveys.models import Organization
from django.views.generic.edit import CreateView, UpdateView, DeleteView #dont think this is needed anymore
from payments.utils.stripe_logic import *

from operator import itemgetter
import datetime

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

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
        'submit_button_text': 'Update password',
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
                messages.error(request, 'Password was not changed! You typed your old password in incorrectly, please try again.', extra_tags='alert alert-warning')
            else:
                # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, request.user)
                # redirect to a new URL:
                messages.success(request, 'Your password was changed.', extra_tags='alert alert-success')
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
        context['submit_button_text'] = 'Send password reset link'
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
        messages.error(request, 'You are already signed in, and can\'t make a new account until you sign out.', extra_tags='alert alert-warning')
        return render(request, 'you_did_something.html')

    form = SignUpForm
    context = {
        'form': form,
        'submit_button_text': 'Sign up',
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
            subscriber = Subscriber(user=user)
            subscriber.save()
            organization = Organization(owner=user)
            organization.save()
            messages.success(request, 'Welcome aboard. Let\'s pick a plan.', extra_tags='alert alert-success')
            send_mail(
                '[www] New user: %s!'%(user.username),
                'User: %s has signed up!'%(user.username),
                'sales@motpanel.com',
                ['sales@motpanel.com'],
                fail_silently=True,
            )
            if user is not None:
                auth.login(request, user)
            # redirect to a new URL:

            return HttpResponseRedirect(reverse('surveys-dashboard'))

    return render(request, 'sign_up_form.html', context)

def login_view(request):
    """View function for logging in."""
    #is user already logged in?
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.', extra_tags='alert alert-warning')
        return HttpResponseRedirect(request.GET.get('next', reverse('surveys-dashboard')))

    #If we receive POST data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = LoginForm(request.POST)
        context = {
            'submit_button_text': 'Login',
            'form': form,
            }
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            #print("username was: %s and password: " % username, password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                #print("user was not none")
                auth.login(request, user)
                #print("user is: %s" % request.user)
                #print("user is authenticated?: %s" % request.user.is_authenticated)
                messages.success(request, 'You have logged in.', extra_tags='alert alert-success')

                return HttpResponseRedirect(request.GET.get('next', '/'))
            else:
                #I don't see this happening, as my form validation should take care of this
                messages.error(request, "Username and password did not match, please try again.", extra_tags='alert alert-warning')
    else:
        #make context
        form = LoginForm
        context = {
            'submit_button_text': 'Login',
            'form': form,
            }
    return render(request, 'login_form.html', context)

def logout_view(request):
    """View function that logs userout and shows success message after logout."""
    auth.logout(request)
    messages.info(request, 'You have logged out successfully.', extra_tags='alert alert-info')
    return render(request, 'logout_complete.html')

@login_required
def edit_account_view(request):
    """View function for editing account"""
    if request.user.is_authenticated:
        form = EditAccountForm(initial={'username': request.user}, user=request.user)
        #If we receive POST data
        context = {
            'form': form,
            'submit_button_text': 'Update account details'
        }
        if request.method == 'POST':
            # Create a form instance and populate it with data from the request (binding):
            form = EditAccountForm(request.POST, user=request.user)
            context.update({'form': form})
            # Check if the form is valid:
            if form.is_valid():
                #print("form was valid")
                # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
                new_username = form.cleaned_data['username']
                request.user.username = new_username
                request.user.email = new_username
                request.user.save()
                messages.success(request, 'Your profile details was updated.', extra_tags='alert alert-success')

        return render(request, 'edit_account_form.html', context)
    #if user not authenticated
    else:
        #this should never occcur
        logger.warning("%s %s: %s tried to edit someone else's account"%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
        messages.error(request, "Can't edit profile when you are not logged in.", extra_tags='alert alert-danger')
        return HttpResponseRedirect(reverse('loginc'))


'''
@login_required
def your_plan_view(request):
    """View function for viewing and updating your plan"""
    s=Subscriber.objects.get(user__username=request.user.username)
    #print(s.update_plan_from_stripe_plan())
    if request.user.subscriber.status == 'inactive':
        messages.info(request, 'You haven\'t picked a plan yet.', extra_tags='alert alert-info')
        return HttpResponseRedirect(reverse('choose-plan'))
    else:

        context = {
            'plans': [request.user.subscriber.plan],
            'show_sales_arguments': False,
            'show_footer': True,
        }
        return render(request, 'current_plan.html', context)


def choose_plan_view(request):
    """View function for choosing a plan"""

    #print('The three plans are; %s, %s and %s.'%(smb_plan, stdrd_plan, ent_plan))
    plans = Plan.objects.filter(can_be_viewed=True).order_by('monthly_price')[:3]
    context = {
        'plans': plans,
        'show_sales_arguments': True,
        'show_footer': True,
    }

    return render(request, 'choose_plan.html', context)

@login_required
def cancel_plan_view(request):
    """View function for choosing a plan"""
    if request.method == 'POST':
        form = CancelPlanForm(request.POST)
        if form.is_valid():
            canceled_sub=""
            try:
                canceled_sub = stripe.Subscription.delete(request.user.subscriber.stripe_subscription_id)
            except:
                messages.error(request, 'While canceling your subscription we encountered an error. Probably your subscription was already cancelled. If your subscription remains active, and the problem persists, please contact us.', extra_tags='alert alert-warning')
            s=request.user.subscriber.sync_with_stripe_plan()
            try:
                if canceled_sub.status == 'canceled':
                    messages.success(request, 'Your plan was cancelled!', extra_tags='alert alert-success')
                else:
                    messages.error(request, 'Oh no! We tried to cancel your subscription with our payment provider, but was unable to. Please try again later, or drop us an email to let us know this happened, and we will get right on fixing it!', extra_tags='alert alert-warning')
            except:
                    messages.error(request, 'Oh no! We tried to cancel your subscription with our payment provider, but was unable to. Please try to log out and in, and then try again.Drop us an email to let us know if this keeps happening.', extra_tags='alert alert-warning')
            return HttpResponseRedirect(reverse('your-plan'))
        else:
            messages.error(request, 'Oh no! We were unable to verify that you confirmed to cancel. This is totally our fault. You can try again later, or contact us directly.', extra_tags='alert alert-warning')
            return HttpResponseRedirect(reverse('your-plan'))
    return render(request, 'cancel_plan_confirm.html')

@login_required
def change_plan_view(request):
    """View function for choosing a plan"""
    messages.error(request, 'We currently have no support for changing plans (as there is only one available plan). Check back later, or let us know that you are interested in a different plan by email or by clicking the link below the plan you are interested in!', extra_tags='alert alert-warning')
    return HttpResponseRedirect(reverse('choose-plan'))

@login_required
def show_interest_in_unavailable_plan(request):

    if request.method == 'POST':
        form = ChoosePlanForm(request.POST)
        if form.is_valid():
            interesting_plan_name = form.cleaned_data['chosen_plan']
            request.user.subscriber.flagged_interest_in_plan = interesting_plan_name
            request.user.subscriber.save()
            messages.success(request, 'Thanks. Your interest is duely noted! We will contact you once the plan becomes available.', extra_tags='alert alert-success')
            send_mail(
                '[www] Interest in unavailable plan from: %s'%(request.user.username),
                '%s has indicated that they are interested in an unavialble plan: %s.'%(request.user.username, interesting_plan_name),
                'sales@motpanel.com',
                ['sales@motpanel.com'],
                fail_silently=True,
            )
        else:
            messages.error(request, 'Oh no! That feature doesn\'t work right now, but please check back in later!', extra_tags='alert alert-warning')
    return HttpResponseRedirect(request.GET.get('next', reverse('choose-plan')))

@login_required
def set_up_subscription(request):

    if request.method != 'POST':
        messages.info(request, 'You must pick a plan before you can set up a subscription.', extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('choose-plan'))

    #logic to pick the plan
    form = ChoosePlanForm(request.POST)
    if form.is_valid():
        #print("ChoosePlanForm was valid")
        #print("trying to look up: %s"%(form.cleaned_data['chosen_plan']))
        chosen_plan = Plan.objects.get(name=form.cleaned_data['chosen_plan'])
        chosen_plan_id = chosen_plan.stripe_monthly_plan_id #only support monthly for now

    else:
        messages.error(request, 'Oh no! We are unable to recognize the plan you chose in our back-end. This is totally our fault! We\'d really appreciate you dropping us an email letting us know this happened!', extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('choose-plan'))

    #Make sure we have a Stripe Customer object to work with
    s=Subscriber.objects.get(user__username=request.user.username)
    s = s.sync_with_stripe_plan()
    if request.user.subscriber.stripe_id is not None:
        #This happens if users use the Update payment method or Restart buttons on plans.
        #This currently bills the customer and starts new subsc., regardless of the old.
        try:
            stripe_customer = stripe.Customer.retrieve(request.user.subscriber.stripe_id)
        except:
            messages.error(request, 'Oh no! We were unable to retrieve your customer data from our payment provider. If the problem persists, please contact us. ', extra_tags='alert alert-warning')
            return HttpResponseRedirect(reverse('choose-plan'))

    else:
        #user does not have a stripe customer id, and we should make one
        try:
            stripe_customer = stripe.Customer.create(
                description="Test Customer from set_up_subscription_view",
                email=request.user.email,
                #more fields here later
                )
            s.stripe_id=stripe_customer.id
            s.save()
            s = s.sync_with_stripe_plan()
        except:
            messages.error(request, 'Oh no! We were unable to connect with our payment provider. This usualy lasts very shortly. ', extra_tags='alert alert-warning')
            return HttpResponseRedirect(reverse('choose-plan'))
    #Make a session where customer object can create a subscription and payment method object on stripe webpage
    try:
        stripe_session = stripe.checkout.Session.create(
            customer=stripe_customer.id,
            payment_method_types=['card'],
            subscription_data={
                'items': [{
                'plan': chosen_plan_id,
                }],
              },
              success_url=request.build_absolute_uri(reverse('set-up-subscription-success'))+'?stripe_session_id={CHECKOUT_SESSION_ID}', #'http:127.0.0.1:8000/set-up-subscription-success/?stripe_session_id={CHECKOUT_SESSION_ID}', #
              cancel_url=request.build_absolute_uri(reverse('set-up-subscription-cancel'))#reverse('set-up-subscription-cancel') #'http:127.0.0.1:8000/set-up-subscription-cancel/',
            )
    except:
            messages.error(request, 'Oh no! We were unable to connect with our payment provider. This usually doesn\'t last very long. However, if the problem persists, please contact us. ', extra_tags='alert alert-warning')
            return HttpResponseRedirect(reverse('choose-plan'))

    messages.info(request, 'You have chosen the %s plan, with monthly billing.'%(chosen_plan.name), extra_tags='alert alert-info')
    messages.info(request, 'Use this credit card in testing: 4242424242424242', extra_tags='alert alert-info')

    context = {
        'stripe_session': stripe_session,
        'stripe_pk': stripe_pk,
        'plans': [chosen_plan],
        'show_sales_arguments': False,
        'show_footer': False,
    }

    return render(request, 'set_up_subscription.html', context) #should just redirect to stripe?

@login_required
def set_up_subscription_success(request):
    "a view for receiving success message from stripe"
    # GET stripes session-id and retrieve the session,
    stripe_session_id = request.GET['stripe_session_id']
    try:
        completed_stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)
    except:
        messages.error(request, 'Oh no! Your payment was successful, but then we were unable to connect to our payment provider to sync your settings on our side. Our people have been alerted, and will do it manually!', extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('your-plan'))
    # Update the Subscriber object with the proper plan
    s=Subscriber.objects.get(user__username=request.user.username)
    s.stripe_subscription_id = completed_stripe_session.subscription
    s.save()
    s = s.sync_with_stripe_plan()
    #print('in the view we have a Subscriber: %s, with a stripe_subscription_id: %s.name'%(s.user.username, s.stripe_subscription_id))
    #Check that the subscription is now active or trialing
    status = request.user.subscriber.status
    #print('in the view we call status and get: %s'%(status))
    if (status == 'active') or (status == 'trialing'): #Possible values are incomplete, trialing, active, expired, 'unable to charge'
        messages.success(request, 'You have succesfully set up a plan! The next step to get started is shown belown!', extra_tags='alert alert-success')
        return HttpResponseRedirect(reverse('surveys-dashboard'))
    else:
        messages.error(request, 'Oh no. This rarely (never?) happens. Our payment provider sent you to this page because you completed subscription setup, but when we check your subscription status, the status-message, which we expected to be "active" or "trialing" is "%s" instead. We\'ve alerted ourselves though, and are working to fix the problem asap.'%(status), extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('your-plan'))

@login_required
def set_up_subscription_cancel(request):
    "a view for receiving error message from stripe"

    messages.error(request, 'The subscription setup process was cancelled. Try again?', extra_tags='alert alert-danger')
    return HttpResponseRedirect(reverse('choose-plan'))
'''
