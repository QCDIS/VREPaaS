# Generated by Django 4.0.5 on 2022-06-07 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtual_labs', '0002_alter_vlprofile_display_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sdiaprovision',
            options={'verbose_name': 'SDIA Provision'},
        ),
        migrations.AddField(
            model_name='sdiaprovision',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
