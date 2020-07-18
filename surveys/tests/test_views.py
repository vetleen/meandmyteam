import datetime
from django.test import TestCase
from django.test import SimpleTestCase
from django.test import Client
from django.urls import reverse

from django.contrib.auth.models import AnonymousUser, User
from django.contrib import auth

#my stuff
from surveys.forms import *
from surveys.models import *
from surveys.tests.testdata import create_test_data
from surveys.core import setup_instrument
from surveys.core import survey_logic



#set up logging
import logging
logger = logging.getLogger('__name__')
logging.disable(logging.CRITICAL)
#logging.disable(logging.NOTSET)

# Create your tests here.
class TestThatUrlsExist(TestCase):
    """
    Test that URLs yield expected response
    """
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

        rti = create_test_data(1)
        setup_instrument.setup_instrument(rti)
        i = Instrument.objects.get(id=1)

        #configure surveys
        survey_setting = survey_logic.configure_survey_setting(
            organization=o,
            instrument=i,
            is_active=True
        )
        #create a survey and instance
        s = survey_logic.create_survey(owner=o, instrument_list=[i, ])
        si_list = survey_logic.survey_instances_from_survey(s)
'''
    def test_url_status_codes(self):
        user = User.objects.get(id=1)
        organization = Organization.objects.get(id=1)
        employee = Respondent.objects.get(id=1)
        instrument = Instrument.objects.get(id=1)
        survey_instance = SurveyInstance.objects.get(id=1)
        survey = Survey.objects.get(id=1)

        deletable_respondent = Respondent(
                organization=organization,
                first_name=None,
                last_name=None,
                email="testrespondenttodelete@tt.tt",
                receives_surveys=True
            )
        deletable_respondent.save()

        self.client.force_login(user=user)

        ## Set the conditions for URL-testing
        urls_to_test = [
            #dashboard_urls
            reverse('surveys-dashboard'),
            reverse('surveys-add-or-remove-employees'),
            reverse('surveys-edit-employee', args=[employee.uidb64()]),
            reverse('surveys-delete-employee', args=[deletable_respondent.uidb64()]),
            #survey_urls
            reverse('surveys-setup-instrument', args=[instrument.slug_name]),
            reverse('surveys-survey-details', args=[survey.uidb64(), instrument.slug_name]),
            reverse('surveys-answer-survey', args=[survey_instance.get_url_token()]),
            reverse('surveys-answer-survey-pages', args=[survey_instance.get_url_token(), 1]),
        ]

        #test that all URL exist
        for url in urls_to_test:
            response = self.client.get(url, follow=True, secure=True)
            self.assertEqual(response.status_code, 200, "%s gives url status code %s."%(url, response.status_code))
'''

class TestViews(TestCase):
    """
    Test each view
    """
    def setUp(self):
        u = User(username="testuser@tt.tt", email="testuser@tt.tt", password="password")
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

        rti = create_test_data(1)
        setup_instrument.setup_instrument(rti)
        i = Instrument.objects.get(id=1)

        #configure surveys
        survey_setting = survey_logic.configure_survey_setting(
            organization=o,
            instrument=i,
            is_active=True
        )
        #create a survey and instance
        s = survey_logic.create_survey(owner=o, instrument_list=[i, ])
        si_list = survey_logic.survey_instances_from_survey(s)
    '''
    def test_add_or_remove_employee_view(self):
        user = User.objects.get(id=1)
        organization = Organization.objects.get(id=1)

        #test that login is required
        response = self.client.get(reverse('surveys-add-or-remove-employees'), follow=True, secure=True)
        self.assertRedirects(response, reverse('loginc')+"?next="+reverse('surveys-add-or-remove-employees'), 302, 200)
        self.assertTemplateNotUsed(response, 'add_or_remove_employees.html')

        #test that we get the correct page when we log in and GET this page
        self.client.force_login(user=user)
        response = self.client.get(reverse('surveys-add-or-remove-employees'), follow=True, secure=True)
        self.assertTemplateUsed(response, 'add_or_remove_employees.html')
        self.assertEqual(response.status_code, 200)
        #test that the correct context is served
        self.assertIsInstance(response.context['form'], AddRespondentForm)
        self.assertFalse(response.context['form'].is_bound)
        respondent_list = organization.respondent_set.all()
        self.assertEqual(len(response.context['employee_list']), len(respondent_list))
        for r in respondent_list:
            self.assertIn(r, response.context['employee_list'])
        for r in response.context['employee_list']:
            self.assertIn(r, respondent_list)
        self.assertIn('submit_button_text', response.context)

        #test that POST works also
        #post minimal and see if it works
        valid_employee_data = {'email': "new_employee@tt.tt"}
        response = self.client.post(reverse('surveys-add-or-remove-employees'), valid_employee_data, follow=True, secure=True)
        self.assertTemplateUsed(response, 'add_or_remove_employees.html')
        self.assertEqual(response.status_code, 200)
        #test that an employee was added
        self.assertEqual(len(Respondent.objects.all()), 2)
        new_respondent = Respondent.objects.get(id=2)
        self.assertEqual(new_respondent.email, "new_employee@tt.tt")
        organization = Organization.objects.get(id=1)
        self.assertEqual(len(Respondent.objects.all()), organization.stripe_subscription_quantity)

        #test that the correct context is served
        self.assertIsInstance(response.context['form'], AddRespondentForm)
        self.assertFalse(response.context['form'].is_bound)
        self.assertTrue(response.context['form'].has_error)
        for field in response.context['form'].fields:
            self.assertFalse(response.context['form'].has_error(field))
        respondent_list = organization.respondent_set.all()
        self.assertEqual(len(response.context['employee_list']), len(respondent_list))
        for r in respondent_list:
            self.assertIn(r, response.context['employee_list'])
        for r in response.context['employee_list']:
            self.assertIn(r, respondent_list)


        #post a bit more and see if THAT works
        valid_employee_data = {'email': "a_third_employee@tt.tt", 'first_name': "tt", 'last_name': "yy"}
        response = self.client.post(reverse('surveys-add-or-remove-employees'), valid_employee_data, follow=True, secure=True)
        self.assertTemplateUsed(response, 'add_or_remove_employees.html')
        self.assertEqual(response.status_code, 200)
        #test that an employee was added
        self.assertEqual(len(Respondent.objects.all()), 3)
        new_respondent = Respondent.objects.get(id=3)
        self.assertEqual(new_respondent.email, "a_third_employee@tt.tt")
        self.assertEqual(new_respondent.first_name, "tt")
        self.assertEqual(new_respondent.last_name, "yy")
        #test that the correct context is served
        self.assertIsInstance(response.context['form'], AddRespondentForm)
        self.assertFalse(response.context['form'].is_bound)
        for field in response.context['form'].fields:
            self.assertFalse(response.context['form'].has_error(field))

        #make sure we cant add the same email twice
        invalid_employee_data = {'email': "a_third_employee@tt.tt", 'first_name': "tt", 'last_name': "yy"}
        response = self.client.post(reverse('surveys-add-or-remove-employees'), invalid_employee_data, follow=True, secure=True)
        self.assertTemplateUsed(response, 'add_or_remove_employees.html')
        self.assertEqual(response.status_code, 200)
        #test that an employee was NOT added
        self.assertEqual(len(Respondent.objects.all()), 3)
        #test that the correct context is served
        self.assertIsInstance(response.context['form'], AddRespondentForm)
        self.assertTrue(response.context['form'].is_bound)
        self.assertTrue(response.context['form'].has_error('email'))

        #ensure stripe subscription quantity was updated in OUR database
        self.assertEqual(len(Respondent.objects.filter(organization=organization)), organization.update_stripe_subscription_quantity())

    def test_edit_employee_view(self):
        user = User.objects.get(id=1)
        employee = Respondent.objects.get(id=1)

        #test that login is required
        #try grab an actual employee
        response = self.client.get(reverse('surveys-edit-employee', args=[employee.uidb64()]), follow=True, secure=True)
        self.assertRedirects(response, reverse('loginc')+"?next="+reverse('surveys-edit-employee', args=[employee.uidb64()]), 302, 200)
        self.assertTemplateNotUsed(response, 'edit_employee.html')
        #try guessing random stuff
        response = self.client.get(reverse('surveys-edit-employee', args=["isthisanemployee"]), follow=True, secure=True)
        self.assertRedirects(response, reverse('loginc')+"?next="+reverse('surveys-edit-employee', args=["isthisanemployee"]), 302, 200)
        self.assertTemplateNotUsed(response, 'edit_employee.html')

        #test that we get the correct page when we log in and GET this page
        self.client.force_login(user=user)
        response = self.client.get(reverse('surveys-edit-employee', args=[employee.uidb64()]), follow=True, secure=True)
        self.assertTemplateUsed(response, 'edit_employee.html')
        self.assertEqual(response.status_code, 200)

        #test that the correct context is served
        self.assertIn('submit_button_text', response.context)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], EditRespondentForm)
        self.assertFalse(response.context['form'].is_bound)
        for field in response.context['form'].fields:
            self.assertFalse(response.context['form'].has_error(field))
        self.assertEqual(employee.email, response.context['form']['email'].initial)
        self.assertEqual(employee.first_name, response.context['form']['first_name'].initial)
        self.assertEqual(employee.last_name, response.context['form']['last_name'].initial)

        #test that we DONT get the correct page when we log inwith the wrong user and GET this page
        self.client.logout()
        bad_user = User(username="bad_user@tt.tt", email="bad_user@tt.tt", password="password")
        bad_user.save()
        self.client.force_login(user=bad_user)
        response = self.client.get(reverse('surveys-edit-employee', args=[employee.uidb64()]), follow=True, secure=True)
        self.assertTemplateNotUsed(response, 'edit_employee.html')
        self.assertEqual(response.status_code, 403)
        #self.assertTemplateUsed(response, '403.html')# -> dont think these templates are used when debugging is true
        self.client.logout()

        #test that we get the correct page when we POST to this page
        self.client.force_login(user=user)
        valid_employee_data = {'email': "new_email_adress@tt.tt", 'first_name': "Adeed", 'last_name': "A. Name",}
        response = self.client.post(reverse('surveys-edit-employee', args=[employee.uidb64()]), valid_employee_data, follow=True, secure=True)
        self.assertTemplateUsed(response, 'add_or_remove_employees.html')
        self.assertRedirects(response, reverse('surveys-add-or-remove-employees'), 302, 200)
        #test that the respondent was updated
        employee = Respondent.objects.get(id=1)
        self.assertEqual(employee.email, valid_employee_data['email'])
        self.assertEqual(employee.first_name, valid_employee_data['first_name'])
        self.assertEqual(employee.last_name, valid_employee_data['last_name'])

    def test_delete_employee_view(self):
        user = User.objects.get(id=1)
        organization = Organization.objects.get(id=1)
        employee = Respondent.objects.get(id=1)

        organization.update_stripe_subscription_quantity()
        self.assertEqual(len(Respondent.objects.all()), organization.stripe_subscription_quantity)

        #test that login is required
        self.assertEqual(len(Respondent.objects.all()), 1)
        response = self.client.get(reverse('surveys-delete-employee', args=[employee.uidb64()]), follow=True, secure=True)
        self.assertRedirects(response, reverse('loginc')+"?next="+reverse('surveys-delete-employee', args=[employee.uidb64()]), 302, 200)

        #test that another user cannot delete your employees
        bad_user = User(username="bad_user@tt.tt", email="bad_user@tt.tt", password="password")
        bad_user.save()
        self.client.force_login(user=bad_user)
        response = self.client.get(reverse('surveys-delete-employee', args=[employee.uidb64()]), follow=True, secure=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(Respondent.objects.all()), 1)

        #login with proper user
        self.client.logout()
        self.client.force_login(user=user)

        #try a faulty link -> trigger DjangoUnicodeDecodeError
        response = self.client.get(reverse('surveys-delete-employee', args=['42']), follow=True, secure=True)
        self.assertEqual(response.status_code, 404)

        #Actually delete the employee
        response = self.client.get(reverse('surveys-delete-employee', args=[employee.uidb64()]), follow=True, secure=True)
        self.assertRedirects(response, reverse('surveys-add-or-remove-employees'), 302, 200)
        self.assertTemplateUsed(response, 'add_or_remove_employees.html')
        self.assertEqual(len(Respondent.objects.all()), 0)
        self.assertIn("testrespondent@tt.tt was permanently deleted, and will not receive future surveys.", response.content.decode())

        #check that stripe subscription quantity was updated
        organization = Organization.objects.get(id=1)
        self.assertEqual(len(Respondent.objects.all()), organization.stripe_subscription_quantity)

        #do it again to trigger DoesNotExist
        response = self.client.get(reverse('surveys-delete-employee', args=[employee.uidb64()]), follow=True, secure=True)
        self.assertEqual(response.status_code, 404)

    '''
    def test_dashboard_view(self):
        user = User.objects.get(id=1)
        organization = Organization.objects.get(id=1)
        employee = Respondent.objects.get(id=1)
        instrument = Instrument.objects.get(id=1)
        #survey_instance = SurveyInstance.objects.get(id=1)
        survey = Survey.objects.get(id=1)

        #test that login is required
        self.assertEqual(len(Respondent.objects.all()), 1)
        response = self.client.get(reverse('surveys-dashboard'), follow=True, secure=True)
        self.assertRedirects(response, reverse('loginc')+"?next="+reverse('surveys-dashboard'), 302, 200)

        #test that we can see the dashboard
        self.client.force_login(user=user)
        response = self.client.get(reverse('surveys-dashboard'), follow=True, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        #test if we get the correct context
        self.assertEqual(response.context['todays_date'], datetime.date.today())
        self.assertEqual(response.context['employee_count'], 1)
        self.assertEqual(len(response.context['employee_list']), 1)
        self.assertEqual(response.context['employee_list'][0], employee)
        self.assertEqual(response.context['stripe_subscription'], None)
        self.assertEqual(response.context['inactive_instrument_list'], [])
        self.assertEqual(response.context['active_instrument_data'][0]['instrument'], instrument)
        self.assertEqual(response.context['active_instrument_data'][0]['closed_surveys'], None)
        self.assertEqual(response.context['active_instrument_data'][0]['open_survey'], survey)

        #Test if we can get some content in inactive instrument_list
        survey_setting = survey_logic.configure_survey_setting(
            organization=organization,
            instrument=instrument,
            is_active=False
        )
        response = self.client.get(reverse('surveys-dashboard'), follow=True, secure=True)
        self.assertEqual(response.context['inactive_instrument_list'], [instrument])
        self.assertEqual(response.context['active_instrument_data'], None)
