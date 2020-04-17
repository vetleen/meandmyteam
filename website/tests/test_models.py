import datetime

from django.test import TestCase
from website.models import Plan, Subscriber
from django.contrib.auth.models import User

# Create your tests here.
class PlanModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods

        Plan.objects.create(
            name='Plan A',
            description ='A basic plan.',
            monthly_price = '20.00',
            yearly_price = '200.00',
            is_paid = "y"
            )
        Plan.objects.create(
            name='Plan B',
            description ='A basic plan B.',
            monthly_price = '30.00',
            yearly_price = '300.00',
            is_paid = "y"
            )
    def test_plans_exist(self):
        plan = Plan.objects.get(id=1)
        self.assertIsInstance(plan, Plan)

    def test_plans_can_be_retrieved(self):
        plan = Plan.objects.get(id=1)
        self.assertEquals(plan.name, 'Plan A')
        self.assertEquals(plan.description, 'A basic plan.')
        self.assertEquals(plan.monthly_price, 20.00)
        self.assertEquals(plan.yearly_price, 200.00)

    def test_plans_have_str_name(self):
        plan = Plan.objects.get(id=1)
        expected_object_name = f'{plan.name}'
        self.assertEquals(expected_object_name, str(plan))

    def test_how_many_plans(self):
        plans=Plan.objects.all()
        self.assertEqual(plans.count(), 2)

class SubscriberModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(
            username='nils@rema.no',
            password='donaldduck')

        Plan.objects.create(
            name='Free',
            description ='A free plan.',
            monthly_price = '0.00',
            yearly_price = '0.00',
            is_paid = "n"
            )
        Subscriber.objects.create(
            #sets up Nils with a free plan
            user=User.objects.get(pk=1),
            plan=Plan.objects.get(pk=1)
            )
        User.objects.create(
            username='karl@rrconsult.no',
            password='NEINEINEINEI')

        Plan.objects.create(
            name='Paid',
            description ='A paid plan.',
            monthly_price = '9.00',
            yearly_price = '99.00',
            is_paid = "y"
            )
        today=datetime.date.today()
        one_month_from_now=today+datetime.timedelta(30)
        #print('today is %s, and in one moth it will be %s'%(today, one_month_from_now))
        Subscriber.objects.create(
            #sets up Karl with a paid plan
            user=User.objects.get(pk=2),
            plan=Plan.objects.get(pk=2),
            date_current_plan_expires=one_month_from_now,
            payment_interval="m"

            )
        User.objects.create(
            username='egon@ob.no',
            password='detvarnoeannet')

        today=datetime.date.today()
        one_month_ago=today-datetime.timedelta(30)
        #print('today is %s, and one month ago it was %s'%(today, one_month_ago))
        Subscriber.objects.create(
            #sets up Karl with a paid plan
            user=User.objects.get(pk=3),
            plan=Plan.objects.get(pk=2),
            date_current_plan_expires=one_month_ago,
            payment_interval="m"

            )
    def test_set_up_worked(self):
        user = User.objects.get(id=1)
        self.assertIsInstance(user, User)
        subscriber = Subscriber.objects.get(id=1)
        self.assertIsInstance(subscriber, Subscriber)
        plan = subscriber.plan
        self.assertIsInstance(plan, Plan)

    def test_can_get_subscriber_from_user(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.subscriber.plan.name, "Free")
        self.assertEqual(user.subscriber.date_current_plan_expires, datetime.date.today())

    def test_can_get_user_from_subscriber(self):
        subscriber = Subscriber.objects.get(id=2) #karl
        self.assertEqual(subscriber.user.username, "karl@rrconsult.no")
        self.assertEqual(subscriber.plan.name, "Paid")
        self.assertEqual(subscriber.date_current_plan_expires, datetime.date.today()+datetime.timedelta(30))
        self.assertEqual(subscriber.payment_interval, "m")
        self.assertTrue(subscriber.is_active())
        #print()
        #print(user.subscriber.payment_interval)
    def test_is_active(self):
        subscribern = Subscriber.objects.get(id=1) #nils
        subscriberk = Subscriber.objects.get(id=2) #karl
        subscribere = Subscriber.objects.get(id=3) #egon
        self.assertFalse(subscribern.is_active())
        self.assertTrue(subscriberk.is_active())
        self.assertFalse(subscribere.is_active())
        #delete Karl's plan
        plan=Plan.objects.get(pk=2)
        plan.delete()
        #update instance
        subscriberk = Subscriber.objects.get(id=2) #karl
        #Assert that he is no longer active, now that he has no plan
        self.assertFalse(subscriberk.is_active())















#
