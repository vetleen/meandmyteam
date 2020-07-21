from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
#from django.db import IntegrityError

from website.forms import *
from website.models import *


#set up logging
import logging
logger = logging.getLogger('__name__')
#logging.disable(logging.CRITICAL)
#logging.disable(logging.NOTSET)


# Create your tests here.
class FormsTest(TestCase):
    ''' TESTS THAT THE ANSWER SURVEY VIEW BEHAVES PROPERLY '''
    def setUp(self):
        pass

    def test_SignUpForm(self):

        #test that valid data makes a valid form
        data = {
            'username': "testuser@testing.te",
            'password': "qw34¥ytg",
            'confirm_password': "qw34¥ytg",
            'name': "A Testing Organization",
            'phone': "+4799999999",
            'address_line_1': "Test street 42",
            'address_line_2': "",
            'zip_code': "9999",
            'city': "Ålesund",
            'country': "NO",
            'accepted_terms_and_conditions': True,
        }

        test_form = SignUpForm(data=data)
        self.assertTrue(test_form.is_valid())

        #test invalid username gives error
        data.update({'username': "testuser96"})
        test_form = SignUpForm(data=data)
        self.assertFalse(test_form.is_valid())
        self.assertTrue(test_form.has_error('username'))
        self.assertIn("Enter a valid email address.", test_form.errors['username'])

        #test invalid password gives error
        data.update({
            'username': "testuser@testing.te",
            'password': "qqq",
            'confirm_password': "qqq",
            })
        test_form = SignUpForm(data=data)
        self.assertFalse(test_form.is_valid())
        self.assertTrue(test_form.has_error('password'))
        self.assertIn("This password is too short. It must contain at least 8 characters.", test_form.errors['password'])
        self.assertIn("This password is too common.", test_form.errors['password'])

        #test two different passwords gives error
        data.update({
            'password': "qw34¥ytg",
            'confirm_password': "qw34¥ytg1",
            })

        test_form = SignUpForm(data=data)
        self.assertFalse(test_form.is_valid())
        self.assertTrue(test_form.has_error('confirm_password'))
        self.assertIn("The second password you entered did not match the first. Please try again.", test_form.errors['confirm_password'])

        #test that username and name must be unique
        user = User(username="taken@motpanel.com", password="password")
        user.save()
        organization=Organization(name="TakenName Inc.")
        organization.save()

        data.update({
            'password': "qw34¥ytg",
            'confirm_password': "qw34¥ytg",
            'username': "taken@motpanel.com",
            'name': "TakenName Inc.",
            })
        test_form = SignUpForm(data=data)
        #print(dir(test_form))
        self.assertFalse(test_form.is_valid())
        self.assertTrue(test_form.has_error('username'))
        self.assertIn("A user with the email already exist (%s)."%("taken@motpanel.com"), test_form.errors['username'])
        self.assertTrue(test_form.has_error('name'))
        self.assertIn("An organization with that name already exists (%s)."%("TakenName Inc."), test_form.errors['name'])

        #test that accepted_terms_and_conditions must be True
        data.update({
            'username': "testuser@testing.te",
            'name': "A Testing Organization",
            'accepted_terms_and_conditions': False,
            })
        test_form = SignUpForm(data=data)
        self.assertFalse(test_form.is_valid())
        self.assertTrue(test_form.has_error('accepted_terms_and_conditions'))
        self.assertIn("Please indicate that you accept the terms and conditions.", test_form.errors['accepted_terms_and_conditions'])

        #test that an invalid phone number raises errer
        data.update({
            'accepted_terms_and_conditions': True,
            'phone': "+47 99"
            })
        test_form = SignUpForm(data=data)
        self.assertFalse(test_form.is_valid())
        self.assertTrue(test_form.has_error('phone'))
        self.assertIn("Enter a valid phone number (e.g. +12125552368).", test_form.errors['phone']) #I am unable to change this error mesage, should be revisited in the next five years or so...

        #reset data
        data.update({
            'phone': "+4799999999"
            })
        test_form = SignUpForm(data=data)
