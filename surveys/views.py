from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect

#from django.db import RelatedObjectDoesNotExist

from django.contrib import messages
from django.contrib.auth.decorators import login_required

#from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User

#from django.contrib.auth.tokens import PasswordResetTokenGenerator
#from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
#from django.utils.encoding import force_bytes, force_text


#from payments.utils.stripe_logic import *
from datetime import date, datetime
# Create your views here.

#set up logging
import logging
import datetime
logger = logging.getLogger('__name__')
