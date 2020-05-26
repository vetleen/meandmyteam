
from django.test import TestCase, SimpleTestCase

from django.contrib.auth.models import AnonymousUser, User
from django.contrib import auth
from payments.utils.stripe_logic import *
from surveys.models import Organization, Employee, Survey, SurveyInstance, IntAnswer, TextAnswer, Question, Product, ProductSetting

from datetime import date, timedelta

from django.core import mail
# Create your tests here.

class HandleSubscribersTest(TestCase):
    ''' TESTS FUNCTIONS IN FUNCTIONS.PY '''
    def setUp(self):
        u = User(username="testuser@aa.aa", email="testuser@aa.aa", password="insecure123")
        u.save()

        o = Organization(owner=u, name="TestOrga1", address_line_1="476 Main street")
        o.save()
    def test_create_subscribers(self):
        o = Organization.objects.get(pk=1)
        s = create_stripe_customer(o)
        #test that a subscriber was created
        self.assertNotEqual(s, None)
        self.assertEqual(s.object, "customer")
        #clean up
        ds = delete_stripe_customer(s.id)

    def test_retrieve_customer(self):
        o = Organization.objects.get(pk=1)
        s = create_stripe_customer(o)
        rs = retrieve_stripe_customer(s.id)
        #test that the stripe customer was retrieved
        self.assertEqual(s, rs)
        #clean up
        ds = delete_stripe_customer(rs.id)

    def test_delete_customer(self):
        o = Organization.objects.get(pk=1)
        s = create_stripe_customer(o)
        ds = delete_stripe_customer(s.id)
        #test that s was deleted
        self.assertNotEqual(ds, None)
        self.assertTrue(ds.deleted)
        self.assertEqual(s.id, ds.id)

    def test_create_stripe_payment_method(self):
        o = Organization.objects.get(pk=1)
        c = create_stripe_customer(o)
        card ={
            "number": "4242424242424242",
            "exp_month": 5,
            "exp_year": 2021,
            "cvc": "314",
        }
        self.assertEqual(c.invoice_settings.default_payment_method, None)
        pm = create_stripe_payment_method(card, c.id)
        #test that PM was created and attached
        self.assertNotEqual(pm, None)
        self.assertEqual(pm.object, "payment_method")
        self.assertEqual(pm.customer, c.id)
        c = retrieve_stripe_customer(c.id)
        self.assertEqual(pm.id, c.invoice_settings.default_payment_method)

        #clean up
        dc = delete_stripe_customer(c.id)

    def test_create_stripe_subscription(self):
        o = Organization.objects.get(pk=1)
        c = create_stripe_customer(o)
        card ={
            "number": "4242424242424242",
            "exp_month": 5,
            "exp_year": 2021,
            "cvc": "314",
        }
        pm = create_stripe_payment_method(card, c.id)
        s = create_stripe_subscription(stripe_customer_id=c.id, quantity=25)
        #Test that a subscription was created and that trial period was set correctly
        self.assertEqual(s.object, "subscription")
        self.assertEqual(s.quantity, 25)

        #clean up
        dc = delete_stripe_customer(c.id)

    def test_delete_stripe_subscription(self):
        o = Organization.objects.get(pk=1)
        c = create_stripe_customer(o)
        card ={
            "number": "4242424242424242",
            "exp_month": 5,
            "exp_year": 2021,
            "cvc": "314",
        }
        pm = create_stripe_payment_method(card, c.id)
        s = create_stripe_subscription(stripe_customer_id=c.id)
        #Test that a subscription was created and that trial period was set correctly
        self.assertEqual(s.object, "subscription")
        self.assertNotEqual(s.status, "canceled")
        s = delete_stripe_subscription(s.id)
        self.assertEqual(s.status, "canceled")

        #clean up
        dc = delete_stripe_customer(c.id)

    def test_modify_stripe_subscription(self):
        o = Organization.objects.get(pk=1)
        c = create_stripe_customer(o)
        card ={
            "number": "4242424242424242",
            "exp_month": 5,
            "exp_year": 2021,
            "cvc": "314",
        }
        pm = create_stripe_payment_method(card, c.id)
        s = create_stripe_subscription(stripe_customer_id=c.id, quantity=25)
        #Test that a subscription was created and that trial period was set correctly
        self.assertEqual(s.object, "subscription")
        self.assertEqual(s.quantity, 25)
        #Test that we can modify quantity
        s = modify_stripe_subscription(s.id, quantity=10)
        #test that it doesnt change it when quantity is not passed in kwargs
        self.assertEqual(s.quantity, 10)
        s = modify_stripe_subscription(s.id)
        self.assertEqual(s.quantity, 10)
        #clean up
        dc = delete_stripe_customer(c.id)
