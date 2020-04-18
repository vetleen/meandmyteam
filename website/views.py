from django.shortcuts import render

from website.forms import ChangePasswordForm, SignUpForm, LoginForm, EditAccountForm
from website.models import Subscriber, Plan
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from django.urls import reverse
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login, authenticate
from django.contrib import auth

from django.contrib import messages
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
            messages.success(request, 'Welcome aboard. This is your dashboard, where you can....', extra_tags='alert alert-success')
            if user is not None:
                auth.login(request, user)
            # redirect to a new URL:

            return HttpResponseRedirect(reverse('dashboard'))

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
                return HttpResponseRedirect(request.GET.get('next', '/'))
            else:
                #i don't see this happening, as my form validation should take care of this
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
    if request.user.subscriber.status() == 'inactive':
        messages.info(request, 'You haven\'t picked a plan yet.', extra_tags='alert alert-info')
        return HttpResponseRedirect(reverse('choose-plan'))
    else:
        illustrations = ['images/small-business-plan.svg']
        plans = [request.user.subscriber.plan]
        zipped_plans = zip(plans, illustrations)
        context = {
            'zipped_plans': zipped_plans,
            'show_sales_arguments': False,
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
    }
    #if user is anonymous
    ## -> SHow plans with buttons that lead to sign up (we'll add some memory later)

    #if user is authenitcated

    #if user already has a plan
    ## -> SHow active plan differently, buttons should read "change to"

    #if user doesn't have a plan
    ## -> Show plans, buttons say "Pick plan"

    return render(request, 'choose_plan.html', context)
