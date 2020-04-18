from django.db import models
from django.contrib.auth.models import User

import datetime
from django.utils import timezone


# Create your models here.

#Plan
    #name
    #short_description

    #price_monthly
    #price_yearly

class Plan(models.Model):
    """The plans user can choose from."""

    # Fields
    name = models.CharField(max_length=60, help_text='Name of the plan')
    description = models.CharField(max_length=255, help_text='A short description of the plan')
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Montly price')
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Yearly price')
    #allowed_nr_of_employees
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
    def __str__(self):
        """String for representing the Plan object (in Admin site etc.)."""
        return self.name

class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True) #default free / no plan?
    date_current_plan_expires = models.DateField(default=timezone.now)
    #custom price?
    #trial?

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
    #maybe it would be more interesting with a get_status-function, including an expired-value
    def is_active(self):
        #print('Plan expires: %s'%(self.date_current_plan_expires))
        date_today=datetime.date.today()
        #print('Todays date is: %s'%(date_today))
        if self.plan is None:
            return False
        if self.plan.is_paid =='n':
            return False
        if self.date_current_plan_expires < date_today:
            return False
        else:
            return True
        return False #catchall - shouldn't hapen

    def __str__(self):
        """String for representing the Plan object (in Admin site etc.)."""
        return self.user.username
