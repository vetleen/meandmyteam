from django.conf import settings
from surveys.models import Organization

#open connection to stripe
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_pk = settings.STRIPE_PUBLISHABLE_KEY
stripe_sk = settings.STRIPE_SECRET_KEY

## stripe things:
#create Customer
#create PaymentMethod and save to Customer
#create Subscription for a Customer and attach PaymentMethod
#cancel Subscription
#change Subscription



##create Customer & save connection to User in db
def create_stripe_customer(organization):
    #Make sure an Organization was provided
    assert isinstance(organization, Organization)
    if organization.address_line_1 == '':
        raise ValueError('The provided organization has not provided an address line 1 in it\'s profile, but this is required by stripe to do payments. Add a full address, and try again.')
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
            description="My Test Customer - make a better description thingy later",
            email= organization.owner.email,
            shipping={
                'address': address,
                'name': organization.name,
                #'phone': None,
            }
        )
    except Exception as err:
        print(err)
        return None
    return s

def retrieve_stripe_customer(stripe_customer_id):
    try:
        s = stripe.Customer.retrieve(stripe_customer_id)
        return s
    except Exception as err:
        print(err)
        return None

def delete_stripe_customer(stripe_customer_id):
    try:
        s = stripe.Customer.delete(stripe_customer_id)
        return s
    except Exception as err:
        print (err)
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
        print(err)
        return None
    return pm

def create_stripe_subscription(stripe_customer_id, price_id="price_HLqVxG4RGJstNV", trial_from_plan=True, quantity=0):
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
        print(err)
        return None

def delete_stripe_subscription(stripe_subscription_id):
    try:
        s=stripe.Subscription.delete(stripe_subscription_id)
        return s
    except Exception as err:
        print(err)
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
        print(err)
        return None
