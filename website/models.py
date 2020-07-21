from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from django.conf import settings

#third party
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
import datetime
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError

# Create your models here.
class Organization(models.Model):
    owner = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL, help_text='User who owns this Organization')
    name = models.CharField(max_length=255, blank=True, null=True, help_text='Name of the Organization')
    phone = PhoneNumberField(null=True, blank=True, unique=True) #o.phone.as_e164
    address_line_1 = models.CharField(max_length=255, blank=True, null=True, help_text='Adress of the Organization')
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, help_text='Address contd.')
    zip_code =  models.CharField(max_length=255, blank=True, null=True, help_text='Zip code of the Organization')
    city =  models.CharField(max_length=255, blank=True, null=True, help_text='City where the Organization is located')
    country =  CountryField(blank=True, null=True, help_text='Country where the Organization is located')
    accepted_terms_and_conditions = models.BooleanField(default=False, help_text='Organization has accepted the terms and conditions and the privacy policy.')

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

    def __str__(self):
        """String for representing the Organization object (in Admin site etc.)."""
        if self.name != None and self.name != '':
            return self.name
        else:
            return "Organization object owned by %s."%(self.owner)
