from pyexpat import model
from django.db import models
from django.contrib.auth.models import User




class Student(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    keycloak_ID = models.CharField(max_length=100)
    slug = models.SlugField(null=True, unique=True)
    name = models.CharField(null=True, max_length=100)
    # assignments_enrolled = models.CharField(null=True,max_length=10000)

    def __str__(self):
        return self.keycloak_ID

    class Meta:
        verbose_name = "Student"


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
