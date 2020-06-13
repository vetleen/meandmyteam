from django.db import models
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User



from website.models import Organization


# Create your models here.
class Respondent(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, help_text='Organization where this Respondent is employed')
    first_name = models.CharField(max_length=255, blank=True, null=True, help_text='First name of Employee')
    email = models.EmailField(max_length=254, help_text='Email of Respondent')
    last_name = models.CharField(max_length=255, blank=True, null=True, help_text='Last name of Respondent')
    receives_surveys = models.BooleanField(default=True, help_text='This Respondent should receive surveys from the Organization')

    def uidb64(self):
        return urlsafe_base64_encode(force_bytes(self.pk))

    def __str__(self):
        """String for representing the Respondent object (in Admin site etc.)."""
        return self.email
