from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect

#from django.db import RelatedObjectDoesNotExist

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from surveys.models import Product, Organization, Employee, ProductSetting, SurveyInstance, Survey, Question, Answer, IntAnswer, TextAnswer
from surveys.forms import CreateOrganizationForm, AddEmployeeForm, EditEmployeeForm, ConfigureEmployeeSatisfactionTrackingForm, AnswerQuestionsForm

from datetime import date, datetime
import math

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from surveys.functions import configure_product
from payments.utils.stripe_logic import retrieve_stripe_subscription
# Create your views here.

@login_required
def dashboard_view(request):
    """View function for the dashboard"""
    try:
        employee_list = request.user.organization.employee_set.all()
        employee_count = employee_list.count()
        #print(employee_count)
    except Organization.DoesNotExist:
        employee_list = []
        employee_count = 0

    #get the organization's surveys, sorted by closing date
    try:
        surveys_raw = Survey.objects.filter(product__name='Employee Satisfaction Tracking', owner=request.user.organization).order_by('-date_close') #the first item is the latest survey

        #if any are not closed yet, remove it from the list, and add a note to show the user the closing date
        surveys = [s for s in surveys_raw if s.date_close < date.today()]
        next_survey_close=None
        if len(surveys_raw) > len(surveys):
            surplus_survey=surveys_raw[0]
            next_survey_close=surplus_survey.date_close
    except Organization.DoesNotExist:
        surveys = ()
        next_survey_close = None

    #get the subscription and pass that in in there
    s = None
    if request.user.subscriber.stripe_subscription_id is not None:
        s = retrieve_stripe_subscription(request.user.subscriber.stripe_subscription_id)

    #get the latest completed survey results
    survey_results = () #empty list to be passed to context if 0 surveys
    latest_survey = None
    #number_of_respondents = 0 #make in case it's not set later
    if len(surveys) > 0: #if, however, there are more than 0 surveys, we want to grab the latest and get the results to display
        latest_survey = surveys[0]

        ##get score per category
        #get all answers in latest survey
        answers = IntAnswer.objects.filter(survey_instance__survey=latest_survey) #for now, all answers are IntAnswers

        #get and average out role clarity:
        try:
            role_clarity_answers = [a for a in answers if a.question.dimension == 'role']
            role_clarity_total = 0
            for a in role_clarity_answers:
                role_clarity_total += a.value
            role_clarity_avg = role_clarity_total / len(role_clarity_answers)
            role_clarity_prog = (role_clarity_avg/5*100)
            #number_of_respondents = int(len(role_clarity_answers)/5)
        except ZeroDivisionError:
            role_clarity_avg = None
            role_clarity_prog = None

        #get and average out control:
        try:
            control_answers = [a for a in answers if a.question.dimension == 'control']
            control_total = 0
            for a in control_answers:
                control_total += a.value
            control_avg = control_total / len(control_answers)
            control_prog = (control_avg/5*100)
        except ZeroDivisionError:
            control_avg = None
            control_prog = None

        #get and average out demands:
        try:
            demands_answers = [a for a in answers if a.question.dimension == 'demands']
            demands_total = 0
            for a in demands_answers:
                demands_total += a.value
            demands_avg = demands_total / len(demands_answers)
            #flip it around, since the statements are negative
            demands_avg=((abs((demands_avg-1)-4))+1)
            demands_prog = (demands_avg/5*100)
        except ZeroDivisionError:
            demands_avg = None
            demands_prog = None

        #get and average out relationships:
        try:
            relationships_answers = [a for a in answers if a.question.dimension == 'relationships']
            relationships_total = 0
            for a in relationships_answers:
                relationships_total += a.value
            relationships_avg = relationships_total / len(relationships_answers)
            #flip it around, since the statements are negative
            relationships_avg=((abs((relationships_avg-1)-4))+1)
            relationships_prog = (relationships_avg/5*100)
        except ZeroDivisionError:
            relationships_avg = None
            relationships_prog = None

        #get and average out peer_support:
        try:
            peer_support_answers = [a for a in answers if a.question.dimension == 'peer support']
            peer_support_total = 0
            for a in peer_support_answers:
                peer_support_total += a.value
            peer_support_avg = peer_support_total / len(peer_support_answers)
            peer_support_prog = (peer_support_avg/5*100)
        except ZeroDivisionError:
            peer_support_avg = None
            peer_support_prog = None

        #get and average out manager_support:
        try:
            manager_support_answers = [a for a in answers if a.question.dimension == 'manager support']
            manager_support_total = 0
            for a in manager_support_answers:
                manager_support_total += a.value
            manager_support_avg = manager_support_total / len(manager_support_answers)
            manager_support_prog = (manager_support_avg/5*100)
        except ZeroDivisionError:
            manager_support_avg = None
            manager_support_prog = None

        #prepare a filled list to pass to context
        survey_results = (
            {'dimension': 'role', 'name': 'Role clarity', 'score': role_clarity_avg, 'progress': (role_clarity_prog)},
            {'dimension': 'control', 'name': 'Degree of control', 'score': control_avg, 'progress': (control_prog)},
            {'dimension': 'demands', 'name': 'Demanding work', 'score': demands_avg, 'progress': (demands_prog)},
            {'dimension': 'relationships', 'name': 'Workplace relations', 'score': relationships_avg, 'progress': (relationships_prog)},
            {'dimension': 'peer support', 'name': 'Peer support', 'score': peer_support_avg, 'progress': (peer_support_prog)},
            {'dimension': 'manager support', 'name': 'Manager support', 'score': manager_support_avg, 'progress': (manager_support_prog)},
        )

    #count respondents
    number_of_respondents = 0 #make in case it's not set later
    number_of_invited = 0
    if latest_survey is not None:
        #print ('there was a latest_survey')
        sis = SurveyInstance.objects.filter(survey=latest_survey)
        number_of_invited = len(sis)
        #print ('%s was invited to respond'%(len(sis)))
        for si in sis:
            if si.completed:
                number_of_respondents += 1
        #print ('%s responded'%(number_of_respondents))



    #make the est_active variable and correctly set it
    est_active = False
    p = Product.objects.get(name='Employee Satisfaction Tracking')

    try:
        if p in request.user.organization.active_products.all():
            est_active = True
    except Organization.DoesNotExist:
        pass

    #collect all the info that the dashboard needs (and maybe then some?)
    context = {
        'todays_date': date.today(),
        'employee_count': employee_count,
        #'active_products_count': active_products_count,
        'stripe_subscription': s,
        'employee_list': employee_list,
        'est_active': est_active,
        'surveys': surveys,
        'next_survey_close': next_survey_close,
        'survey_results': survey_results,
        'number_of_invited': number_of_invited,
        'number_of_respondents': number_of_respondents,


    }
    return render(request, 'dashboard.html', context)

@login_required
def edit_organization_view(request):
    """View function for creating organizations."""
    #logged in users are redirected
    try:
        existing_organization=Organization.objects.get(owner=request.user)
    except Organization.DoesNotExist:
        existing_organization=None

    if existing_organization is not None:
        data={
            'name':  request.user.organization.name,
            'address_line_1': request.user.organization.address_line_1,
            'address_line_2': request.user.organization.address_line_2,
            'zip_code': request.user.organization.zip_code,
            'city': request.user.organization.city,
            'country': request.user.organization.country,
        }
        form = CreateOrganizationForm(initial=data)
        context = {
            'form': form,
            'submit_button_text': 'Edit organization details',
        }
    else:
        data={
            'name':  None,
            'address_line_1': None,
            'address_line_2': None,
            'zip_code': None,
            'city': None,
            'country': None,
        }
        form = CreateOrganizationForm(initial=data)
        context = {
            'form': form,
            'submit_button_text': 'Save organization details',
        }
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = CreateOrganizationForm(request.POST, user=request.user)
        context.update({'form': form})
        # Check if the form is valid:
        if form.is_valid():
            if existing_organization is not None:
                existing_organization.name = form.cleaned_data['name']
                existing_organization.address_line_1 = form.cleaned_data['address_line_1']
                existing_organization.address_line_2 = form.cleaned_data['address_line_2']
                existing_organization.zip_code = form.cleaned_data['zip_code']
                existing_organization.city = form.cleaned_data['city']
                existing_organization.country = form.cleaned_data['country']
                existing_organization.save()
                messages.success(request, 'Your organization profile was updated!', extra_tags='alert alert-success')
            else:
                o = Organization(
                    owner = request.user,
                    name = form.cleaned_data['name'],
                    address_line_1 = form.cleaned_data['address_line_1'],
                    address_line_2 = form.cleaned_data['address_line_2'],
                    zip_code = form.cleaned_data['zip_code'],
                    city = form.cleaned_data['city'],
                    country = form.cleaned_data['country'],
                    )
                o.save()
                messages.success(request, 'You have set up your organization profile.', extra_tags='alert alert-success')
            return HttpResponseRedirect(reverse('surveys-dashboard'))
    return render(request, 'create_organization.html', context)
### edit_organization view, or maybe in edit account?

### view, edit, add and delete employees
@login_required
def edit_coworker_view(request):
    """View function for adding employees."""
    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        messages.error(request, 'You have to set up your organization before adding coworkers.', extra_tags='alert alert-warning')
        return HttpResponseRedirect(reverse('surveys-create-organization'))
    employee_list = organization.employee_set.all()
    form = AddEmployeeForm
    context = {
        'form': form,
        'submit_button_text': 'Add coworker',
        'employee_list': employee_list,
    }
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = AddEmployeeForm(request.POST)
        context.update({'form': form})
        # Check if the form is valid:
        if form.is_valid():
            e = Employee(
                organization = organization,
                email = form.cleaned_data['email'],
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                receives_surveys = True
            )
            e.save()
            messages.success(request, 'You have added a coworker (%s)! You can continue to add more below.'%(form.cleaned_data['email']), extra_tags='alert alert-success')
            form = AddEmployeeForm
            context.update({'form': form})
    return render(request, 'edit_coworkers.html', context)

@login_required
def edit_individual_coworker_view(request, **kwargs):
    uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64', None)))
    employee = get_object_or_404(Employee, pk=uid)
    if not request.user == employee.organization.owner:
        return HttpResponseForbidden()
    data ={
        'email': employee.email,
        'first_name': employee.first_name,
        'last_name': employee.last_name
    }
    form = EditEmployeeForm(initial=data)
    context = {
        'form': form,
        'submit_button_text': 'Update',
        }
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = EditEmployeeForm(request.POST)
        context.update({'form': form})
        # Check if the form is valid:
        if form.is_valid():
            employee.email = form.cleaned_data['email']
            employee.first_name = form.cleaned_data['first_name']
            employee.last_name = form.cleaned_data['last_name']
            employee.save()
            messages.success(request, 'Co-worker was updated.', extra_tags='alert alert-success')
            return HttpResponseRedirect(request.GET.get('next', reverse('surveys-edit-coworker')))
    return render(request, 'edit_individual_coworker.html', context)

@login_required
def delete_coworker_view(request, **kwargs):
    uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64', None)))
    employee = get_object_or_404(Employee, pk=uid)
    if employee.organization.owner == request.user:
        messages.info(request, '%s was permanently deleted, and will not reveive future surveys.'%(employee.email), extra_tags='alert alert-warning')
        employee.delete()
        return HttpResponseRedirect(request.GET.get('next', reverse('surveys-edit-coworker')))
    else:
        return HttpResponseForbidden()
###logic that actually makes surveys and sends out emails

@login_required
def set_up_employee_satisfaction_tracking(request, **kwargs):
    est = Product.objects.get(name="Employee Satisfaction Tracking")
    apset = request.user.organization.active_products.all()

    #check if the product is currently active
    est_is_active=False
    if est in apset:
        est_is_active=True

    #set default: assume it's not activated yet
    form=ConfigureEmployeeSatisfactionTrackingForm(label_suffix='')
    context = {
        'form': form,
        'submit_button_text': 'Start Employee Satisfaction Tracking',
        'est_is_active': est_is_active,
    }

    #we check if product was ever activated, by looking for an existing config
    ps = ProductSetting.objects.filter(organization=request.user.organization, product=est)
    if ps.count() != 0:
        submit_button_text = 'Update settings'
        ps = configure_product(request.user.organization, est)

        data={
            'is_active':  est_is_active,
            'survey_interval': ps.survey_interval,

        }
        form = ConfigureEmployeeSatisfactionTrackingForm(initial=data, label_suffix='.')
        context.update({
            'form': form,
            'submit_button_text': submit_button_text
        })

    if request.method == 'POST':
        form=ConfigureEmployeeSatisfactionTrackingForm(request.POST, label_suffix='')
        context.update({'form': form})
        if form.is_valid():
            if form.cleaned_data['is_active']==True and est not in apset:
                request.user.organization.active_products.add(est)
            if form.cleaned_data['is_active']==False and est in apset:
                #print("before: %s."%(request.user.organization.active_products.all().count()))
                request.user.organization.active_products.remove(est)
                #print("before: %s."%(request.user.organization.active_products.all().count()))
            ps=configure_product(

                organization = request.user.organization,
                product = est,
                survey_interval = form.cleaned_data['survey_interval'],
                surveys_remain_open_days = 21
            )

            apset = request.user.organization.active_products.all()
            if est in apset:
                messages.success(request, 'Your settings were updated: Employee satisfaction tracking is ON.', extra_tags='alert alert-success')
            else:
                messages.success(request, 'Your settings were updated: Employee satisfaction tracking is OFF.', extra_tags='alert alert-warning')
            return HttpResponseRedirect(reverse('surveys-dashboard'))

    if est not in apset:
        messages.info(request, 'Make sure you tick the box below to activate satisfaction tracking!', extra_tags='alert alert-warning')

    return render(request, 'set_up_product.html', context)

def answer_survey_view(request, **kwargs):
    #instantiate the context right away
    context = {
        'submit_button_text': 'Continue',
    }

    #The URL should be telling us which survey instance user is trying to answer, let's use that to get the survey instance 'si' right away
    #The URL should also have a token, so let's use that to ensure the user actually has the valid link that lets him answer this survey
    try:
        #get the si-id and token from the url, and check that it's format is correct
        token = kwargs.get('token', None)
        token_args = token.split("-")
        assert len(token_args) == 2, "Faulty link (wrong link format)"
        #get the assosciated SI
        si_id = int(force_text(urlsafe_base64_decode(token_args[0])))
        si = get_object_or_404(SurveyInstance, pk=si_id)
        #ensure the token matches the si
        assert si.get_hash_string() == token_args[1], "Faulty link (invalid hash)"
        #ensure the survey that the si belonmgs to is still open
        assert si.survey.date_close >= date.today()
        context.update({'si': si})
    except:
        raise Http404("The survey you asked for does not exist. If you pasted a link, make sure you got the entire link.")

    #this view also takes a page argument that we use for pagination of questions
    page=kwargs.get('page', None)
    context.update({'page': page})

    page_size = 5 #questions per page

    #get the questions in the survey, we are going to use them anyway
    questions = Question.objects.filter(product=si.survey.product).order_by('pk')


    #if it's not paginated, we present the user with the "start survey" help text and button
    if page is None:
        #check of this survey was started before, and if so, find the first unanswered and go there
        alist = IntAnswer.objects.filter(survey_instance=si)
        if len(alist) > 0:
            q_counter = 0
            for q in questions:
                q_counter += 1
                alist = IntAnswer.objects.filter(question=q, survey_instance=si)
                print('%s answers to Question %s.'%(len(alist), q.pk))
                if len(alist) < 1:
                    missing_page = math.ceil((q_counter/page_size))
                    print('going for question %s at page %s'%(q_counter, missing_page))
                    return HttpResponseRedirect(reverse('surveys-answer-survey-pages', args=(token, missing_page)))

    #else, it is a paginated page, and we should probably present some questions
    else:

        #make a list 'qlist' containing exactly the questions the user should be asked
        qlist = []
        last_q_id = int(page)*page_size
        for i, q in enumerate(questions):
            if i < last_q_id and i >= (last_q_id-page_size):
                qlist.append(q)

        #initialize the dict that will contain pre-existing data from the db to fill in the initial values in the form
        data={}
        #get previous answers for the questions in qlist and add them to the dict
        for q in qlist:
            alist = IntAnswer.objects.filter(question=q, survey_instance=si)
            if alist is not None:
                try:
                    data.update({'question_%s'%(q.pk): alist[0].value})
                except IndexError:
                    pass
        #print (data)

        #make a form, with pre-existing data if any
        form=AnswerQuestionsForm(questions=qlist, initial=data)
        #make form available to context
        context.update({'form': form})

        #did the user POST something?
        if request.method == 'POST':
            print('received form')
            #make a fresh form insatnce, and bind it with the posted value
            form=AnswerQuestionsForm(request.POST, questions=qlist)
            context.update({'form': form})

            #deal with data if it's valid
            if form.is_valid():
                print('form is valid')
                for item in form.cleaned_data:
                    # identify the question that has been answered
                    q_id= int(item.replace('question_', ''))
                    q = Question.objects.get(pk=q_id)

                    # find the value that has been provided as the answer
                    value=int(form.cleaned_data[item])

                    # use the answer method of the question to create answer objects for this si
                    q.answer(value=value, survey_instance=si)

                #if there are more questions, send them to the next page
                if len(questions) > int(page)*page_size:
                    return HttpResponseRedirect(reverse('surveys-answer-survey-pages', args=(token, int(page)+1)))
                #else, we are done answering, and redirect to thank you message
                else:
                    print('survey complete?')
                    #compare number of answers to number of questions:
                    answers = IntAnswer.objects.filter(survey_instance=si)
                    print('comparing %s to %s.'%(len(answers), len(questions)))
                    if len(answers) >= len(questions):
                        print('enough answers!')
                        si.completed=True
                        si.save()
                        return HttpResponseRedirect(reverse('surveys-answer-survey', args=(token, )))
                    else:
                        #find first unanswered in questions, calculate wich page that should be on
                        #redirect there instead of page 1.
                        q_counter = 0
                        for q in questions:
                            q_counter += 1
                            alist = IntAnswer.objects.filter(question=q, survey_instance=si)
                            print('%s answers to Question %s.'%(len(alist), q.pk))
                            if len(alist) < 1:
                                missing_page = math.ceil((q_counter/page_size))
                                print('going for question %s at page %s'%(q_counter, missing_page))
                                messages.warning(request, 'There are still %s unanswered questions in this survey. Would you mind going through again and making sure everything got answered?'%(len(questions)-len(answers)), extra_tags='alert alert-warning')
                                return HttpResponseRedirect(reverse('surveys-answer-survey-pages', args=(token, missing_page)))
                        #catchall, should only trigger if code can't find what is unanswered. So never?
                        messages.warning(request, 'Ups. There are still %s unanswered questions. Would you mind going through again and making sure everything got answered?'%(len(questions)-len(answers)), extra_tags='alert alert-warning')
                        return HttpResponseRedirect(reverse('surveys-answer-survey-pages', args=(token, 1)))

    #In case a valid form was not submitted, we present the current form
    return render(request, 'answer_survey.html', context)

@login_required
def co_worker_satisfaction_data_view(request, **kwargs):
    #get the survey with the specified date provided by the url
    date_close=kwargs.get('date_close', None)
    print('got date close from url: %s.'%(date_close))
    date_close = datetime.strptime(date_close, "%Y-%m-%d").date()
    print('turned it into: %s.'%(date_close))

    #get the organization's surveys, sorted by closing date, and only the ones up until the date specified in the url
    surveys = Survey.objects.filter(
        product__name='Employee Satisfaction Tracking',
        owner=request.user.organization,
        date_close__lte=date_close
    ).order_by('date_close') #the last item is the requested survey (with the should_be_impossible_exception that more surveys end this date)
    print ('Found %s closed surveys'%(len(surveys)))

    #turn queryset into list, and remove any surveys that are not closed yet
    surveys = [s for s in surveys if s.date_close < date.today()]

    #get the last closed survey and bind to variable, if any
    if len(surveys) > 0:
        this_survey = surveys.pop()
    else:
        this_survey = None
    print ('This survey is: %s'%(this_survey))
    #get the second last survey and bind to variable, if any
    if len(surveys) > 0:
        previous_survey = surveys.pop()
    else:
        previous_survey = None
    print ('Previous survey is: %s'%(previous_survey))
    ##get score per category
    #get all answers in latest survey
    survey_results = () #empty list if there is no latest survey
    #set the number of respondents-variables in case they are not set later
    number_of_respondents = 0
    number_of_respondents_previous = 0

    #make sure we have these variables to pass to view, even if they somehow don't get set later
    lowest_score = (None, 5)
    highest_score = (None, 0)

    if this_survey is not None:
        answers = IntAnswer.objects.filter(survey_instance__survey=this_survey) #for now, all answers are IntAnswers
        print('found %s answers for this survey'%(len(answers)))

        #get and average out role clarity:
        role_clarity_avg = 0
        try:
            print("trying to retrieve answers for role clarity and average them")
            role_clarity_answers = [a for a in answers if a.question.dimension == 'role']
            role_clarity_total = 0
            for a in role_clarity_answers:
                role_clarity_total += a.value
            role_clarity_avg = role_clarity_total / len(role_clarity_answers)
            #number_of_respondents = int((len(role_clarity_answers)/5)) #for now all questions must be answered, so one is a good indication of all

        except ZeroDivisionError:
            pass #print('Got a divide by Zero error, because there are no answers in this category ')

        #get and average out control:
        control_avg = 0
        try:
            control_answers = [a for a in answers if a.question.dimension == 'control']
            control_total = 0
            for a in control_answers:
                control_total += a.value
            control_avg = control_total / len(control_answers)

        except ZeroDivisionError:
            pass #print('Got a divide by Zero error, because there are no answers in this category ')

        #get and average out demands:
        demands_avg = 0
        try:
            demands_answers = [a for a in answers if a.question.dimension == 'demands']
            demands_total = 0
            for a in demands_answers:
                demands_total += a.value
            demands_avg = demands_total / len(demands_answers)
            #flip it, because statements are negative
            demands_avg = ((abs((demands_avg-1)-4))+1)
        except ZeroDivisionError:
            pass #print('Got a divide by Zero error, because there are no answers in this category ')

        #get and average out relationships:
        relationships_avg = 0
        try:
            relationships_answers = [a for a in answers if a.question.dimension == 'relationships']
            relationships_total = 0
            for a in relationships_answers:
                relationships_total += a.value
            relationships_avg = relationships_total / len(relationships_answers)
            #flip it, because statements are negative
            relationships_avg = ((abs((relationships_avg-1)-4))+1)
        except ZeroDivisionError:
            pass #print('Got a divide by Zero error, because there are no answers in this category ')

        #get and average out peer_support:
        peer_support_avg = 0
        try:
            peer_support_answers = [a for a in answers if a.question.dimension == 'peer support']
            peer_support_total = 0
            for a in peer_support_answers:
                peer_support_total += a.value
            peer_support_avg = peer_support_total / len(peer_support_answers)
        except ZeroDivisionError:
            pass #print('Got a divide by Zero error, because there are no answers in this category ')

        #get and average out manager_support:
        manager_support_avg = 0
        try:
            manager_support_answers = [a for a in answers if a.question.dimension == 'manager support']
            manager_support_total = 0
            for a in manager_support_answers:
                manager_support_total += a.value
            manager_support_avg = manager_support_total / len(manager_support_answers)
        except ZeroDivisionError:
            pass #print('Got a divide by Zero error, because there are no answers in this category ')

        survey_results = (
            {
                'dimension': 'role',
                'description': 'Role clarity is the degree to which co-workers\' in your organization feels that it is clearly understood what is expected of them, and what their job entails.',
                'name': 'Role clarity',
                'score': role_clarity_avg,
                'progress': (role_clarity_avg/5*100),
            },
            {
                'dimension': 'control',
                'description': 'Degree of control is the degree to which co-workers\' in your organization feels that they themselves have autonomy, meaning that they have control over what they do at work.',
                'name': 'Degree of control',
                'score': control_avg,
                'progress': (control_avg/5*100),
            },
            {
                'dimension': 'demands',
                'description': 'Demanding work is a score for how demanding your co-workers feel work is. For simplicity sake, we have processed the data in such a way that a high score is good and a low score bad. This way you can compare this dimension to the others.',
                'name': 'Demanding work',
                'score': demands_avg,
                'progress': (demands_avg/5*100),
            },
            {
                'dimension': 'relationships',
                'description': 'Workplace relationships is a score for how good relations between co-workers are. A low score may indicate workplace bullying, harassment or high levels of conflict.',
                'name': 'Workplace relations',
                'score': relationships_avg,
                'progress': (relationships_avg/5*100),
            },
            {
                'dimension': 'peer support',
                'description': 'Peer support indicates the extent to which your co-workers feel they can rely on their co-workers to support them in execution of tasks.',
                'name': 'Peer support',
                'score': peer_support_avg,
                'progress': (peer_support_avg/5*100),
            },
            {
                'dimension': 'manager support',
                'description': 'Manager support indicates the extent to which your co-workers feel they can rely on their manager(s) for support in execution of tasks.',
                'name': 'Manager support',
                'score': manager_support_avg,
                'progress': (manager_support_avg/5*100),
            },
        )

        #if there was a previous survey, let's grab that data and add to our context as well:
        if previous_survey is not None:

            panswers = IntAnswer.objects.filter(survey_instance__survey=previous_survey) #for now, all answers are IntAnswers

            #get and average out role clarity:
            #also decide the size of the bars to display
            prole_clarity_avg = 0
            try:
                print('Trying to get role clarity averaghe for PREVIOUS survey')
                role_clarity_answers = [a for a in panswers if a.question.dimension == 'role']
                role_clarity_total = 0
                for a in role_clarity_answers:
                    role_clarity_total += a.value
                prole_clarity_avg = role_clarity_total / len(role_clarity_answers)
                #The blue bar should be equal to the smallest of the two results
                blue_bar = (prole_clarity_avg/5*100)
                if role_clarity_avg < prole_clarity_avg:
                    blue_bar = (role_clarity_avg/5*100)

                #the red bar should be equal to any negative change
                red_bar = (0/5*100)
                if role_clarity_avg < prole_clarity_avg:
                    red_bar = ((prole_clarity_avg-role_clarity_avg)/5*100)
                #the green bar should be equal to any postive change
                green_bar = (0/5*100)
                if role_clarity_avg > prole_clarity_avg:
                    green_bar = ((role_clarity_avg-prole_clarity_avg)/5*100)

                number_of_respondents_previous = int((len(role_clarity_answers)/5)) #for now all questions must be answered, so one is a good indication of all

            except ZeroDivisionError:
                pass #print('Got a divide by Zero error, because there are no answers in this category ')
                blue_bar = 0
                red_bar = 0
                green_bar = 0

            finally:
                survey_results[0].update ({

                        'previous_score': prole_clarity_avg,
                        'previous_progress': (prole_clarity_avg/5*100),
                        'delta':  (role_clarity_avg-prole_clarity_avg),
                        'blue_bar': blue_bar,
                        'red_bar': red_bar,
                        'green_bar': green_bar,
                   })


            #get and average out control:
            pcontrol_avg = 0
            try:
                control_answers = [a for a in panswers if a.question.dimension == 'control']
                control_total = 0
                for a in control_answers:
                    control_total += a.value
                pcontrol_avg = control_total / len(control_answers)
                #The blue bar should be equal to the smallest of the two results
                blue_bar = (pcontrol_avg/5*100)
                if control_avg < pcontrol_avg:
                    blue_bar = (control_avg/5*100)

                #the red bar should be equal to any negative change
                red_bar = (0/5*100)
                if control_avg < pcontrol_avg:
                    red_bar = ((pcontrol_avg-control_avg)/5*100)
                #the green bar should be equal to any postive change
                green_bar = (0/5*100)
                if control_avg > pcontrol_avg:
                    green_bar = ((control_avg-pcontrol_avg)/5*100)

            except ZeroDivisionError:
                pass #print('Got a divide by Zero error, because there are no answers in this category ')
                blue_bar = 0
                red_bar = 0
                green_bar = 0

            finally:
                survey_results[1].update ({

                        'previous_score': pcontrol_avg,
                        'previous_progress': (pcontrol_avg/5*100),
                        'delta':  (control_avg-pcontrol_avg),
                        'blue_bar': blue_bar,
                        'red_bar': red_bar,
                        'green_bar': green_bar,
                   })

            #get and average out demands:
            pdemands_avg = 0
            try:
                demands_answers = [a for a in panswers if a.question.dimension == 'demands']
                demands_total = 0
                for a in demands_answers:
                    demands_total += a.value
                pdemands_avg = demands_total / len(demands_answers)

                #flip it around, since the statements are negative
                pdemands_avg=((abs((pdemands_avg-1)-4))+1)
                #The blue bar should be equal to the smallest of the two results
                blue_bar = (pdemands_avg/5*100)
                if demands_avg < pdemands_avg:
                    blue_bar = (demands_avg/5*100)

                #the red bar should be equal to any negative change
                red_bar = (0/5*100)
                if demands_avg < pdemands_avg:
                    red_bar = ((pdemands_avg-demands_avg)/5*100)
                #the green bar should be equal to any postive change
                green_bar = (0/5*100)
                if demands_avg > pdemands_avg:
                    green_bar = ((demands_avg-pdemands_avg)/5*100)

            except ZeroDivisionError:
                pass #print('Got a divide by Zero error, because there are no answers in this category ')
                blue_bar = 0
                red_bar = 0
                green_bar = 0

            finally:
                survey_results[2].update ({

                        'previous_score': pdemands_avg,
                        'previous_progress': (pdemands_avg/5*100),
                        'delta':  (demands_avg-pdemands_avg),
                        'blue_bar': blue_bar,
                        'red_bar': red_bar,
                        'green_bar': green_bar,
                   })

            #get and average out relationships:
            prelationships_avg = 0
            try:
                relationships_answers = [a for a in panswers if a.question.dimension == 'relationships']
                relationships_total = 0
                for a in relationships_answers:
                    relationships_total += a.value
                prelationships_avg = relationships_total / len(relationships_answers)
                #flip it around, since the statements are negative
                prelationships_avg=((abs((prelationships_avg-1)-4))+1)
                #The blue bar should be equal to the smallest of the two results
                blue_bar = (prelationships_avg/5*100)
                if relationships_avg < prelationships_avg:
                    blue_bar = (relationships_avg/5*100)

                #the red bar should be equal to any negative change
                red_bar = (0/5*100)
                if relationships_avg < prelationships_avg:
                    red_bar = ((prelationships_avg-relationships_avg)/5*100)
                #the green bar should be equal to any postive change
                green_bar = (0/5*100)
                if relationships_avg > prelationships_avg:
                    green_bar = ((relationships_avg-prelationships_avg)/5*100)

            except ZeroDivisionError:
                pass #print('Got a divide by Zero error, because there are no answers in this category ')
                blue_bar = 0
                red_bar = 0
                green_bar = 0

            finally:
                survey_results[3].update ({

                        'previous_score': prelationships_avg,
                        'previous_progress': (prelationships_avg/5*100),
                        'delta':  (relationships_avg-prelationships_avg),
                        'blue_bar': blue_bar,
                        'red_bar': red_bar,
                        'green_bar': green_bar,
                   })

            #get and average out peer_support:
            ppeer_support_avg = 0
            try:
                peer_support_answers = [a for a in panswers if a.question.dimension == 'peer support']
                peer_support_total = 0
                for a in peer_support_answers:
                    peer_support_total += a.value
                ppeer_support_avg = peer_support_total / len(peer_support_answers)
                #The blue bar should be equal to the smallest of the two results
                blue_bar = (ppeer_support_avg/5*100)
                if peer_support_avg < ppeer_support_avg:
                    blue_bar = (peer_support_avg/5*100)

                #the red bar should be equal to any negative change
                red_bar = (0/5*100)
                if peer_support_avg < ppeer_support_avg:
                    red_bar = ((ppeer_support_avg-peer_support_avg)/5*100)
                #the green bar should be equal to any postive change
                green_bar = (0/5*100)
                if peer_support_avg > ppeer_support_avg:
                    green_bar = ((peer_support_avg-ppeer_support_avg)/5*100)

            except ZeroDivisionError:
                pass #print('Got a divide by Zero error, because there are no answers in this category ')
                blue_bar = 0
                red_bar = 0
                green_bar = 0

            finally:
                survey_results[4].update ({

                        'previous_score': ppeer_support_avg,
                        'previous_progress': (ppeer_support_avg/5*100),
                        'delta':  (peer_support_avg-ppeer_support_avg),
                        'blue_bar': blue_bar,
                        'red_bar': red_bar,
                        'green_bar': green_bar,
                   })

            #get and average out manager_support:
            pmanager_support_avg = 0
            try:
                manager_support_answers = [a for a in panswers if a.question.dimension == 'manager support']
                manager_support_total = 0
                for a in manager_support_answers:
                    manager_support_total += a.value
                pmanager_support_avg = manager_support_total / len(manager_support_answers)
                #The blue bar should be equal to the smallest of the two results
                blue_bar = (pmanager_support_avg/5*100)
                if manager_support_avg < pmanager_support_avg:
                    blue_bar = (manager_support_avg/5*100)

                #the red bar should be equal to any negative change
                red_bar = (0/5*100)
                if manager_support_avg < pmanager_support_avg:
                    red_bar = ((pmanager_support_avg-manager_support_avg)/5*100)
                #the green bar should be equal to any postive change
                green_bar = (0/5*100)
                if manager_support_avg > pmanager_support_avg:
                    green_bar = ((manager_support_avg-pmanager_support_avg)/5*100)

            except ZeroDivisionError:
                pass #print('Got a divide by Zero error, because there are no answers in this category ')
                blue_bar = 0
                red_bar = 0
                green_bar = 0

            finally:
                survey_results[5].update ({

                        'previous_score': pmanager_support_avg,
                        'previous_progress': (pmanager_support_avg/5*100),
                        'delta':  (manager_support_avg-pmanager_support_avg),
                        'blue_bar': blue_bar,
                        'red_bar': red_bar,
                        'green_bar': green_bar,
                   })
            print("comparing: %s, %s..." %(manager_support_avg, pmanager_support_avg))
    #get questions for the product to display under each category
    questions = Question.objects.filter(product__name='Employee Satisfaction Tracking')
    print('found %s questions'%(len(questions)))
    #get all answers for this survey, so we can show scores with the questions
    #find the average score for each, and also calculate the progress bar length to display - pass both into a list questions
    print("are there any answers?")
    if answers:
        print("YES!")
        answers_avgs = []
        for q in questions:
            relevant_answers = [a for a in answers if a.question == q]
            relevant_answers_total = 0
            for a in relevant_answers:
                relevant_answers_total += a.value
            #most dimensions have theur scoire be the average, like this:
            relevant_answers_avg = relevant_answers_total / len(relevant_answers)
            #but when there is a negative statement, we want to flip the score (e.g. a 1.5 avg is a 4.5 score, because that's good):
            if q.dimension == 'demands' or q.dimension == 'relationships':
                relevant_answers_avg = ((abs((relevant_answers_avg-1)-4))+1)
            answers_avgs.append((relevant_answers_avg, ((relevant_answers_avg/5)*100)))

        questions = list(zip(questions, answers_avgs))

    #set highest and lowest scores for view, to be displayed if less than 4 respondent
    #make list of all averages, with proper "key"
    avgs = {'role': role_clarity_avg,
            'control': control_avg,
            'demands': demands_avg,
            'relationships': relationships_avg,
            'peer support': peer_support_avg,
            'manager support': manager_support_avg,
            }
    #find the largest one and smallest and assign to appr. variables
    #print("Higest score: %s, lowest score: %s."%(highest_score, lowest_score))
    for key in avgs:
        #print (key, '->', avgs[key])
        if avgs[key] > highest_score[1]:
            highest_score = (key, avgs[key])
        if avgs[key] < lowest_score[1]:
           lowest_score = (key, avgs[key])

    highest_score = highest_score[0]
    lowest_score = lowest_score[0]

    print("Higest score: %s, lowest score: %s."%(highest_score, lowest_score))

    #count respondents
    number_of_respondents = 0 #make in case it's not set later
    number_of_invited = 0
    print("is there a this_survey?")
    if this_survey:
        print("YES!")

        sis = SurveyInstance.objects.filter(survey=this_survey)
        number_of_invited = len(sis)
        #print ('%s was invited to respond'%(len(sis)))
        for si in sis:
            print("in for loop!")
            if si.completed:
                number_of_respondents += 1
        #print ('%s responded'%(number_of_respondents))

    number_of_respondents_previous = 0 #make in case it's not set later
    number_of_invited_previous = 0
    print("is there a prev_survey?")
    if previous_survey:
        print("YES!")

        sis = SurveyInstance.objects.filter(survey=previous_survey)
        number_of_invited_previous = len(sis)
        #print ('%s was invited to respond'%(len(sis)))
        for si in sis:
            print("in another for loop!")
            if si.completed:
                number_of_respondents_previous += 1
        #print ('%s responded'%(number_of_respondents))
    print("About to make the context var")
    context={
        'survey_results': survey_results,
        'number_of_respondents': number_of_respondents,
        'number_of_respondents_previous': number_of_respondents_previous,
        'number_of_invited': number_of_invited,
        'number_of_invited_previous': number_of_invited_previous,
        'questions': questions,
        'this_survey': this_survey,
        'previous_survey': previous_survey,
        'highest_score': highest_score,
        'lowest_score': lowest_score,
    }
    return render(request, 'co_worker_satisfaction_data.html', context)
