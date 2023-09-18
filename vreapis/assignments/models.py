from pyexpat import model
from django.db import models
from django.contrib.auth.models import User


class AsgProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    display_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)


    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "Asg Profile"
        verbose_name_plural = "Asg Profiles"

class Assignment(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=True, unique=True)
    short_description = models.CharField(max_length=1000)
    long_description = models.CharField(max_length=10000, null=True)
    vlab = models.ForeignKey('virtual_labs.VirtualLab', on_delete=models.CASCADE, null=True)
    enrolled_students = models.ManyToManyField('students.Student',null=True,blank=True)
  
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Assignment"


class TokenCredentials(models.Model):
    CHOICES_CREDENTIALS_TYPE = (
        ('gh', 'Github Repository'),
        ('we', 'Workflow Engine')
    )

    created = models.DateTimeField(auto_now_add=True, null=True)
    name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=2, choices=CHOICES_CREDENTIALS_TYPE, null=True)
    url = models.URLField(null=True)
    token = models.CharField(max_length=100, null=True)
    Asgab = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING, null=True)


class KeyCloakAuth(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    issuer = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    client_secret = models.CharField(max_length=100)
    realm_name = models.CharField(max_length=100)

    def __str__(self):
        return self.issuer

    class Meta:
        verbose_name = "KeyCloak Auth"
