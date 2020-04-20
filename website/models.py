from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
import datetime
from django.utils import timezone

# Create your models here.

class SalesArgument(models.Model):
    """Model representing the sales arguments Plans can have."""
    argument = models.CharField(max_length=255, help_text='What is the argument?')
    priority = models.PositiveSmallIntegerField(default=0,  help_text='Set a priority (0-100):', validators=[MinValueValidator(0), MaxValueValidator(100)])

    BADGE_TYPE_CHOICES = (
        ('No set', None),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('danger', 'Danger'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('light', 'Light'),
        ('dark', 'Dark'),
            )

    badge_type = models.CharField(
        max_length=30,
        choices=BADGE_TYPE_CHOICES,
        blank=True,
        default=None,
        help_text='Should a badge accompany the argument?',
    )
    badge_text = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='What should the badge (if any) say?')
    is_active = models.BooleanField(default=True, help_text='Is this argument active (supposed to be visible)?')

    def __str__(self):
        """String for representing the Model object."""
        return self.argument

class Plan(models.Model):
    """The plans Subscribers can choose from."""

    # Fields
    name = models.CharField(max_length=60, help_text='Name of the plan')
    description = models.CharField(max_length=255, help_text='A short description of the plan')
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Montly price')
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Yearly price')
    show_price = models.BooleanField(default=True, help_text='Should the price be displayed?')
    included_employees = models.PositiveSmallIntegerField(default=10,  help_text='The number of employees that are included', validators=[MinValueValidator(0), MaxValueValidator(2000000)])
    can_be_picked = models.BooleanField(default=True, help_text='This plan should be available to pick for visitors')
    can_be_viewed = models.BooleanField(default=True, help_text='This plan should be visible to visitors')
    # illustration
    IS_PAID = (
        ('n', 'No'),
        ('y', 'Yes'),
            )

    is_paid = models.CharField(
        max_length=1,
        choices=IS_PAID,
        blank=False,
        default='n',
        help_text='Is the plan a paid plan?',
    )
    sales_argument = models.ManyToManyField(SalesArgument, blank=True, help_text='Select sales arguments for this plan')

    ##Stripe integration
    stripe_plan_id = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='This Plans Plan-object ID in Stripe API, format should be "plan_H7nTHThryy8L62".')

    def __str__(self):
        """String for representing the Plan object (in Admin site etc.)."""
        return self.name

class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, blank=True, null=True)
    date_current_plan_expires = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='The date the current strupe subscription ends')
    status = models.CharField(max_length=35, blank=True, null=True, default=None, help_text='The subscrition status of the Subscriber')
    date_last_synced_with_stripe = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, help_text='The date this object was synced with Stripe')
    flagged_interest_in_plan = models.CharField(max_length=60, blank=True, null=True, help_text='Subscriber is interested in this plan')

    #stripe
    stripe_id = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='Subscribers Customer object ID in Stripe API')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True, default=None, help_text='Subscribers Subscription object ID in Stripe API')

    def sync_with_stripe_plan(self):
        if self.stripe_subscription_id is None:
            #avoid errors caused by tryiong to retrieve a stripe-subscription that's not there.
            return self
        stripe_subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)

        #Update the plan
        plan_to_set = Plan.objects.get(stripe_plan_id=stripe_subscription.plan.id)
        self.plan = plan_to_set

        #Update the plans expiery date
        self.date_current_plan_expires = datetime.datetime.fromtimestamp(stripe_subscription.current_period_end).date()

        #Update status of the Subscriber
        if stripe_subscription.status == 'active':
            val_to_set = 'active'
        if stripe_subscription.status == 'trialing':
            val_to_set =  'trialing'
        if stripe_subscription.status == 'canceled':
            val_to_set =  'canceled'
        if stripe_subscription.status == 'unpaid':
            val_to_set =  'expired'
        if stripe_subscription.status == 'incomplete':
            val_to_set =  'incomplete'
        if stripe_subscription.status == 'incomplete_expired':
            val_to_set =  'incomplete'
        if stripe_subscription.status == 'past_due':
            val_to_set =  'unable to charge'
        self.status = val_to_set

        #Update the day this account was synced
        self.date_last_synced_with_stripe = datetime.date.today()

        self.save()
        return self

    def __str__(self):
        """String for representing the Plan object (in Admin site etc.)."""
        return self.user.username
