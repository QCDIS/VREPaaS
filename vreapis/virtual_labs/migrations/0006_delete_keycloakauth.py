# Generated by Django 4.2.7 on 2023-11-30 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('virtual_labs', '0005_virtuallabinstance'),
    ]

    operations = [
        migrations.DeleteModel(
            name='KeyCloakAuth',
        ),
    ]
