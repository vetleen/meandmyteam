from django.conf import settings

from website.forms import ChangePasswordForm, SignUpForm, LoginForm, EditAccountForm, ChoosePlanForm, CancelPlanForm
from website.models import Subscriber, Plan
from django.views.generic.edit import CreateView, UpdateView, DeleteView #dont think this is needed anymore

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


import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_pk = settings.STRIPE_PUBLISHABLE_KEY
stripe_sk = settings.STRIPE_SECRET_KEY
#from catalog.models import ...

# Create your views here.
def index(request):
    """View function for home page of site."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard'))
    context = {
        'foo': 'bar',
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

@login_required
def dashboard_view(request):
    """View function for the dashboard"""
    messages.info(request, 'You have reached the dashboard.', extra_tags='alert alert-info')
    messages.success(request, 'Success!.', extra_tags='alert alert-success')
    messages.warning(request, 'the dashboard is under construction', extra_tags='alert alert-warning')
    context = {
        'foo': 'bar',
    }
    return render(request, 'dashboard.html', context)

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
            messages.success(request, 'Welcome aboard. Let\'s pick a plan.', extra_tags='alert alert-success')
            if user is not None:
                auth.login(request, user)
            # redirect to a new URL:

            return HttpResponseRedirect(reverse('choose-plan'))

    return render(request, 'sign_up_form.html', context)

def login_view(request):
    """View function for logging in."""
    #is user already logged in?
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.', extra_tags='alert alert-warning')
        return HttpResponseRedirect(request.GET.get('next', reverse('dashboard')))

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
                s = Subscriber.objects.get(user__username=request.user.username)
                s = s.sync_with_stripe_plan()
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
        messages.error(request, "Can't edit profile when you are not logged in.", extra_tags='alert alert-danger')
        return HttpResponseRedirect(reverse('loginc'))

@login_required
def your_plan_view(request):
    """View function for viewing and updating your plan"""
    s=Subscriber.objects.get(user__username=request.user.username)
    #print(s.update_plan_from_stripe_plan())
    if request.user.subscriber.status == 'inactive':
        messages.info(request, 'You haven\'t picked a plan yet.', extra_tags='alert alert-info')
        return HttpResponseRedirect(reverse('choose-plan'))
    else:
        illustrations = ['images/small-business-plan.svg']
        plans = [request.user.subscriber.plan]
        zipped_plans = zip(plans, illustrations)
        context = {
            'zipped_plans': zipped_plans,
            'show_sales_arguments': False,
            'show_footer': True,
        }
        return render(request, 'current_plan.html', context)


def choose_plan_view(request):
    """View function for choosing a plan"""

    #print('The three plans are; %s, %s and %s.'%(smb_plan, stdrd_plan, ent_plan))
    illustrations = ['images/small-business-plan.svg', 'images/standard-plan.svg', 'images/enterprise-plan.svg']
    plans = Plan.objects.filter(can_be_viewed=True).order_by('monthly_price')[:3]
    zipped_plans = zip(plans, illustrations)
    context = {
        'zipped_plans': zipped_plans,
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
            cancelled_sub = stripe.Subscription.delete(request.user.subscriber.stripe_subscription_id)
            if cancelled_sub.status == 'canceled':
                messages.success(request, 'Your plan was cancelled!', extra_tags='alert alert-success')
            else:
                messages.error(request, 'Oh no! We tried to cancel your subscription with our payment provider, but was unable to. Please try again later, or drop us an email to let us know this happened, and we will get right on fixing it!', extra_tags='alert alert-warning')
            s = request.user.subscriber.sync_with_stripe_plan()
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
    ''' a view for marking a subscriber as interested in an unavailable plan '''
    if request.method == 'POST':
        form = ChoosePlanForm(request.POST)
        if form.is_valid():
            interesting_plan_name = form.cleaned_data['chosen_plan']
            request.user.subscriber.flagged_interest_in_plan = interesting_plan_name
            request.user.subscriber.save()
            messages.success(request, 'Thanks. Your interest is duely noted! We will contact you once the plan becomes available.', extra_tags='alert alert-success')
        else:
            messages.error(request, 'Oh no! That feature doesn\'t work right now, but please check back in later!', extra_tags='alert alert-warning')
    return HttpResponseRedirect(request.GET.get('next', reverse('choose-plan')))

@login_required
def set_up_subscription(request):
    ''' a view for confirming subscriber-intent, and sending new subscribers to Stripe '''

    if request.method != 'POST':
        messages.info(request, 'You must pick a plan before you can set up a subscription.', extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('choose-plan'))

    #logic to pick the plan
    form = ChoosePlanForm(request.POST)
    if form.is_valid():
        print("ChoosePlanForm was valid")
        print("trying to look up: %s"%(form.cleaned_data['chosen_plan']))
        chosen_plan = Plan.objects.get(name=form.cleaned_data['chosen_plan'])
        chosen_plan_id = chosen_plan.stripe_plan_id

    else:
        messages.error(request, 'Oh no! We are unable to recognize the plan you chose in our back-end. This is totally our fault! We\'d really appreciate you dropping us an email letting us know this happened!', extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('choose-plan'))

    #Make sure we have a Stripe Customer object to work with
    s=Subscriber.objects.get(user__username=request.user.username)
    s = s.sync_with_stripe_plan()
    if request.user.subscriber.stripe_id is not None:
        #This happens if users use the Update payment method or Restart buttons on plans.
        #This currently bills the customer and starts new subsc., regardless of the old.
        stripe_customer = stripe.Customer.retrieve(request.user.subscriber.stripe_id)
    else:
        #user does not have a stripe customer id, and we should make one
        stripe_customer = stripe.Customer.create(
            description="Test Customer from set_up_subscription_view",
            email=request.user.email,
            #more fields here later
            )
        s.stripe_id=stripe_customer.id
        s.save()
        s = s.sync_with_stripe_plan()
    #Make a session where customer object can create a subscription and payment method object on stripe webpage
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
    illustration = 'images/small-business-plan.svg'
    zipped_plans = {(chosen_plan, illustration)}

    messages.info(request, 'You have chosen the %s plan, with monthly billing.'%(chosen_plan.name), extra_tags='alert alert-info')
    messages.info(request, 'Use this credit card in testing: 4242424242424242', extra_tags='alert alert-info')

    context = {
        'stripe_session': stripe_session,
        'stripe_pk': stripe_pk,
        'zipped_plans': zipped_plans,
        'show_sales_arguments': False,
        'show_footer': False,
    }

    return render(request, 'set_up_subscription.html', context) #should just redirect to stripe?

@login_required
def set_up_subscription_success(request):
    ''' a view for receiving success message from stripe '''
    # GET stripes session-id and retrieve the session,
    stripe_session_id = request.GET['stripe_session_id']
    completed_stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)

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
        messages.success(request, 'You have succesfully set up a plan! Now, go check out your dashboard!', extra_tags='alert alert-success')
        return HttpResponseRedirect(reverse('your-plan'))
    else:
        messages.error(request, 'Oh no. This rarely (never?) happens. Our payment provider sent you to this page because you completed subscription setup, but when we check your subscription status, the status-message, which we expected to be "active" or "trialing" is "%s" instead.'%(status), extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('your-plan'))

@login_required
def set_up_subscription_cancel(request):
    ''' a view for receiving error message from stripe '''

    messages.error(request, 'The subscription setup process was cancelled. Try again?', extra_tags='alert alert-danger')
    return HttpResponseRedirect(reverse('choose-plan'))
