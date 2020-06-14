from django.test import TestCase
from django.test import SimpleTestCase
from django.urls import reverse

from django.test import Client
from website.forms import ChangePasswordForm, SignUpForm, LoginForm, EditAccountForm

from django.contrib.auth.models import AnonymousUser, User
from django.contrib import auth

def yellow(message):
    ''' A custom function that sets strings meant for the consoll to yellow so that they stand out'''
    return '\n' + '\033[1;33;40m ' + message + '\x1b[0m'

##Why do tests top working when i set the SECURE_SSL_REDIRECT-setting
#import os
#from django.conf import settings
#
#print ('OS says redirect: %s'%(os.environ.get('DJANGO_SECURE_SSL_REDIRECT', "fuzzballs")))
#print ('Django says redirect: %s'%(settings.SECURE_SSL_REDIRECT))


# Create your tests here.
class AnswerSurveyViewTest(TestCase):
    ''' TESTS THAT THE ANSWER SURVEY VIEW BEHAVES PROPERLY '''
    def setUp(self):
        User.objects.create_user(   'macgyver@phoenix.com',
                                    'macgyver@phoenix.com',
                                    'anguspassword'
                                    )
        User.objects.create_user(   'thornton@phoenix.com',
                                    'thornton@phoenix.com',
                                    'petepassword'
                                    )
    def test_base(self):
        pass
        # test that faulty links i caught and 404-ed
        # test valid links aren't 404-ed
        # test closed survey instances are 404-ed,
        # open instances are NOT 404ed

        #test that there is a Page variable, that is either a number or None
        #if none, we get the page with no form
        #if a number we get the valid form
    def test_pagination_views(self):
        pass
        #test that a clean form is presented at a fresh survey instance form
        #test that the a survey instance that has already been answered displays the previous answers
        #on submit, test that data is saved, and you are correctly redirected (both to next page and to "done-page")
        #test if post shows something else than get (correctly)
