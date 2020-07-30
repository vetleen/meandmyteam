from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from django.conf import settings

#my stuff


#third party
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
import datetime
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError

#set up logging
import logging
logger = logging.getLogger('__name__')

# Create your models here.
class Organization(models.Model):
    owner = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL, help_text='User who owns this Organization')
    name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the Organization')
    phone = PhoneNumberField(null=True, blank=True) #o.phone.as_e164
    address_line_1 = models.CharField(max_length=255, blank=True, null=True, help_text='Adress of the Organization')
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, help_text='Address contd.')
    zip_code =  models.CharField(max_length=255, blank=True, null=True, help_text='Zip code of the Organization')
    city =  models.CharField(max_length=255, blank=True, null=True, help_text='City where the Organization is located')
    country =  CountryField(blank=True, null=True, help_text='Country where the Organization is located')
    accepted_terms_and_conditions = models.BooleanField(default=False, help_text='Organization has accepted the terms and conditions and the privacy policy.')
    has_free_access = models.BooleanField(default=False, help_text='This organization should have free access.')
    subscription_paid_until = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='Organization has full access until')

    #stripe
    stripe_id = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='Subscribers Customer object ID in Stripe API')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='Subscribers Subscription object ID in Stripe API')
    stripe_subscription_quantity = models.PositiveSmallIntegerField(default=0, help_text='Current number of users/employees that are billed for', validators=[MinValueValidator(0), MaxValueValidator(2000000)])
    
    def save(self, *args, **kwargs):
        if self.phone:
            try:
                validate_international_phonenumber(self.phone)
            except ValidationError as err:
                raise ValidationError(
                    "Tried to create an organization with an invalid phone number (%(phone_number)s). Error message: %(error_message)s",
                    code='invalid',
                    params={'phone_number': self.phone, 'error_message': err.message}
                )
        super(Organization, self).save(*args, **kwargs)

    def update_stripe_subscription_quantity(self):
        respondents_list = self.respondent_set.all()
        self.stripe_subscription_quantity = len(respondents_list)
        self.save()
        return self.stripe_subscription_quantity
    
    def update_subscription_paid_until(self):
        ''' 
        Checks all possible sources of payments/free 
        trials etc. (currently either Stripe or free-access), 
        and sets the latest date as the 
        subscription_paid_until date.
        '''
        #make a list which will hold candidates for the new date
        candidates = []
        
        #check if there is an end date from stripe, append that to our canidates list
        if self.stripe_subscription_id is not None and self.stripe_subscription_id != '':
            stripe_subscription = None
            try:
                stripe_subscription=stripe.Subscription.retrieve(self.stripe_subscription_id)
            except Exception as err:
                logger.exception(\
                        "%s - %s - %s: Organization.update_subscription_paid_until(self): (user: %s) %s: %s."\
                        %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), __name__, 'EXCEPTION: ', self.owner, type(err), err))

            if stripe_subscription is not None:
                try:
                    date_from_stripe = datetime.datetime.fromtimestamp(stripe_subscription.current_period_end).date()
                    candidates.append(date_from_stripe)
                except Exception as err:
                    logger.exception(\
                        "%s - %s - %s: Organization.update_subscription_paid_until(self): (user: %s) %s: %s."\
                        %(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]'), __name__, 'EXCEPTION: ', self.owner, type(err), err))
        
        #check if we can make an end date for a free user (e.g. a tester), append that to our canidates list
        if self.has_free_access == True:
            date_from_free = datetime.date.today() + datetime.timedelta(days=30)
            candidates.append(date_from_free)

        #pick the latest of the candiDates
        new_date = None
        if len(candidates)>0:
            new_date = max(candidates)
        
        #update the paid_until date if needed
        if new_date is not None:
            if self.subscription_paid_until is None:
                self.subscription_paid_until = new_date
                self.save()
            elif new_date > self.subscription_paid_until:
                self.subscription_paid_until = new_date
                self.save()
        
        #return the subscription_paid_until date
        return self.subscription_paid_until

    def __str__(self):
        """String for representing the Organization object (in Admin site etc.)."""
        if self.name != None and self.name != '':
            return self.name
        else:
            return "Organization object owned by %s."%(self.owner)

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, help_text='')
    ALLOWED_CATEGORIES = [
        #anonymous user
        #'visited_privacy_policy',
        #'visited_terms_and_conditions',
        'visited_sign_up_view',

        #signed-up user
        'completed_sign_up', 
        'failed_sign_up', 
        'completed_log_in', 
        #'clicked_log_out', 
        'successfully_add_employee',
        'failed_to_add_employee',
        #'click_set_up_plan_from_dashboard', #in wizard
        'visited_pick_a_plan_first_time',
        'created_stripe_checkout_session', #picked a plan OR added another payment method
        #'clicked_set_up_payment_method', #continued on to stripe
        'successfully_set_up_payment_method', #returned successfully from stripe after setting up PM
        'failed_to_set_up_payment_method', #returned un-successfully from stripe after trying to set up PM
        'succesfully_set_up_subscription', #was able to create stripe subscription with provided payment method
        'failed_to_set_up_subscription', #was unable
        #'clicked_change_payment_method',
        #'clicked_cancel_subscription',
        'succesfully_cancel_subscription',
        'failed_to_cancel_subscription',
        'succesfully_restarted_subscription',
        'failed_to_restart_subscription',
        #'clicked_change_plan',
        #'clicked_dashboard_start_tracking_button',
        #'clicked_dashboard_OFF_button', #turns tracking ON
        #'clicked_dashboard_ON_button', #turns tracking OFF
        #'clicked_dashboard_add_employees_button',
        'started_tracking_with_an_instrument',
        'stopped_tracking_with_an_instrument',

        #respondent
        'opened_survey_instance_link',
        'failed_to_open_survey_instance_link',
        'accepted_terms_and_conditions',
        #'clicked_continue_button_on_answer_survey_view',
        'completed_survey_instance',
    ]
    category = models.CharField(
        max_length=255,
        help_text='What was the event?'
    )
    comment = models.TextField(blank=True, null=True, help_text='More info on event')
    time = models.DateTimeField(auto_now_add=True, editable=False, help_text='Time of event')

