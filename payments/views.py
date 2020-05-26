from django.shortcuts import render

# Create your views here.
def resources(request):
    """View function for ..."""

    context = {
        'foo': 'bar'
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'resources.html', context=context)
