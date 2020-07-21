import datetime

from django.test import TestCase
from website.models import Organization
from surveys.models import *
from django.contrib.auth.models import User

#from phonenumber_field.validators import validate_international_phonenumber
from phonenumber_field import phonenumber
# Create your tests here.
class TestModels(TestCase):

    def setUp(self):
        pass


    def test_Organization__phone_valid(self):
        #test that we can create an organization with a valid number
        valid_phone_number_list=[
            "+4799999999",
            "+47 999 99 998",
            "+47 99 99 99 97",
            "+4799 99 99 96",
            "+460771840100",
            "+1 650-326-0983",
            "+1 650 326 0984",
            "+16503260985",
        ]
        for n, number in enumerate(valid_phone_number_list):
            user = User(username="testuser%s@tt.tt"%(n), email="testuser%s@tt.tt"%(n), password="password")
            user.save()
            organization = Organization(
                    owner=user,
                    name="TestOrg%s"%(n),
                    phone=number,
                    address_line_1="Test st. 77",
                    address_line_2=None,
                    zip_code="7777",
                    city="Test Town",
                    country='NO'
                )
            organization.save()

            self.assertEqual(organization.phone, number)
            self.assertEqual(type(organization.phone), phonenumber.PhoneNumber)
            self.assertTrue(organization.phone.is_valid())

    def test_Organization__phone_invalid(self):
        #test that we cannot create an organization with a valid number
        invalid_phone_number_list=[
            "+4699999999",
            "+41 999 99 998",
            "+34 99 99 99 97",
            "+4199 99 99 96",
            "+470771840100",
            "+47 650-326-0983",
            "+47 650 326 0984",
            "+476503260985",
        ]
        user = User(username="testuser@tt.tt", email="testuser@tt.tt", password="password")
        user.save()
        for n, number in enumerate(invalid_phone_number_list):
            def make_org_with_bad_phone():
                organization = Organization(
                        owner=user,
                        name="TestOrg%s"%(n),
                        phone=number,
                        address_line_1="Test st. 77",
                        address_line_2=None,
                        zip_code="7777",
                        city="Test Town",
                        country='NO'
                    )
                organization.save()

            self.assertRaises(ValidationError, make_org_with_bad_phone)


    def test_organization_update_stripe_subscription_quantity(self):
        user = User(username="testuser@tt.tt", email="testuser@tt.tt", password="password")
        user.save()
        organization = Organization(
                owner=user,
                name="TestOrg",
                phone=None,
                address_line_1="Test st. 77",
                address_line_2=None,
                zip_code="7777",
                city="Test Town",
                country='NO'
            )
        organization.save()
        r = Respondent(
                organization=organization,
                first_name=None,
                last_name=None,
                email="testrespondent@tt.tt",
                receives_surveys=True
            )
        r.save()

        #Test that the organization's stripe_subscription_quantity should be 0 (since we created the employee manually)
        self.assertEqual(organization.stripe_subscription_quantity, 0)

        #Test that we get 1 when we run update_stripe_subscription_quantity
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 1)

        #test that we now have 2 when we add another employee
        r2 = Respondent(
                organization=organization,
                first_name=None,
                last_name=None,
                email="testrespondent2@tt.tt",
                receives_surveys=True
            )
        r2.save()
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 2)

        #test that we have 17 when we add 15 more
        for i in range(15):
            rx = Respondent(
                    organization=organization,
                    first_name=None,
                    last_name=None,
                    email="testrespondent%s@tt.tt"%(i+3),
                    receives_surveys=True
                )
            rx.save()

        #
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 17)

        #test that we now have 12 when we remove 5 emplopyees
        count = 0
        for r in Respondent.objects.all().reverse():
            if count <= 4:
                count+=1
                r.delete()
        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 12)

        #Test that we now have 0 and we delete all
        for r in Respondent.objects.all().reverse():
            r.delete()

        organization.update_stripe_subscription_quantity()
        self.assertEqual(organization.stripe_subscription_quantity, 0)















#
