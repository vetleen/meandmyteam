import datetime

from django.test import TestCase
from website.models import Organization
from surveys.models import *
from django.contrib.auth.models import User


# Create your tests here.
class TestModels(TestCase):

    def setUp(self):
        u = User (username="testuser@tt.tt", email="testuser@tt.tt", password="password")
        u.save()
        o = Organization(
                owner=u,
                name="TestOrg",
                phone=None,
                address_line_1="Test st. 77",
                address_line_2=None,
                zip_code="7777",
                city="Test Town",
                country='NO'
            )
        o.save()
        r = Respondent(
                organization=o,
                first_name=None,
                last_name=None,
                email="testrespondent@tt.tt",
                receives_surveys=True
            )
        r.save()

    def test_organization_update_stripe_subscription_quantity(self):
        user = User.objects.get(id=1)
        organization = Organization.objects.get(id=1)

        #since we created the employee manually, we should start with 0
        self.assertEqual(organization.stripe_subscription_quantity, 0)

        #Test update_stripe_subscription_quantity
        organization.update_stripe_subscription_quantity()

        #test that we now got 1
        self.assertEqual(organization.stripe_subscription_quantity, 1)

        #add another employee
        r2 = Respondent(
                organization=organization,
                first_name=None,
                last_name=None,
                email="testrespondent2@tt.tt",
                receives_surveys=True
            )
        r2.save()

        #test that we have 2
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 2)

        #add 15 more
        for i in range(15):
            rx = Respondent(
                    organization=organization,
                    first_name=None,
                    last_name=None,
                    email="testrespondent%s@tt.tt"%(i+3),
                    receives_surveys=True
                )
            rx.save()

        #test that we have 17
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 17)

        #try remove 5 emplopyees
        count = 0
        for r in Respondent.objects.all().reverse():
            if count <= 4:
                count+=1
                r.delete()

        #test that we now have 12
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 12)

        #delete all
        for r in Respondent.objects.all().reverse():
            r.delete()

        #Test that we now have Zero
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 0)

        #add 15 again
        for i in range(15):
            rx = Respondent(
                    organization=organization,
                    first_name=None,
                    last_name=None,
                    email="testrespondent%s@tt.tt"%(i),
                    receives_surveys=True
                )
            rx.save()

        #test that we have 17
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 15)














#
