from django.db import models

# Create your models here.


class PaasConfiguration(models.Model):
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    documentation_url = models.URLField(null=True, blank=True)
    site_icon = models.TextField(
        null=True,
        help_text=("Base 64-encoded image, eg. data:image/png;base64,"
                  "ZXhhbXBsZQo="),
        )

    def __str__(self):
        return self.title
