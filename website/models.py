from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

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
    badge_text = models.CharField(max_length=255, blank=True, default=None, help_text='What should the badge (if any) say?')
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
    additional_employee_monthly_price = models.DecimalField(max_digits=10, default=1.00, decimal_places=2, help_text='Montly price per additional employee')
    additional_employee_yearly_price = models.DecimalField(max_digits=10, default=10.00, decimal_places=2, help_text='Yearly price per additional employee')
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
    # stripe_plan_id

    def __str__(self):
        """String for representing the Plan object (in Admin site etc.)."""
        return self.name

class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, blank=True, null=True) #default free / no plan?
    date_current_plan_expires = models.DateField(default=timezone.now)
    custom_price = models.DecimalField(max_digits=10, blank=True, null=True, decimal_places=2, help_text='Special price for this Subscriber (leave blank to use the plan\'s price.)')

    PAYMENT_INTERVALS = (
        ('m', 'Monthly'),
        ('y', 'Yearly'),
            )

    payment_interval = models.CharField(
        max_length=1,
        choices=PAYMENT_INTERVALS,
        blank=True,
        default='',
        help_text='Payment interval',
    )
    def payment_amount(self):
        ''' return the amount due at each payment time. Does not currently account for any employees over included-limit '''
        if custom_price is not None:
            return custom_price
        if self.plan.is_paid:
            if self.payment_interval == 'y':
                return self.plan.yearly_price
            else:
                return  self.plan.monthly_price
        else:
            return 0.00


    def status(self):
        date_today=datetime.date.today()
        if self.plan is None:
            return 'inactive'
        if self.plan.is_paid =='n':
            return 'inactive'
        if self.date_current_plan_expires < date_today:
            return 'expired'
        else:
            return 'active'
        return 'inactive' #catchall - shouldn't hapen

    def __str__(self):
        """String for representing the Plan object (in Admin site etc.)."""
        return self.user.username
