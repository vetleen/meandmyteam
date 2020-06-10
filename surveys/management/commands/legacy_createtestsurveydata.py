from django.core.management.base import BaseCommand, CommandError
from surveys.functions import daily_survey_maintenance
from surveys.models import User, Organization, Survey, SurveyInstance, Question, Answer, Product, Employee, Survey
from website.models import Subscriber
from django.db import IntegrityError
from datetime import date, timedelta
from surveys.functions import configure_product

import random

class Command(BaseCommand):
    help = 'Creates a few surveys and so on so ...'

    def handle(*args, **kwargs):
        orgname="TestOrganization01"
        username="testorg01@aa.aa"
        password="jjj43skjma@67#"

        print('creating test data, Organization and Employees')
        try:
            u = User.objects.create_user(username=username, email=username, password=password)
            u.save()
            o = Organization(owner=u, name=orgname, address_line_1="Calle Espana 345")
            o.save()
            s = Subscriber(user=u)
            s.save()
        except IntegrityError as err:
            print('the user was already created, let\'s retreive it...')
            u=User.objects.get(username=username)
        try:
            o = Organization(owner=u, name=orgname, address_line_1="Calle Espana 345")
            o.save()
        except IntegrityError as err:
            print('the organization was already created, let\'s retreive it...')
            o=Organization.objects.get(owner=u)
        print('moving on with %s and %s...'%(u, o))

        p = Product.objects.get(pk=1)

        o.active_products.add(p)
        o.save()
        es = Employee.objects.filter(organization=o)
        if len(es) < 4:
            try:
                e1=Employee(
                    organization = o,
                    email = 'testrespondent1@aa.aa',
                    receives_surveys = True
                )
                e1.save()
            except IntegrityError as err:
                print('e1 was created before... let\'s retrieve instead...')
                e1= Employee.objects.get(email='testrespondent1@aa.aa')
            try:
                e2=Employee(
                    organization = o,
                    email = 'testrespondent2@aa.aa',
                    receives_surveys = True
                )
                e2.save()
            except IntegrityError as err:
                print('e2 was created before... let\'s retrieve instead...')
                e2= Employee.objects.get(email='testrespondent2@aa.aa')
            try:
                e3=Employee(
                    organization = o,
                    email = 'testrespondent3@aa.aa',
                    receives_surveys = True
                )
                e3.save()
            except IntegrityError as err:
                print('e3 was created before... let\'s retrieve instead...')
                e3= Employee.objects.get(email='testrespondent3@aa.aa')
            try:
                e4=Employee(
                    organization = o,
                    email = 'testrespondent4@aa.aa',
                    receives_surveys = True
                )
                e4.save()
            except IntegrityError as err:
                print('e4 was created before... let\'s retrieve instead...')
                e4= Employee.objects.get(email='testrespondent4@aa.aa')



        print('running daily survey tasks...')
        daily_survey_maintenance()
        print('Done!')

        print('answering survey...')
        es = Employee.objects.filter(organization=o)
        print ('got %s employees that must answer...'%(len(es)))
        for e in es:
            print('%s is answering survey...'%(e))
            sis = SurveyInstance.objects.filter(respondent=e)
            if len(sis) < 1:
                print('Oh no, there was no SurveyInstance for this test user, even if I totally expected there to be!')
                return
            si=sis[0]
            qs = Question.objects.filter(product=si.survey.product).order_by('pk')
            for q in qs:
                #print('answering: %s...'%(q))
                value = random.randint(1, 4)
                q.answer(value=value, survey_instance=si)
                #print('... %s.'%(value))
            si.completed=True
            si.save()
        print('Done!')




        print('Cheating by making that survey look old!')

        #get the survey and change the date close and open
        surveys = Survey.objects.filter(
            product__name='Employee Satisfaction Tracking',
            owner=o
        ).order_by('date_close') #the last item is the last survey
        s = surveys[0]
        s.date_open = s.date_open + timedelta(days=-300)
        s.date_close = s.date_close + timedelta(days=-300)
        s.save()

        #get fresh data to print
        surveys = Survey.objects.filter(
            product__name='Employee Satisfaction Tracking',
            owner=o
        ).order_by('date_close') #the last item is the last survey
        s = surveys[0]
        print('Surveys date_close should be %s.'%(s.date_close))

        #get product settings and update those dates as well
        ps=configure_product(organization=o, product=p)
        last_survey_open = ps.last_survey_open + timedelta(days=-300)
        last_survey_close = ps.last_survey_close + timedelta(days=-300)
        ps=configure_product(organization=o, product=p, last_survey_open=last_survey_open, last_survey_close=last_survey_close)
        ps.save()

        #get fresh data to print
        ps=configure_product(organization=o, product=p)
        print('PS last_survey_close should be %s.'%(ps.last_survey_close))

        print('Done!')

        #check how many survey instances exist
        ss = Survey.objects.filter(owner=o)
        print('before second daily_SM-step there are %s surveys.'%(len(ss)))





        print('running daily survey tasks...')
        daily_survey_maintenance()
        print('Done!')
        #check how many survey instances exist
        ss = Survey.objects.filter(owner=o)
        print('after second daily_SM-step there are %s surveys.'%(len(ss)))

        '''
        print('answering survey...')
        es = Employee.objects.filter(organization=o)
        print ('got %s employees that must answer...'%(len(es)))
        for e in es:
            print('%s is answering survey...'%(e))
            sis = SurveyInstance.objects.filter(respondent=e)
            print('found %s SIs, expected 2'%(len(sis)))
            if len(sis) < 1:
                print('Oh no, there was no SurveyInstance for this test user, even if I totally expected there to be!')
                return
            si=sis[1]
            qs = Question.objects.filter(product=si.survey.product).order_by('pk')
            for q in qs:
                #print('answering: %s...'%(q))
                value = random.randint(2, 5)
                q.answer(value=value, survey_instance=si)
                #print('... %s.'%(value))
            si.completed=True
            si.save()
        print('Done!')
        '''
        print('Cheating by making that survey look old!')

        #get the survey and change the date close and open
        surveys = Survey.objects.filter(
            product__name='Employee Satisfaction Tracking',
            owner=o
        ).order_by('date_close') #the last item is the last survey
        s = surveys[1]
        s.date_open = s.date_open + timedelta(days=-100)
        s.date_close = s.date_close + timedelta(days=-100)
        s.save()

        #get fresh data to print
        surveys = Survey.objects.filter(
            product__name='Employee Satisfaction Tracking',
            owner=o
        ).order_by('date_close') #the last item is the last survey
        s = surveys[0]
        print('Surveys date_close should be %s.'%(s.date_close))

        #get product settings and update those dates as well
        ps=configure_product(organization=o, product=p)
        last_survey_open = ps.last_survey_open + timedelta(days=-100)
        last_survey_close = ps.last_survey_close + timedelta(days=-100)
        ps=configure_product(organization=o, product=p, last_survey_open=last_survey_open, last_survey_close=last_survey_close)
        ps.save()

        #get fresh data to print
        ps=configure_product(organization=o, product=p)
        print('PS last_survey_close should be %s.'%(ps.last_survey_close))

        print('Done!')
