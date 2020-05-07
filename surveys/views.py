from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect


from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from surveys.models import Product, Organization, Employee, ProductSetting, SurveyInstance, Survey, Question, Answer, IntAnswer, TextAnswer
from surveys.forms import CreateOrganizationForm, AddEmployeeForm, EditEmployeeForm, ConfigureEmployeeSatisfactionTrackingForm, AnswerQuestionsForm

from datetime import date

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from surveys.functions import configure_product
# Create your views here.

@login_required
def dashboard_view(request):
    """View function for the dashboard"""
    try:
        employee_list = request.user.organization.employee_set.all()
        employee_count = employee_list.count()
        print(employee_count)
    except Organization.DoesNotExist:
        employee_list = []
        employee_count = 0

    #try:
    #    active_products = request.user.organization.active_products.all()
    #    active_products_count =  active_products.count()
    #
    #except Organization.DoesNotExist:
    #    active_products_count = 0

    #see your organization(name, number of employees and so on)
    #See what products are activated, easily get started on them
    #If a product is activated show mini-dashboard with, when was the last survey, when is the next, how many have replied, and how many are waiting to reply
    est_active = False
    p = Product.objects.get(name='Employee Satisfaction Tracking')
    try:
        if p in request.user.organization.active_products.all():
            est_active = True
    except Organization.DoesNotExist:
        pass
    #print('est is active: %s.'%(est_active))
    context = {
        'todays_date': date.today(),
        'employee_count': employee_count,
        #'active_products_count': active_products_count,
        'employee_list': employee_list,
        'est_active': est_active

    }
    return render(request, 'dashboard.html', context)

###get started wizard for product number one (setup-product-name)
# add or confirm your organization
# add employees manually, or email us the list
# set up how often surveys are sent, and the date for the first one

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
        form = CreateOrganizationForm
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
    #print('page (%s) is of type %s'%(page, type(page)))
    #if it's not paginated, we present the user with the "start survey" help text and button

    if page is None:
        pass

    #else, it is a paginated page, and we should probably present some questions
    else:
        #get the questions in the survey, we are going to use them anyway
        questions = Question.objects.filter(product=si.survey.product).order_by('pk')

        #make a list 'qlist' containing exactly the questions the user should be asked
        page_size = 5 #questions per page
        qlist = []
        last_q_id = int(page)*page_size
        for i, q in enumerate(questions):
            if i < last_q_id and i >= (last_q_id-page_size):
                qlist.append(q)
        #initialize the dict that will contain pre-existing data from the db to fill in the initial values in the form
        data={}
        #get previous answers for the questions in qlist and add them to the dict
        for q in qlist:
            #print(q)
            alist = IntAnswer.objects.filter(question=q, survey_instance=si)
            if alist is not None:
                try:
                    #print(alist[0])
                    data.update({'question_%s'%(q.pk): alist[0].value})
                except IndexError:
                    pass
        print (data)

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
                    #print('calling q.answer for question %s, with answer %s, and si %s.'%(q.pk, value, si.pk))

                #if there are more questions, send them to the next page
                print('comparing questions-length, %s, to page x page_size, %s...'%(len(questions), int(page)*page_size))
                if len(questions) > int(page)*page_size:
                    print('redirecting to page number %s.'%(page))
                    return HttpResponseRedirect(reverse('surveys-answer-survey-pages', args=(token, int(page)+1)))
                #else, we are done answering, and redirect to thank you message
                else:
                    print('survey complete')
                    si.completed=True
                    si.save()
                    print(token)
                    return HttpResponseRedirect(reverse('surveys-answer-survey', args=(token, )))

    #In case a valid form was not submitted, we present the current form
    print('default choice')
    print(context)
    return render(request, 'answer_survey.html', context)
