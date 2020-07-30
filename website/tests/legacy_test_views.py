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

class DashboardViewTest(TestCase):
    ''' TESTS THAT THE DASHBOARD BEHAVES PROPERLY '''
    def setUp(self):
        User.objects.create_user(   'macgyver@phoenix.com',
                                    'macgyver@phoenix.com',
                                    'anguspassword'
                                    )
        User.objects.create_user(   'thornton@phoenix.com',
                                    'thornton@phoenix.com',
                                    'petepassword'
                                    )
    def test_anonymous_users(self):
        #Test that anonymous users are redirected properly
        response = self.client.get('/dashboard/', follow=True, secure=True)
        my_message = yellow('DashboardViewTest: anonymous users should be redirected when attempting to GET at this address')
        self.assertRedirects(response, '/login/?next=/dashboard/', 302, 200, msg_prefix=my_message)
        response = self.client.post('/dashboard/', follow=True, secure=True)
        my_message = yellow('DashboardViewTest: anonymous users should be redirected when attempting to POST to this address')
        self.assertRedirects(response, '/login/?next=/dashboard/', 302, 200, msg_prefix=my_message)

    def test_authenitcated_users(self):
        #log in
        self.credentials = {
            'username': 'macgyver@phoenix.com',
            'password': 'anguspassword'
            }
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)

        #check that it worked
        self.assertTrue(response.context['user'].is_active)

        #Test that authenticated users are shown the correct template
        my_message = "DashboardTestView: The template 'dashboard.html' should be used."
        self.assertTemplateUsed(response, 'dashboard.html', my_message)

class IndexViewTest(TestCase):
    ''' TESTS THAT THE FRONTPAGE BEHAVES PROPERLY '''
    def setUp(self):
        User.objects.create_user(   'macgyver@phoenix.com',
                                    'macgyver@phoenix.com',
                                    'anguspassword'
                                    )
        User.objects.create_user(   'thornton@phoenix.com',
                                    'thornton@phoenix.com',
                                    'petepassword'
                                    )
    def test_index_can_be_loaded(self):
        response = self.client.get('/', follow=True, secure=True)
        my_message = yellow('Couldn\'t find the front page at \'/\'')
        self.assertTemplateUsed(response, 'index.html', my_message)
    def test_authenticated_users_get_rd_to_dashboard(self):
        #log in
        self.credentials = {
            'username': 'macgyver@phoenix.com',
            'password': 'anguspassword'
            }
        login_response = self.client.post('/login/', self.credentials, follow=True, secure=True)
        #try go to front page
        response = self.client.post('/', self.credentials, follow=True, secure=True)
        #assert get dashboard
        my_message = yellow(' Active user was not correctly redirected when trying to reach front page: ')
        self.assertRedirects(response, '/dashboard/', 302, 200, msg_prefix=my_message)
        #assert correct template
        self.assertTemplateNotUsed(response, 'index.html', my_message)
        self.assertTemplateUsed(response, 'dashboard.html', my_message)

class SignUpViewTest(TestCase):
    """
    TEST THE SIGNUP VIEW IN EVERY WHICH WAY
    """
    #test that you are redirected if already authenticated
    #test that sign-up is possible
    def test_signup_is_possible_but_not_twice(self):
        signup_credentials = {'username':"jcdenton@unatco.gov", 'password': "bloodshot"}
        response = self.client.post('/sign-up/', {
                                    'username': signup_credentials['username'],
                                    'password': signup_credentials['password'],
                                    'confirm_password': signup_credentials['password']
                                    }, follow=True, secure=True)
        #check that user was signed in after creating user
        self.assertTrue(response.context['user'].is_active)
        users_w_uname = User.objects.filter(username = signup_credentials['username']).count()
        self.assertEqual(users_w_uname, 1, yellow("Signup-view should create exactly 1 user with the same username, not %s")%(users_w_uname))
        self.assertRedirects(response, '/dashboard/', 302, 200, msg_prefix="Expected user to be redirected to dashboard after sign-up")
        self.assertContains(response, 'Welcome aboard.', msg_prefix=yellow("expected a newly signed on user to be greeted by a hearty \'Welcome aboard.\'"))

        #test that signup is not possible with existing username
        #def test_signup_not_possible_with_exising_username(self):
        #signup_credentials = {'username':"jcdenton@unatco.gov", 'password': "bloodshot"}
        response = self.client.post('/logout/', follow=True, secure=True)
        self.assertFalse(response.context['user'].is_active) #logging out user before signing up again

        #same credentials as before
        response = self.client.post('/sign-up/', {
                                    'username': signup_credentials['username'],
                                    'password': signup_credentials['password'],
                                    'confirm_password': signup_credentials['password']
                                    }, follow=True, secure=True)
        #check that user was signed in after creating user
        self.assertFalse(response.context['user'].is_active) # should not be logged in, because should not be signed up
        self.assertEqual(User.objects.filter(username = signup_credentials['username']).count(), 1, yellow("Signup-view should not have created a new user with an existing username"))
        self.assertTemplateUsed(response, 'sign_up_form.html', yellow('Expected the tempate sign_up_form.html to be used'))
        self.assertNotContains(response, 'Welcome aboard.', msg_prefix=yellow("Did not expect a user that should have failed to sign up to be greeted by a hearty \'Welcome aboard.\'"))
        self.assertContains(response, 'A user with the email already exist', msg_prefix=yellow("Expected an error containing \'A user with the email already exist.\'"))

    #test that signup is not possible with no password
    def test_signup_not_possible_with_no_password(self):
        signup_credentials2 = {'username':"pauldenton@unatco.gov", 'password': "chameleon"}
        response = self.client.post('/logout/', follow=True, secure=True)
        self.assertFalse(response.context['user'].is_active) #logging oput user before signing up again

        #same credentials as before
        response = self.client.post('/sign-up/', {
                                    'username': signup_credentials2['username'],
                                    'password': '',
                                    'confirm_password': ''
                                    }, follow=True, secure=True)
        #check that user was signed in after creating user
        self.assertFalse(response.context['user'].is_active) # should not be logged in, because should not be signed up
        self.assertEqual(User.objects.filter(username = signup_credentials2['username']).count(), 0, yellow("Signup-view should not have created a new user when no password was provided"))
        self.assertTemplateUsed(response, 'sign_up_form.html', yellow('Expected the tempate sign_up_form.html to be used'))
        self.assertNotContains(response, 'Welcome aboard.', msg_prefix=yellow("Did not expect a user that should have failed to sign up to be greeted by a hearty \'Welcome aboard.\'"))
        self.assertContains(response, 'This field is required.', msg_prefix=yellow("Expected an error containing \'This field is required.\'"))

    #test that signup is not possible non-matching password
    def test_signup_not_possible_with_non_matching_passwords(self):
        signup_credentials2 = {'username':"pauldenton@unatco.gov", 'password': "chameleon"}
        response = self.client.post('/logout/', follow=True, secure=True)
        self.assertFalse(response.context['user'].is_active) #logging oput user before signing up again

        #same credentials as before
        response = self.client.post('/sign-up/', {
                                    'username': signup_credentials2['username'],
                                    'password': signup_credentials2['password'],
                                    'confirm_password': 'jcpassword'
                                    }, follow=True, secure=True)
        #check that user was signed in after creating user
        self.assertFalse(response.context['user'].is_active) # should not be logged in, because should not be signed up
        self.assertEqual(User.objects.filter(username = signup_credentials2['username']).count(), 0, yellow("Signup-view should not have created a new user when non-matching passwords was provided"))
        self.assertTemplateUsed(response, 'sign_up_form.html', yellow('Expected the tempate sign_up_form.html to be used'))
        self.assertNotContains(response, 'Welcome aboard.', msg_prefix=yellow("Did not expect a user that should have failed to sign up to be greeted by a hearty \'Welcome aboard.\'"))
        self.assertContains(response, 'The second password you entered did not match the first. Please try again.', msg_prefix=yellow("Expected an error containing \'The second password you entered did not match the first. Please try again.\'"))

class LoginViewTest(TestCase):
    """
    TEST THE LOGIN VIEW IN EVERY WHICH WAY
    """
    def setUp(self):
        User.objects.create_user(   'lennon@thebeatles.com',
                                    'lennon@thebeatles.com',
                                    'johnpassword'
                                    )
        User.objects.create_user(   'lennon@thebeatles2.com',
                                    'lennon@thebeatles2.com',
                                    'johnpassword2'
                                    )

    ### TESTS FOR IF USER IS ALREADY LOGGED IN ###
    def test_active_users_given_correct_template_and_a_message(self):
        #correct credentials
        self.credentials = {
            'username': 'lennon@thebeatles.com',
            'password': 'johnpassword'
            }
        #Login
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)
        #check that it worked
        self.assertTrue(response.context['user'].is_active)
        #try go to login page again
        response = self.client.get('/login/', follow=True, secure=True)
        messages = list(response.context['messages'])

        #check for logged in message
        my_message = yellow('LoginViewTest: Already logged in users should be told "You are already logged in."')
        self.assertContains(response, 'You are already logged in.', msg_prefix=my_message)

        my_message = yellow('LoginViewTest: Already logged in user should be redirected to dashboard.')
        self.assertTemplateUsed(response, 'dashboard.html', my_message)

    ### TESTS FOR GET ###
    def test_correct_form_and_template_is_used(self):
        ''' Test that a GET request is met with the correct form and template '''
        response = self.client.get('/login/', follow=True, secure=True)
        received_form = response.context['form']
        #print(response.context)
        my_message = yellow('LoginViewTest: %s was not the expected object'% (received_form))
        self.assertEqual(received_form, LoginForm, my_message)
        my_message = yellow('LoginViewTest: An anonymous user was not shown the correct template at /login/.')
        self.assertTemplateUsed(response, 'login_form.html', my_message)

    ### TESTS FOR  POST ###
    def test_login_works(self):
        ''' Test that login works with valid credentials '''
        self.credentials = {
            'username': 'lennon@thebeatles.com',
            'password': 'johnpassword'
            }
        #user = User.objects.get(username='lennon@thebeatles.com')
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)
        # should be logged in now
        my_message = yellow('LoginViewTest: User was not logged in as expected')
        self.assertTrue(response.context['user'].is_active, my_message)
        my_message = yellow('LoginViewTest: The \"active\" user was not the expected user.')
        self.assertEqual(response.context['user'], User.objects.get(username='lennon@thebeatles.com'), my_message)

        messages = list(response.context['messages'])
        #my_message = 'User was not given exactly 1 messages as expected after he loged in, but %s.'%(len(messages))
        #self.assertEqual(len(messages), 4, yellow(my_message))
        my_message = yellow('LoginViewTest: User was not correctly redirected after login')
        self.assertRedirects(response, '/dashboard/', 302, 200, msg_prefix=my_message)
        #SimpleTestCase.assertContains(response, text, count=None, status_code=200, msg_prefix='', html=False)
        my_message = yellow('LoginViewTest: After login the expected "You have logged in."-text did not show')
        self.assertContains(response, 'You have logged in.', msg_prefix=my_message)

    def test_login_does_not_work_for_unathorized(self):
        ''' Test that login doesnt work with invalid credentials '''

        self.credentials = {
            'username': 'lennon@thebeatles.com', #existing
            'password': 'elvispassword' #wrong
            }
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)
        # should NOT be logged in now
        my_message = yellow('LoginViewTest: User was logged in mysteriously, despite submitting the wrong password')
        self.assertFalse(response.context['user'].is_active, my_message)

        #and should get the login form again:
        received_form = response.context['form']
        #print(response.context)
        my_message = yellow('LoginViewTest: %s was not an insatnce ofg LoginForm. A user giving the wrong password was supposed to get the form anew.'% (received_form))
        self.assertIsInstance(received_form, LoginForm, my_message)
        my_message = yellow('LoginViewTest: A user giving the wrong password was not shown the correct template at /login/.')
        self.assertTemplateUsed(response, 'login_form.html', my_message)

class LogoutViewTest(TestCase):
    """
    TEST THE LOGOUT VIEW IN EVERY WHICH WAY
    """
    def setUp(self):
        User.objects.create_user(   'lennon@thebeatles.com',
                                    'lennon@thebeatles.com',
                                    'johnpassword'
                                    )
        User.objects.create_user(   'lennon@thebeatles2.com',
                                    'lennon@thebeatles2.com',
                                    'johnpassword2'
                                    )
    def test_logout(self):
        #correct credentials
        self.credentials = {
            'username': 'lennon@thebeatles.com',
            'password': 'johnpassword'
            }
        #Login
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)
        #check that it worked
        my_message = yellow('TestLogoutView: User was supposed to be logged in' )
        self.assertTrue(response.context['user'].is_active, my_message)
        #try logout
        response = self.client.get('/logout/', follow=True, secure=True)
        my_message = yellow('TestLogoutView: User was supposed to be logged out after visiting /logout/' )
        self.assertFalse(response.context['user'].is_active, my_message)
        my_message = 'TestLogoutView: After logout user was supposed to find a different template.'
        self.assertTemplateUsed(response, 'logout_complete.html', yellow(my_message))
        my_message = yellow('TestLogoutView: After logout the expected "You have logged out successfully."-text did not show')
        self.assertContains(response, 'You have logged out successfully.', msg_prefix=my_message)


class ChangePasswordViewTest(TestCase):
    """
    TEST THE CHANGE PASSWORD VIEW IN EVERY WHICH WAY
    """
    def setUp(self):
        User.objects.create_user(   'lennon@thebeatles.com',
                                    'lennon@thebeatles.com',
                                    'johnpassword'
                                    )
        User.objects.create_user(   'lennon@thebeatles2.com',
                                    'lennon@thebeatles2.com',
                                    'johnpassword2'
                                    )
    def test_that_login_is_required(self):

        #Test that login is required
        response = self.client.get('/change-password/', follow=True, secure=True)
        my_message = yellow('ChangePasswordViewTest: anonymous users should be redirected when attempting to GET at this address')
        self.assertRedirects(response, '/login/?next=/change-password/', 302, 200, msg_prefix=my_message)
        response = self.client.post('/change-password/', follow=True, secure=True)
        my_message = yellow('ChangePasswordViewTest: anonymous users should be redirected when attempting to POST to this address')
        self.assertRedirects(response, '/login/?next=/change-password/', 302, 200, msg_prefix=my_message)

    def test_get_requests(self):
        #correct credentials
        self.credentials = {
            'username': 'lennon@thebeatles.com',
            'password': 'johnpassword'
            }
        #Login
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)

        #check that it worked
        my_message = yellow('ChangePasswordViewTest: User was supposed to be logged in' )
        self.assertTrue(response.context['user'].is_active, my_message)

        #Test GET works
        response = self.client.get('/change-password/', follow=True, secure=True)

        ##correct template
        my_message = yellow('ChangePasswordViewTest: Should use template "change_password_form.html".')
        self.assertTemplateUsed(response, 'change_password_form.html', my_message)

        ##correct form
        my_message = yellow('ChangePasswordViewTest: Expected ChangePasswordForm to be available in context.')
        self.assertTrue(response.context['form'], my_message)

    def test_post_requests(self):
        #correct credentials
        self.credentials = {
            'username': 'lennon@thebeatles.com',
            'password': 'johnpassword'
            }
        #Login
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)

        #check that it worked
        my_message = yellow('ChangePasswordViewTest: User was supposed to be logged in' )
        self.assertTrue(response.context['user'].is_active, my_message)

        ###Test POST works
        #wrong input in all fields
        response = self.client.post('/change-password/', {'old_password': "", 'new_password': "", 'confirm_new_password': ""}, follow=True, secure=True)
        my_message = yellow('ChangePasswordViewTest: %s should be an instance of ChangePasswordForm.'%(response.context['form']))
        received_form = response.context['form']
        self.assertIsInstance(received_form, ChangePasswordForm, my_message)
        my_message = yellow('ChangePasswordViewTest: should use change_password_form-html template.')
        self.assertTemplateUsed(response, 'change_password_form.html', my_message)

        #correct input in all fields
        response = self.client.post('/change-password/', {'old_password': "johnpassword", 'new_password': "newjohnpassword", 'confirm_new_password': "newjohnpassword"}, follow=True, secure=True)
        my_message = yellow('ChangePasswordViewTest: %s should exist.'%(response.context['form']))
        received_form = response.context['form']
        self.assertIsInstance(received_form, ChangePasswordForm, my_message)
        my_message = yellow('ChangePasswordViewTest: should use change_password_form-html template.')
        self.assertTemplateUsed(response, 'change_password_form.html', my_message)

        #gotta check the user is still logged in:
        self.assertTrue(response.context['user'].is_active)

        #should stil use the right template
        my_message = 'ChangePasswordViewTest: Should use template "change_password_form.html".'
        self.assertTemplateUsed(response, 'change_password_form.html', yellow(my_message))
        #Are passwords correctly updated?
        my_message = yellow('ChangePasswordViewTest: password should be changed')
        self.assertFalse(response.context['user'].check_password('johnpassword'), my_message)
        self.assertTrue(response.context['user'].check_password('newjohnpassword'), my_message)

        #Are passwords incorrectly updated when you provide the wrong passowrd?
        response = self.client.post('/change-password/', {'old_password': "ggg", 'new_password': "ejpassword", 'confirm_new_password': "ejpassword"}, follow=True, secure=True)
        my_message = yellow('ChangePasswordViewTest: password should NOT be changed.')
        self.assertFalse(response.context['user'].check_password('ejpassword'), my_message)
        self.assertTrue(response.context['user'].check_password('newjohnpassword'), my_message)

        #should stil use the right template
        my_message = 'ChangePasswordViewTest: Should use template "change_password_form.html".'
        self.assertTemplateUsed(response, 'change_password_form.html', yellow(my_message))

class EditAccountViewTest(TestCase):
    ''' TESTS THAT THE DASHBOARD BEHAVES PROPERLY '''
    def setUp(self):
        User.objects.create_user(   'macgyver@phoenix.com',
                                    'macgyver@phoenix.com',
                                    'anguspassword'
                                    )
        User.objects.create_user(   'thornton@phoenix.com',
                                    'thornton@phoenix.com',
                                    'petepassword'
                                    )
    #Test that anonymous users are redirected to login
    def test_anonymous_users(self):
        #Test that anonymous users are redirected properly
        response = self.client.get('/edit-account/', follow=True, secure=True)
        my_message = yellow('EditAccountViewTest: anonymous users should be redirected when attempting to GET at this address')
        self.assertRedirects(response, '/login/?next=/edit-account/', 302, 200, msg_prefix=my_message)
        response = self.client.post('/edit-account/', follow=True, secure=True)
        my_message = yellow('EditAccountViewTest: anonymous users should be redirected when attempting to POST to this address')
        self.assertRedirects(response, '/login/?next=/edit-account/', 302, 200, msg_prefix=my_message)

    #Test loggeed in users are shown proper page
    def test_authenitcated_users_can_visit_site(self):
        ## Set up
        #log in
        self.credentials = {
            'username': 'macgyver@phoenix.com',
            'password': 'anguspassword'
            }
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)
        #check that it worked
        self.assertTrue(response.context['user'].is_active)

        ##tests
        response = self.client.get('/edit-account/', follow=True, secure=True)
        self.assertTemplateUsed(response, 'edit_account_form.html', yellow('EditAccountViewTest: Expected edit_account_form.html template to be used.'))
        self.assertIsInstance(response.context['form'], EditAccountForm, yellow('EditAccountViewTest: Expected EditAccountForm to be used.'))

    #Test account username can be updated, and that both email and uname is
    def test_authenitcated_users_can_edit(self):
        #log in
        self.credentials = {
            'username': 'macgyver@phoenix.com',
            'password': 'anguspassword'
            }
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)

        #check that it worked
        self.assertTrue(response.context['user'].is_active)

        #Tests
        response = self.client.post('/edit-account/', {'username': 'am@phoenix.com'}, follow=True, secure=True)
        self.assertTemplateUsed(response, 'edit_account_form.html', yellow('EditAccountViewTest: Expected edit_account_form.html template to be used.'))
        self.assertIsInstance(response.context['form'], EditAccountForm, yellow('EditAccountViewTest: Expected EditAccountForm to be used.'))
        users_w_uname = User.objects.filter(username = 'am@phoenix.com').count()
        self.assertEqual(users_w_uname, 1, yellow("Expected exactly 1 user with the filtered username, not %s")%(users_w_uname))
        users_w_uname = User.objects.filter(username = 'macgyver@phoenix.com').count()
        self.assertEqual(users_w_uname, 0, yellow("Expected exactly 0 users with the filtered username, not %s")%(users_w_uname))
    #Test that you cant change to your own name (and proper error)
    def test_authenitcated_users_cant_change_to_current_name(self):
        #log in
        self.credentials = {
            'username': 'macgyver@phoenix.com',
            'password': 'anguspassword'
            }
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)

        #check that it worked
        self.assertTrue(response.context['user'].is_active)

        #Tests
        response = self.client.post('/edit-account/', {'username': self.credentials['username']}, follow=True, secure=True)
        self.assertTemplateUsed(response, 'edit_account_form.html', yellow('EditAccountViewTest: Expected edit_account_form.html template to be used.'))
        self.assertIsInstance(response.context['form'], EditAccountForm, yellow('EditAccountViewTest: Expected EditAccountForm to be used.'))
        self.assertContains(response, 'Your email is already set to', msg_prefix=yellow("EditAccountViewTest: expected error message containing \'Your email is already set to\'"))

    #Test that you cant change to someone else's name (and proper error)
    def test_authenitcated_users_cant_change_to_occupied_name(self):
        #log in
        self.credentials = {
            'username': 'macgyver@phoenix.com',
            'password': 'anguspassword'
            }
        response = self.client.post('/login/', self.credentials, follow=True, secure=True)

        #check that it worked
        self.assertTrue(response.context['user'].is_active)

        #Tests
        response = self.client.post('/edit-account/', {'username': 'thornton@phoenix.com'}, follow=True, secure=True)
        self.assertTemplateUsed(response, 'edit_account_form.html', yellow('EditAccountViewTest: Expected edit_account_form.html template to be used.'))
        self.assertIsInstance(response.context['form'], EditAccountForm, yellow('EditAccountViewTest: Expected EditAccountForm to be used.'))
        self.assertContains(response, 'A user with the email already exist', msg_prefix=yellow("EditAccountViewTest: expected error message containing \'A user with the email already exist\'"))
        #print(response.content)
