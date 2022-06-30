# Generated by Django 4.0.5 on 2022-06-29 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('virtual_labs', '0004_remove_virtuallab_profiles_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('argo_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=50, null=True)),
                ('progress', models.CharField(max_length=50, null=True)),
                ('argo_url', models.URLField(null=True)),
                ('vlab', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='virtual_labs.virtuallab')),
            ],
        ),
    ]
