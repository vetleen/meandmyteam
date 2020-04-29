from django.test import TestCase, SimpleTestCase

from django.contrib.auth.models import AnonymousUser, User
from django.contrib import auth
from surveys.functions import make_surveys_for_active_products, make_survey_instances_for_active_surveys, send_out_survey_instance_emails, configure_product, create_survey
from surveys.models import Organization, Employee, Survey, SurveyInstance, IntAnswer, TextAnswer, Question, Product, ProductSetting

from datetime import date, timedelta

def yellow(message):
    ''' A custom function that sets strings meant for the consoll to yellow so that they stand out'''
    return '\n' + '\033[1;33;40m ' + message + '\x1b[0m'


class MinorFunctionsTest(TestCase):
    ''' TESTS FUNCTIONS IN FUNCTIONS.PY '''
    def setUp(self):
        u = User(username="testuser", password="insecure123")
        o = Organization(owner=u, name="TestOrga1", surveys_remain_open_days = 21)
        p=Product(name="Product Name")
        p.save()
        u.save()
        o.save()

    def test_function_configure_product(self):
        o=Organization.objects.get(pk=1)
        p=Product.objects.get(pk=1)
        self.assertEqual(ProductSetting.objects.all().count(), 0)

        #test that a ProductSetting is produced as expected
        configure_product(o, p)
        self.assertEqual(ProductSetting.objects.all().count(), 1)

        #test that it wont make more if called again
        configure_product(o, p)
        self.assertEqual(ProductSetting.objects.all().count(), 1)

        #test that default values are set:
        ps = configure_product(o, p)
        self.assertEqual(ps.is_active, True)
        self.assertEqual(ps.survey_interval, 90)
        self.assertEqual(ps.last_survey_open, None)
        self.assertEqual(ps.last_survey_close, None)

        #test if we can change the default values
        ps = configure_product(organization=o, product=p, is_active=False)
        self.assertEqual(ps.is_active, False)
        ps = configure_product(organization=o, product=p, survey_interval=75)
        self.assertEqual(ps.survey_interval, 75)
        ps = configure_product(organization=o, product=p, last_survey_open=date.today())
        self.assertEqual(ps.last_survey_open, date.today())
        ps = configure_product(organization=o, product=p, last_survey_close=date.today()+timedelta(days=-14))
        self.assertEqual(ps.last_survey_close, date.today()+timedelta(days=-14))

    def test_function_create_survey(self):
        o=Organization.objects.get(pk=1)
        p=Product.objects.get(pk=1)
        #check that no surveys exist as per now
        self.assertEqual(Survey.objects.all().count(), 0)
        #chech that we can make one
        create_survey(o, p)
        self.assertEqual(Survey.objects.all().count(), 1)
        #chech default values
        s=Survey.objects.get(pk=1)
        self.assertEqual(s.product, p)
        self.assertEqual(s.owner, o)
        self.assertEqual(s.date_open, date.today())
        self.assertEqual(s.date_close, s.date_open + timedelta(days=o.surveys_remain_open_days))

class TestFunction_make_surveys_for_active_products_base(TestCase):
    '''  '''
    def setUp(self):
        u = User(username="testuser", password="insecure123")
        o = Organization(owner=u, name="TestOrga1", surveys_remain_open_days = 21)
        u.save()
        o.save()
        p=Product(name="Product One")
        p.save()
        p2=Product(name="Product Two ")
        p2.save()
    def test_no_survey_made_when_no_act_product(self):
        u=User.objects.get(pk=1)
        o=Organization.objects.get(pk=1)
        #test that it does not make surveys when no active products AND that it works at all
        self.assertEqual(Survey.objects.all().count(), 0)
        make_surveys_for_active_products(o)
        self.assertEqual(Survey.objects.all().count(), 0)

    def test_survey_made_when_active_product(self):
        u=User.objects.get(pk=1)
        o=Organization.objects.get(pk=1)
        p=Product.objects.get(pk=1)
        o.active_products.add(p)
        o.save()
        #check that number of surveys go from 0 to 1 when calling the function with active products
        self.assertEqual(Survey.objects.all().count(), 0)
        make_surveys_for_active_products(o)
        self.assertEqual(Survey.objects.all().count(), 1)
        #check that it doesn't happen again
        self.assertEqual(Survey.objects.all().count(), 1)
        make_surveys_for_active_products(o)
        self.assertEqual(Survey.objects.all().count(), 1)
        #check that if there are surveys, but it's still time to make new ones, that they are made
        ps = configure_product(
        organization=o,
        product=p,
        last_survey_open=date.today()+timedelta(days=-140),
        last_survey_close=date.today()+timedelta(days=-120)
        )
        self.assertEqual(Survey.objects.all().count(), 1)
        make_surveys_for_active_products(o)
        self.assertEqual(Survey.objects.all().count(), 2)
        #check that last_dates were updated, and settings for product
        s=Survey.objects.get(pk=2)
        ps = configure_product(o, p)
        self.assertEqual(s.date_open, ps.last_survey_open)
        self.assertEqual(s.date_close, ps.last_survey_close)
        self.assertEqual(s.date_open, date.today())
        self.assertEqual(s.date_close, s.date_open + timedelta(days=s.owner.surveys_remain_open_days))
        #check that the rest of the survey was made right
        self.assertEqual(s.owner, o)
        self.assertEqual(s.product, p)
        ## What happens if more active products?
        p2 = Product.objects.get(pk=2)
        o.active_products.add(p2)
        o.save()
        #check that we add a Survey only to the new active product
        ss = Survey.objects.filter(product=p2)
        self.assertEqual(ss.count(), 0)
        ss = Survey.objects.filter(product=p)
        self.assertEqual(ss.count(), 2)
        self.assertEqual(Survey.objects.all().count(), 2)
        make_surveys_for_active_products(o)
        self.assertEqual(Survey.objects.all().count(), 3)
        ss = Survey.objects.filter(product=p2)
        self.assertEqual(ss.count(), 1)
        ss = Survey.objects.filter(product=p)
        self.assertEqual(ss.count(), 2)
        #check that it doesnt add another if we run it again
        make_surveys_for_active_products(o)
        ss = Survey.objects.filter(product=p2)
        self.assertEqual(ss.count(), 1)
        ss = Survey.objects.filter(product=p)
        self.assertEqual(ss.count(), 2)

class TestFunctionmake_survey_instances_for_active_surveys(TestCase):
    def setUp(self):
        #org with surveys that are active and inactive, employees to add
        u = User(username="testuser", password="insecure123")
        o = Organization(owner=u, name="TestOrga1", surveys_remain_open_days = 21)
        p=Product(name="Product Name")
        u.save()
        o.save()
        p.save()
        s1 = Survey(
            product = p,
            owner = o,
            date_open =  date.today() + timedelta(days=-25),
            date_close  =  date.today() + timedelta(days=-4)
        )
        s2 = Survey(
            product = p,
            owner = o,
            date_open =  date.today() + timedelta(days=-5),
            date_close  =  date.today() + timedelta(days=16)
        )
        s1.save()
        s2.save()
        e1=Employee(
            organization = o,
            email = 'e1@aa.aa',
            receives_surveys = True
        )
        e2=Employee(
            organization = o,
            email = 'e2@aa.aa',
            receives_surveys = False
        )
        e3=Employee(
            organization = o,
            email = 'e3@aa.aa'
        )
        e1.save()
        e2.save()
        e3.save()

    def test_survey_instance_creation(self):

        #test
        o=Organization.objects.get(pk=1)
        #check that the expected amount of survey instances present along the way
        #start with 0
        sis = SurveyInstance.objects.filter(survey__owner=o)
        self.assertEqual(sis.count(), 0)
        #make one for each of the TWO active employees
        make_survey_instances_for_active_surveys(o)
        sis = SurveyInstance.objects.filter(survey__owner=o)
            #print(SurveyInstance.objects.all().count())
        self.assertEqual(sis.count(), 2)
        #make sure that it only happens once
        make_survey_instances_for_active_surveys(o)
        sis = SurveyInstance.objects.filter(survey__owner=o)
        self.assertEqual(sis.count(), 2)
        #a new employee is added to the mix
        e4=Employee(
            organization = o,
            email = 'e4@aa.aa'
        )
        e4.save()
        #Check that exactly one new survey instance is made
        make_survey_instances_for_active_surveys(o)
        sis = SurveyInstance.objects.filter(survey__owner=o)
        self.assertEqual(sis.count(), 3)

class TestFunctionmake_send_out_survey_instance_emails(TestCase):
    def setUp(self):
        #org with surveys that are active and inactive, employees to add
        u = User(username="testuser", password="insecure123")
        o = Organization(owner=u, name="TestOrga1", surveys_remain_open_days = 21)
        p=Product(name="Product Name")
        u.save()
        o.save()
        p.save()
        s1 = Survey(
            product = p,
            owner = o,
            date_open =  date.today() + timedelta(days=-25),
            date_close  =  date.today() + timedelta(days=-4)
        )
        s2 = Survey(
            product = p,
            owner = o,
            date_open =  date.today() + timedelta(days=-5),
            date_close  =  date.today() + timedelta(days=16)
        )
        s1.save()
        s2.save()
        e1=Employee(
            organization = o,
            email = 'e1@aa.aa',
            receives_surveys = True
        )
        e2=Employee(
            organization = o,
            email = 'e2@aa.aa',
            receives_surveys = False
        )
        e3=Employee(
            organization = o,
            email = 'e3@aa.aa'
        )
        e1.save()
        e2.save()
        e3.save()
    def test_survey_instance_emailing(self):
        o = Organization.objects.get(pk=1)
        make_survey_instances_for_active_surveys(o)
        sis = SurveyInstance.objects.filter(survey__owner=o)
        #one active survey, 2 active amployees = 2
        self.assertEqual(sis.count(), 2)
        #since none of these has been sent out, we excpect both to be
        #we can first check that they don't have a sen intital-tag or last-updated-date
        for si in sis:
            self.assertEqual(si.sent_initial, False)
            self.assertEqual(si.last_reminder, None)
        #after running test-fucntion both survey insatnces are sent
        send_out_survey_instance_emails(o)
        sis = SurveyInstance.objects.filter(survey__owner=o)
        for si in sis:
            self.assertEqual(si.sent_initial, True)
            self.assertEqual(si.last_reminder, date.today())

        #let's say all of this happened in the past for one si
        si = SurveyInstance.objects.get(pk=1)
        si.last_reminder = date.today() + timedelta(days=-9)
        si.save()
        #we expect that a reminder must be sent
        self.assertEqual(si.last_reminder, date.today() + timedelta(days=-9))
        send_out_survey_instance_emails(o)
        si = SurveyInstance.objects.get(pk=1)
        self.assertEqual(si.last_reminder, date.today())
