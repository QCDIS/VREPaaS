from django.db import models

# Create your models here.


class PaasConfiguration(models.Model):
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    documentation_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title
