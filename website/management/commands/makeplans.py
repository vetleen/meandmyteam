from django.core.management.base import BaseCommand, CommandError
from website.models import Plan

class Command(BaseCommand):
    help = 'Makes three Plan objects for the review app'
    print("This command makes Plan objects if there are none.")
    print("Found %s Plan objects"%(len(Plan.objects.all())))

    def handle(*args, **kwargs):
        if len(Plan.objects.all()) == 0:
            print("...making three objects.")
            p = Plan(
            name = "Small business",
            illustration_static_address = "images/small-business-plan.svg",
            description = "REVIEW: A small plan for small businesses. With this plan you can track the satisfaction of up to 10 employees.",
            monthly_price = 15.00,
            yearly_price = 150.00,
            show_price = True,
            included_employees = 10,
            can_be_picked = True,
            can_be_viewed = True,
            is_paid = "y",
            stripe_monthly_plan_id = "plan_H7nTHThryy8L62",
            )
            p.save()

            p = Plan(
            name = "Standard",
            illustration_static_address = "images/standard-plan.svg",
            description = "REVIEW: A medium plan for medium businesses. With this plan you can track up to 50 employees' satisfaction.",
            monthly_price = 35.00,
            yearly_price = 350.00,
            show_price = True,
            included_employees = 50,
            can_be_picked = False,
            can_be_viewed = True,
            is_paid = "y",
            stripe_monthly_plan_id = "",
            )
            p.save()

            p = Plan(
            name = "Enterprise",
            illustration_static_address = "images/enterprise-plan.svg",
            description = "REVIEW: A big plan for big business. With this plan you can track as many employees as you want.",
            monthly_price = 70.00,
            yearly_price = 700.00,
            show_price = False,
            included_employees = 500,
            can_be_picked = False,
            can_be_viewed = True,
            is_paid = "y",
            stripe_monthly_plan_id = "",
            )
            p.save()
            print("...done.")
        else:
            print ("... not making any objects.")
        print("exiting.")
