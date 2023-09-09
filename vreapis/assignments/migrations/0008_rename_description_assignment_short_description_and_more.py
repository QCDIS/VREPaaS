# Generated by Django 4.0.10 on 2023-09-09 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('virtual_labs', '0004_remove_virtuallab_profiles_and_more'),
        ('assignments', '0007_assignment_long_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignment',
            old_name='description',
            new_name='short_description',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='base_url',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='fqdn',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='ingress_ssl_port',
        ),
        migrations.AddField(
            model_name='assignment',
            name='vlab',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='virtual_labs.virtuallab'),
        ),
    ]