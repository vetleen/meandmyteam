from django.conf import settings
from surveys.models import Organization

#open connection to stripe
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_pk = settings.STRIPE_PUBLISHABLE_KEY
stripe_sk = settings.STRIPE_SECRET_KEY



##create Customer & save connection to User in db
def create_stripe_customer(organization):
    #Make sure an Organization was provided
    assert isinstance(organization, Organization)
    if organization.address_line_1 == '':
        raise ValueError('The %s has not provided an address line 1 in it\'s profile, but this is required by Stripe to do payments. Add a full address, and try again.'%(organization))
    #address should be a dictionary with the following keys:
        #line1 (required)
        #city (optional)
        #country (optional) (must be a two-letter country code, as per "https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2")
        #line2 (optional)
        #postal_code (optional)
        #state (optional) (may also be a country, province or region)

    address = {
        'line1': organization.address_line_1,
        'line2': organization.address_line_2,
        'postal_code': organization.zip_code ,
        'city': organization.city,
        #'country' : organization.country,
    }

    #Make sure there is a minimum of adress info provided
    try:

        s = stripe.Customer.create(
            address=address,
            description="%s"%(organization),
            email= organization.owner.email,
            shipping={
                'address': address,
                'name': organization.name,
                #'phone': None,
            }
        )
    except Exception as err:
        print('create_stripe_customer() returned an error: %s: %s.'%(type(err), err))
        return None
    return s

def retrieve_stripe_customer(stripe_customer_id):
    try:
        s = stripe.Customer.retrieve(stripe_customer_id)
        return s
    except Exception as err:
        print('retrieve_stripe_customer() returned an error: %s: %s.'%(type(err), err))
        return None

def delete_stripe_customer(stripe_customer_id):
    try:
        s = stripe.Customer.delete(stripe_customer_id)
        return s
    except Exception as err:
        print('delete_stripe_customer() returned an error: %s: %s.'%(type(err), err))
        return None

def create_stripe_payment_method(card, customer_id):
    #card must be a dictionary with the following keys:
    #card ={
    #     "number": "4242424242424242",
    #    "exp_month": 5,
    #    "exp_year": 2021,
    #    "cvc": "314",
    # }
    try:
        pm = stripe.PaymentMethod.create(
        type="card",
            card=card,
        )
        pm = stripe.PaymentMethod.attach(
            pm.id,
            customer=customer_id,
        )
        invoice_settings = {'default_payment_method': pm}
        c = stripe.Customer.modify(customer_id, invoice_settings=invoice_settings)

    except Exception as err:
        print('create_stripe_payment_method() returned an error: %s: %s.'%(type(err), err))
        return None
    return pm

def set_default_stripe_payment_method(customer_id, payment_method_id):
    try:
        pm = retrieve_stripe_payment_method(payment_method_id)
        invoice_settings = {'default_payment_method': pm}
        c = stripe.Customer.modify(customer_id, invoice_settings=invoice_settings)
    except Exception as err:
        print('create_stripe_payment_method() returned an error: %s: %s.'%(type(err), err))
        return None
    return pm

def retrieve_stripe_payment_method(payment_method_id):

    try:
        pm = stripe.PaymentMethod.retrieve(
            payment_method_id,
        )
    except Exception as err:
        print('retrieve_stripe_payment_method() returned an error: %s: %s.'%(type(err), err))
        return None
    return pm

def list_stripe_payment_methods(stripe_customer_id):
    try:
        pm_list = stripe.PaymentMethod.list(
            customer=stripe_customer_id,
            type="card",
        )
    except Exception as err:
        print(err)
        return None
    return pm_list

def delete_stripe_payment_method(stripe_payment_method_id):
    try:
        dpm = stripe.PaymentMethod.detach(
            stripe_payment_method_id,
        )
        return dpm
    except Exception as err:
        print('delete_stripe_payment_method() returned an error: %s: %s.'%(type(err), err))
        return None

def create_stripe_subscription(stripe_customer_id, price_id, trial_from_plan=True, quantity=0):
    try:
        s=stripe.Subscription.create(
            customer=stripe_customer_id,
            items=[{
              'price': price_id,
              'quantity': quantity,
            }],
            trial_from_plan=trial_from_plan
            )
        return s
    except Exception as err:
        print('create_stripe_subscription() returned an error: %s: %s.'%(type(err), err))
        return None

def delete_stripe_subscription(stripe_subscription_id):
    try:
        s=stripe.Subscription.delete(stripe_subscription_id)
        return s
    except Exception as err:
        print('delete_stripe_subscription() returned an error: %s: %s.'%(type(err), err))
        return None

def cancel_stripe_subscription(stripe_subscription_id):
    try:
        cs=stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )
        return cs
    except Exception as err:
        print('cancel_stripe_subscription() returned an error: %s: %s.'%(type(err), err))
        return None

def restart_cancelled_stripe_subscription(stripe_subscription_id):
    try:
        cs=stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=False
        )
        return cs
    except Exception as err:
        print('cancel_stripe_subscription() returned an error: %s: %s.'%(type(err), err))
        return None

def retrieve_stripe_subscription(stripe_subscription_id):
    try:
        s=stripe.Subscription.retrieve(stripe_subscription_id)
        return s
    except Exception as err:
        print('retrieve_stripe_subscription() returned an error: %s: %s.'%(type(err), err))
        return None

def modify_stripe_subscription(stripe_subscription_id, **kwargs):
    quantity = kwargs.get('quantity', None)

    try:
        s=stripe.Subscription.modify(
            stripe_subscription_id,
            quantity=quantity
        )
        return s
    except Exception as err:
        print('modify_stripe_subscription() returned an error: %s: %s.'%(type(err), err))
        return None

def list_stripe_products():
    try:
        #print('product:')
        #print(dir(stripe))
        ps=stripe.Product.list()
        return ps
    except Exception as err:
        print('list_stripe_products() returned an error: %s: %s.'%(type(err), err))
        return None

def retrieve_stripe_product(stripe_product_id):
    try:
        #print('price:')
        #print(dir(stripe))
        p = stripe.Product.retrieve(stripe_product_id)
        return p
    except Exception as err:
        print('retrieve_stripe_product() returned an error: %s: %s.'%(type(err), err))
        return None

def list_stripe_plans(stripe_product_id=None, active=True):
    try:
        ps=stripe.Plan.list(product=stripe_product_id, active=active)
        return ps
    except Exception as err:
        print('retrieve_stripe_plans() returned an error: %s: %s.'%(type(err), err))
        return None

def list_stripe_invoices(customer=None):
    try:
        ins = stripe.Invoice.list(customer=customer)
        return ins
    except Exception as err:
        print('retrieve_stripe_plans() returned an error: %s: %s.'%(type(err), err))
        return None
