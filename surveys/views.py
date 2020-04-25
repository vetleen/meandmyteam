from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseForbidden



from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from surveys.models import Product, Organization, Employee
from surveys.forms import CreateOrganizationForm, AddEmployeeForm, EditEmployeeForm

from datetime import date
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
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

    try:
        active_products = request.user.organization.active_products.all()
        active_products_count =  active_products.count()

    except Organization.DoesNotExist:
        active_products_count = 0

    #see your organization(name, number of employees and so on)
    #See what products are activated, easily get started on them
    #If a product is activated show mini-dashboard with, when was the last survey, when is the next, how many have replied, and how many are waiting to reply


    context = {
        'todays_date': date.today(),
        'employee_count': employee_count,
        'active_products_count': active_products_count,
        'employee_list': employee_list,

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
