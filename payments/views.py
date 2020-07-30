from django.conf import settings

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden

from django.urls import reverse
from django.contrib import messages

#
from website.models import Event

#
from payments.tools.stripe_logic import *
from operator import itemgetter
import datetime

#set up logging
import logging
logger = logging.getLogger('__name__')

# Create your views here.
@login_required
def current_plan_view(request):
    """View function for ..."""

    ## what do we know about this user?
    #get the customer object id from DB
    stripe_id = request.user.organization.stripe_id
    #get the subscription object id from DB
    stripe_subscription_id = request.user.organization.stripe_subscription_id

    #get the customer object from Stripe, if any, or make one
    stripe_customer = None
    if stripe_id is not None and stripe_id != '':
        stripe_customer = retrieve_stripe_customer(stripe_id)
    if stripe_customer == None:
        #mark an event - someone visited for the first time
        event = Event(category='visited_pick_a_plan_first_time', user=request.user, comment=None)
        event.save()        
        #Try make a customer
        stripe_customer = create_stripe_customer(request.user.organization)
        #if it wasnt made, error connecting to Stripe
        if stripe_customer == None:
            logger.warning("%s %s: current_plan_view: Unable to get a Customer object from Stripe for user %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
            return HttpResponseServerError()
        #if it WAS made, save it, so we can retrieve it later
        stripe_id = stripe_customer.id
        request.user.organization.stripe_id = stripe_id
        request.user.organization.save()

    ##SUBSCRIPTION
    #if there is a sub_id, get the subscription object from Stripe,
    stripe_subscription = None
    if stripe_subscription_id is not None and stripe_subscription_id != '':
        #UPDATE QUANTITY HERE? -> No, this should be handled in the add/delete employee views now
        stripe_subscription = retrieve_stripe_subscription(stripe_subscription_id)
    if stripe_subscription_id is not None and stripe_subscription is None:
        logger.warning("%s %s: current_plan_view: Unable to get a Subscription object from Stripe for user %s, and sub_id %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user, stripe_subscription_id))
        return HttpResponseServerError()

    #clean it up for the template:
    clean_stripe_subscription = None
    if stripe_subscription is not None:
        clean_stripe_subscription = {}
        clean_stripe_subscription = {
            'id': stripe_subscription.id,
            'cancel_at_period_end': stripe_subscription.cancel_at_period_end,
            'latest_invoice': stripe_subscription.latest_invoice,
            'plan_active': stripe_subscription.plan.active,
            'plan_interval_amount': "%.0f" % int(stripe_subscription.plan.amount/stripe_subscription.plan.interval_count/100),
            'plan_total': "%.0f" % int(stripe_subscription.plan.amount/stripe_subscription.plan.interval_count*stripe_subscription.quantity/100),
            'plan_currency': stripe_subscription.plan.currency,
            'plan_id': stripe_subscription.plan.id,
            'plan_interval': stripe_subscription.plan.interval,
            'plan_name': stripe_subscription.plan.nickname,
            'quantity': stripe_subscription.quantity,
            'status': stripe_subscription.status,
            'current_period_start': datetime.datetime.fromtimestamp(stripe_subscription.current_period_start).date(),
            'current_period_end': datetime.datetime.fromtimestamp(stripe_subscription.current_period_end).date(),
            'billing_cycle_anchor': datetime.datetime.fromtimestamp(stripe_subscription.billing_cycle_anchor).date(),
        }

    ##PAYMENT METHOD
    #get the default payment method if any, and assign to variable
    payment_method_id = stripe_customer.invoice_settings.default_payment_method
    default_payment_method = None
    if payment_method_id != None:
        default_payment_method = retrieve_stripe_payment_method(payment_method_id)

    #get a list of payment methods
    pm_list = list_stripe_payment_methods(stripe_id)

    ##PLANS
    #get a list of the product and all of its plans:
    product = retrieve_stripe_product('prod_HLqVCyWrjJFx6v') #test-product, must be changed for production, and preferably got through some more elegant meansd
    plan_list = list_stripe_plans(product.id)

    #Clean it up for display
    clean_plan_list = []
    for plan in plan_list:
        if plan.product == product.id and plan.active == True:

            #clean data and dict for each plan
            cleaned_plan = {
                'name': plan.nickname,
                'currency': plan.currency,
                'id': plan.id,
                'interval': plan.interval,
                'interval_count': plan.interval_count,
                'trial_period_days': plan.trial_period_days,
                'amount': "%.0f" % int(plan.amount/100),
                'interval_amount': "%.0f" % int(plan.amount/plan.interval_count/100),
                'tiers': [] #make room for tiers, which will be appended later
            }
            clean_plan_list.append(cleaned_plan)
    clean_plan_list2 = sorted(clean_plan_list, key=itemgetter('amount'), reverse=True)

    ##INVOICES
    #List of invoices
    invoice_list = list_stripe_invoices(customer=stripe_id)

    #Clean them up for display
    clean_invoice_list = None
    if invoice_list is not None and len(invoice_list) > 0:
        clean_invoice_list = []
        for invoice in invoice_list:
            cleaned_invoice = {
             'number': invoice.number,
             'created': datetime.datetime.fromtimestamp(invoice.created).date(),
             'paid': invoice.paid,
             'invoice_pdf': invoice.invoice_pdf,
             'line_items': [],
            }
            #add info from line items:
            for item in invoice.lines:

                clean_line={
                    'amount': "%.0f" % item.amount,
                    'currency': item.currency,
                    'period_start': datetime.datetime.fromtimestamp(item.period.start).date(),
                    'period_end': datetime.datetime.fromtimestamp(item.period.end).date(),
                    'plan_name': item.plan.nickname,

                }
                cleaned_invoice['line_items'].append(clean_line)
            clean_invoice_list.append(cleaned_invoice)

    context = {

        'stripe_subscription': clean_stripe_subscription,
        'default_payment_method': default_payment_method,
        'pm_list': pm_list,
        'product': product,
        'plan_list': clean_plan_list2,
        'invoice_list': clean_invoice_list,
        #'clean_product_list': clean_product_list,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'current_plan.html', context=context)

@login_required
def set_up_payment_view(request):
    """View function for ..."""
    #mark an event - someone clicked pick a plan or add payment method - who knows which?
    event = Event(category='created_stripe_checkout_session', user=request.user, comment=None)
    event.save()

    #get the customer object id from DB, if any
    stripe_id = request.user.organization.stripe_id
    #get the subscription object id from DB, if any
    stripe_subscription_id = request.user.organization.stripe_subscription_id

    #Make sure we have a customer object, either retrive or create:
    stripe_customer = retrieve_stripe_customer(stripe_id)
    if stripe_customer == None:
        #Make a customer
        stripe_customer = create_stripe_customer(request.user.organization)
        #If it wasnt made, error connecting to stripe
        if stripe_customer == None:
            print('Unable to get a Customer object from Stripe for user %s.'%(request.user))
            logger.warning("%s %s: set_up_payment_view: Unable to get a Customer object from Stripe for user %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
            return HttpResponseServerError()
        #if it was made, save it in DB, so we can use it later
        stripe_id = stripe_customer.id
        request.user.organization.stripe_id = stripe_id
        request.user.organization.save()

    #catch cases where we have subscription id, but are not able to get the Subscriber object from stripe
    if stripe_subscription_id is not None and stripe_subscription_id is not '':
        stripe_subscription = retrieve_stripe_subscription(stripe_subscription_id)
        if stripe_subscription is None:
            print('Unable to retrieve a Subscription object from Stripe for user %s, with stripe ID %s.'%(request.user, stripe_id))
            logger.warning("%s %s: set_up_payment_view: Unable to retrieve a Subscription object from Stripe for user %s, with stripe ID %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user, stripe_id))
            return HttpResponseServerError()

    #Now we know we have a stripe Customer object: That means we can get to work:
    #Prepare a NEW PAYMENT-METHOD.-checkout-session

    #make the success URL:
    success_url = request.build_absolute_uri(reverse('payments-set-up-payment-method-success'))+'?stripe_session_id={CHECKOUT_SESSION_ID}'
    next_url = request.GET.get('next', None)
    if next_url is not None:
        success_url = success_url+'&next='+next_url #This is used if we also should set up a subscription

    #make session
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='setup',
        customer=stripe_customer,
        success_url=success_url,
        cancel_url=request.build_absolute_uri(reverse('payments-set-up-payment-method-cancel'))
        )
    messages.info(request, 'Use this credit card in testing: Visa: 4242 4242 4242 4242', extra_tags='alert alert-info')
    messages.info(request, 'Use this credit card in testing: American Express: 3782 822463 10005', extra_tags='alert alert-info')
    messages.info(request, 'Use this credit card in testing: Mastercard: 5555 5555 5555 4444', extra_tags='alert alert-info')

    #initiate context variable to send to view
    context = {
        'stripe_session': stripe_session,
        'stripe_pk': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'set_up_payment_method.html', context=context)

@login_required
def set_up_payment_method_cancel(request):
    "a view for receiving error message from stripe"
    #mark an event 
    event = Event(category='failed_to_set_up_payment_method', user=request.user, comment=None)
    event.save()

    #do things
    messages.error(request, 'The subscription setup process was cancelled. Try again?', extra_tags='alert alert-warning')
    logger.warning("%s %s: set_up_payment_method_cancel: Stripe returned a failed payment attempt for user %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
    return HttpResponseRedirect(reverse('payments-set-up-payment-method'))

@login_required
def set_up_payment_method_success(request):
    "a view for receiving success message from stripe"
    #mark an event 
    event = Event(category='successfully_set_up_payment_method', user=request.user, comment=None)
    event.save()

    # GET stripes session-id and retrieve the session,
    stripe_session_id = request.GET['stripe_session_id']
    try:
        completed_stripe_session = stripe.checkout.Session.retrieve(stripe_session_id, expand=['setup_intent'])
    except:
        logger.error("%s %s: set_up_payment_method_success: Stripe returned a successful payment attempt for user %s, but we were unable to retrieve the stripe session. We should set default payment method manually, and check that everything is in order!"%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'ERROR: ', request.user))
        messages.success(request, 'Looks like you were able to set up a payment method, but we were unable to get data from our payment provider just now. Don\'t worry though, our support staff have been notified and will fix it!', extra_tags='alert alert-success')
        return HttpResponseRedirect(reverse('payments_current_plan'))

    #get the new payment method, and set it to default
    pm = completed_stripe_session.setup_intent.payment_method
    invoice_settings = {'default_payment_method': pm}
    c = stripe.Customer.modify(request.user.organization.stripe_id, invoice_settings=invoice_settings)

    #declare success and return to overview
    messages.success(request, 'Payment method set up successfully!', extra_tags='alert alert-success')
    return HttpResponseRedirect(request.GET.get('next', reverse('payments_current_plan')))

@login_required
def use_payment_method_view(request, **kwargs):
    """View function for ..."""
    payment_method_id = kwargs.get('payment_method_id', None)
    try:
        stripe_id = request.user.organization.stripe_id
        stripe_customer = retrieve_stripe_customer(stripe_id)
        pm = retrieve_stripe_payment_method(payment_method_id)
        if stripe_id == pm.customer:
            dpm = set_default_stripe_payment_method(stripe_id, payment_method_id)
            if dpm is not None:
                messages.success(request, 'Your preferred payment method was updated!', extra_tags='alert alert-success')
            else:
                messages.warning(request, 'We tried to change your payment method, but it may not have work. Feel free to try again!', extra_tags='alert alert-warning')
                logger.warning("%s %s: use_payment_method_view: Tried to change payment method for user %s, but was unsuccessful."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
        else:
            return HttpResponseForbidden()
    except Exception as err:
        logger.exception("%s %s: use_payment_method_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user, type(err), err))
        return HttpResponseServerError()
    return HttpResponseRedirect(reverse('payments_current_plan'))

@login_required
def delete_payment_method_view(request, **kwargs):
    """View function for ..."""
    payment_method_id = kwargs.get('payment_method_id', None)
    try:
        stripe_user = retrieve_stripe_customer(request.user.organization.stripe_id)
        pm = retrieve_stripe_payment_method(payment_method_id)
        if stripe_user.id == pm.customer:
            dpm = delete_stripe_payment_method(payment_method_id)
            if dpm is not None:
                messages.success(request, 'The selected card was deleted!', extra_tags='alert alert-success')
            else:
                logger.warning("%s %s: delete_payment_method_view: Tried to delete payment method for user %s, but was unsuccessful."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
                messages.warning(request, 'We tried to delete your card, but it may not have work. Feel free to try again!', extra_tags='alert alert-warning')
        else:
            return HttpResponseForbidden()
    except Exception as err:
        logger.exception("%s %s: delete_payment_method_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        return HttpResponseServerError()
    return HttpResponseRedirect(reverse('payments_current_plan'))
    #return HttpResponseRedirect(request.GET.get('next', reverse('surveys-dashboard')))

@login_required
def create_subscription_view(request, **kwargs):
    """View function for ..."""
    #grab the desired sub ID from the url
    subscription_id = kwargs.get('subscription_id', None)

    #get the default payment method if any, and assign to variable
    stripe_customer = retrieve_stripe_customer(request.user.organization.stripe_id)
    if stripe_customer == None:
        logger.error("%s %s: create_subscription_view: Tried to retrieve stripe Subscriber object for user %s, with ID %s, but was unsuccessful."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'ERROR: ', request.user, request.user.organization.stripe_id))
        return HttpResponseServerError()

    payment_method_id = stripe_customer.invoice_settings.default_payment_method
    default_payment_method = None
    if payment_method_id != None and payment_method_id != '':
        default_payment_method = retrieve_stripe_payment_method(payment_method_id)
    if default_payment_method == None:
        #redirect to set up PM before coming back here...
        return HttpResponseRedirect(reverse('payments-set-up-payment-method')+'?next='+reverse('payments-create-subscription', args=[subscription_id]))

    try:
        #Update and retrieve the number of co-workers to charge
        quantity=request.user.organization.update_stripe_subscription_quantity()

        #get the Customer object ID
        stripe_id = request.user.organization.stripe_id

        #create subscription with stripe
        s = create_stripe_subscription(stripe_id, subscription_id, trial_from_plan=True, quantity=quantity)
        request.user.organization.stripe_subscription_id=s.id
        request.user.organization.save()
        #check if succeeded
        if s is not None:
            #declare success
            messages.success(request, 'Your subscription was started!', extra_tags='alert alert-success')
            #update payment status
            request.user.organization.update_subscription_paid_until()
            #mark an event 
            event = Event(category='succesfully_set_up_subscription', user=request.user, comment=None)
            event.save()
        else:
            #log failure
            logger.warning("%s %s: create_subscription_view: Tried to start subscription for user %s, but was unsuccessful."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
            messages.warning(request, 'We tried to start your subscription, but something went wrong. You can try again, and we\'ll make sure you don\'t get charged twice!', extra_tags='alert alert-warning')
            #mark an event 
            event = Event(category='failed_to_set_up_subscription', user=request.user, comment=None)
            event.save()

    except Exception as err:
        logger.exception("%s %s: create_subscription_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        return HttpResponseServerError()

    return HttpResponseRedirect(reverse('payments_current_plan'))

@login_required
def cancel_subscription_view(request, **kwargs):
    """View function for ..."""
    subscription_id = kwargs.get('subscription_id', None)
    try:
        if subscription_id == request.user.organization.stripe_subscription_id:
            cs = cancel_stripe_subscription(subscription_id)
            if cs is not None:
                messages.success(request, 'Your subscription was cancelled, it will not renew next billing cycle.', extra_tags='alert alert-success')
                #update payment status
                request.user.organization.update_subscription_paid_until()
                #mark an event 
                event = Event(category='succesfully_cancel_subscription', user=request.user, comment=None)
                event.save()
            else:
                logger.warning("%s %s: cancel_subscription_view: Tried to cancel subscription for user %s, but was unsuccessful."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
                messages.warning(request, 'We tried to cancel your subscription, but it may not have work.Try again later, or contact support.', extra_tags='alert alert-warning')
                #mark an event 
                event = Event(category='failed_to_cancel_subscription', user=request.user, comment=None)
                event.save()
        else:
            return HttpResponseForbidden()
    except Exception as err:
        logger.exception("%s %s: cancel_subscription_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        return HttpResponseServerError()
    return HttpResponseRedirect(reverse('payments_current_plan'))

@login_required
def restart_cancelled_subscription_view(request, **kwargs):
    """View function for ..."""
    subscription_id = kwargs.get('subscription_id', None)
    try:
        if subscription_id == request.user.organization.stripe_subscription_id:
            rs = restart_cancelled_stripe_subscription(subscription_id)
            if rs is not None:
                messages.success(request, 'Your subscription was restarted!', extra_tags='alert alert-success')
                #update payment status
                request.user.organization.update_subscription_paid_until()
                #mark an event 
                event = Event(category='succesfully_restarted_subscription', user=request.user, comment=None)
                event.save()
            else:
                logger.warning("%s %s: restart_cancelled_subscription_view: Tried to restart subscription for user %s, but was unsuccessful."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
                messages.warning(request, 'We tried to restart your subscription, but it may not have worked. Try again later, or contact support.', extra_tags='alert alert-warning')
                #mark an event 
                event = Event(category='failed_to_restart_subscription', user=request.user, comment=None)
                event.save()
        else:
            return HttpResponseForbidden()
    except Exception as err:
        logger.exception("%s %s: restart_cancelled_subscription_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        return HttpResponseServerError()
    return HttpResponseRedirect(reverse('payments_current_plan'))

@login_required
def change_subscription_price_view(request, **kwargs):
    """View function for ..."""
    price_id = kwargs.get('price_id', None)
    try:
        s = change_stripe_subscription_price(request.user.organization.stripe_subscription_id, price_id, quantity=request.user.organization.update_stripe_subscription_quantity())
        if s is not None:
            messages.success(request, 'Your subscription was updated with the chosen plan!', extra_tags='alert alert-success')
            #update payment status
            request.user.organization.update_subscription_paid_until()
        else:
            logger.warning("%s %s: change_subscription_price_view: Tried to changet subscription Price for user %s, but was unsuccessful."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'WARNING: ', request.user))
            messages.warning(request, 'We tried to update your subscription, but it may not have worked. Try again later, or contact support.', extra_tags='alert alert-warning')
    except Exception as err:
        logger.exception("%s %s: change_subscription_price_view: (user: %s) %s: %s."%(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), 'EXCEPTION: ', request.user, type(err), err))
        return HttpResponseServerError()
    return HttpResponseRedirect(reverse('payments_current_plan'))
