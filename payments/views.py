from django.conf import settings

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden

from django.urls import reverse
from django.contrib import messages
from surveys.models import Employee
from payments.utils.stripe_logic import *


# Create your views here.
@login_required
def current_plan_view(request):
    """View function for ..."""

    #get the customer object id from DB
    stripe_id = request.user.subscriber.stripe_id
    #get the subscription object id from DB
    stripe_subscription_id = request.user.subscriber.stripe_subscription_id
    #get the customer object from Stripe
    stripe_customer = retrieve_stripe_customer(stripe_id)
    if stripe_customer == None:
        #Try make a customer
        stripe_customer = create_stripe_customer(request.user.organization)
        #if it wasnt made, error connecting to Stripe
        if stripe_customer == None:
            print('Unable to get a Customer object from Stripe for user %s.'%(request.user))
            return HttpResponseServerError()
        #if it WAS made, save it, so we can retrieve it later
        stripe_id = stripe_customer.id
        request.user.subscriber.stripe_id = stripe_id
        request.user.subscriber.save()

    #get the subscription object from Stripe, if there is a sub_id
    stripe_subscription = retrieve_stripe_subscription(stripe_subscription_id)
    if stripe_subscription_id is not None and stripe_subscription is None:
        print('Unable to get a Subscription object from Stripe for user %s.'%(request.user))
        return HttpResponseServerError()

    #get the default payment method if any, and asign to variable
    payment_method_id = stripe_customer.invoice_settings.default_payment_method
    default_payment_method = retrieve_stripe_payment_method(payment_method_id)

    #get a list of payment methods
    pm_list = list_stripe_payment_methods(stripe_id)

    print('default_payment_method: %s.'%(default_payment_method))
    print('pm_list: %s.'%(pm_list))
    context = {

        'stripe_subscription': stripe_subscription,
        'default_payment_method': default_payment_method,
        'pm_list': pm_list,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'current_plan.html', context=context)

@login_required
def set_up_payment_view(request):
    """View function for ..."""
    #get the customer object id from DB, if any
    stripe_id = request.user.subscriber.stripe_id
    #get the subscription object id from DB, if any
    stripe_subscription_id = request.user.subscriber.stripe_subscription_id

    #Make sure we have a customer object, either retrive or create:
    stripe_customer = retrieve_stripe_customer(stripe_id)
    if stripe_customer == None:
        #Make a customer
        stripe_customer = create_stripe_customer(request.user.organization)
        #If it wasnt made, error connecting to stripe
        if stripe_customer == None:
            print('Unable to get a Customer object from Stripe for user %s.'%(request.user))
            return HttpResponseServerError()
        #if it was made, save it in DB, so we can use it later
        stripe_id = stripe_customer.id
        request.user.subscriber.stripe_id = stripe_id
        request.user.subscriber.save()

    #Make sure we DON'T have a pre-existing subscription, another view handles that
    if stripe_subscription_id is not None and stripe_subscription_id is not '':
        stripe_subscription = retrieve_stripe_subscription(stripe_subscription_id)
        if stripe_subscription is None:
            print('Unable to get a Subscription object from Stripe for user %s.'%(request.user))
            return HttpResponseServerError()
        else:
            messages.error(request, 'You already have a subscription.', extra_tags='alert alert-warning')
            return HttpResponseRedirect(reverse('payments_current_plan'))


    #Now we know we have a stripe Customer object, and that we don't have a previous subscription. That means we can get to work:
    #Prepare a NEW PAYMENT-METHOD.-checkout-session if customer DON'T have a subscriptiion-id from before
    stripe_session=None
    if stripe_subscription_id is None or stripe_subscription_id == '':
        #Get the price to use
        #subsc_price = 'price_HLqVxG4RGJstNV' #for now only one price. PS. This is the test_price.

        #Get the number of co-workers to charge for:
        #quantity=4 #minimum number
        #elist = Employee.objects.filter(organization=request.user.organization)
        #print(len(elist))
        #if len(elist) > quantity:
        #    quantity = len(elist)

        #Create the session
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='setup',
            customer=stripe_customer,
            success_url=request.build_absolute_uri(reverse('payments-set-up-payment-method-success'))+'?stripe_session_id={CHECKOUT_SESSION_ID}', #'http:127.0.0.1:8000/set-up-subscription-success/?stripe_session_id={CHECKOUT_SESSION_ID}', #
            cancel_url=request.build_absolute_uri(reverse('payments-set-up-payment-method-cancel'))#reverse('set-up-subscription-cancel') #'http:127.0.0.1:8000/set-up-subscription-cancel/',
            )
        messages.info(request, 'Use this credit card in testing: 4242424242424242', extra_tags='alert alert-info')

    #initiate context variable to send to view
    context = {
        'stripe_session': stripe_session,
        'stripe_pk': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'set_up_payment_method.html', context=context)

@login_required
def set_up_payment_method_cancel(request):
    "a view for receiving error message from stripe"
    messages.error(request, 'The subscription setup process was cancelled. Try again?', extra_tags='alert alert-warning')
    return HttpResponseRedirect(reverse('payments-set-up-payment-method'))

@login_required
def set_up_payment_method_success(request):
    "a view for receiving success message from stripe"
    # GET stripes session-id and retrieve the session,
    stripe_session_id = request.GET['stripe_session_id']
    try:
        completed_stripe_session = stripe.checkout.Session.retrieve(stripe_session_id, expand=['setup_intent'])
    except:
        print('Boy, we need a logging system to catch these things!') #on todo-list
        messages.success(request, 'Looks like you were able to set up a payment method, but we were unable to get data from our payment provider just now. Don\'t worry though, this usualy resolves itself in a few hours, if not, we are notified and will fix it! It may mean that you have to manually pick this card as your "default payment method", but don\'t worry, we\'ll make it easy.', extra_tags='alert alert-success')
        return HttpResponseRedirect(reverse('payments_current_plan'))

    #get the new payment method, and set it to default
    #print('completed_stripe_session:')
    #print(completed_stripe_session)
    #print('completed_stripe_session.setup_intent.payment_method')
    #print(completed_stripe_session.setup_intent.payment_method)
    pm = completed_stripe_session.setup_intent.payment_method
    invoice_settings = {'default_payment_method': pm}
    c = stripe.Customer.modify(request.user.subscriber.stripe_id, invoice_settings=invoice_settings)

    #declare success and return to overview
    messages.success(request, 'Payment method set up successfully!', extra_tags='alert alert-success')
    return HttpResponseRedirect(reverse('payments_current_plan'))

    '''
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
    '''
@login_required
def use_payment_method_view(request, **kwargs):
    """View function for ..."""
    payment_method_id = kwargs.get('payment_method_id', None)
    try:
        stripe_id = request.user.subscriber.stripe_id
        stripe_customer = retrieve_stripe_customer(stripe_id)
        pm = retrieve_stripe_payment_method(payment_method_id)
        if stripe_id == pm.customer:
            dpm = set_default_stripe_payment_method(stripe_id, payment_method_id)
            if dpm is not None:
                messages.success(request, 'Your preferred payment method was updated!', extra_tags='alert alert-success')
            else:
                messages.warning(request, 'We tried to change your payment method, but it may not have work. Feel free to try again!', extra_tags='alert alert-warning')
        else:
            return HttpResponseForbidden()
    except Exception as err:
        print (type(err), ': ', err)
        return HttpResponseServerError()
    return HttpResponseRedirect(reverse('payments_current_plan'))

@login_required
def delete_payment_method_view(request, **kwargs):
    """View function for ..."""
    payment_method_id = kwargs.get('payment_method_id', None)
    try:
        stripe_user = retrieve_stripe_customer(request.user.subscriber.stripe_id)
        pm = retrieve_stripe_payment_method(payment_method_id)
        if stripe_user.id == pm.customer:
            dpm = delete_stripe_payment_method(payment_method_id)
            if dpm is not None:
                messages.success(request, 'The selected card was deleted!', extra_tags='alert alert-success')
            else:
                messages.warning(request, 'We tried to delete your card, but it may not have work. Feel free to try again!', extra_tags='alert alert-warning')
        else:
            return HttpResponseForbidden()
    except Exception as err:
        print (type(err), ': ', err)
        return HttpResponseServerError()
    return HttpResponseRedirect(reverse('payments_current_plan'))


#view current plan and payments etc. Later, invoices also.
#view to set up a subscription incl. adding payment method
#view to cancel a subscription
#view to modify subscription, incl. modifying payment method.
