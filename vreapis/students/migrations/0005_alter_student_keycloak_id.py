# Generated by Django 4.0.10 on 2023-09-09 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_alter_student_keycloak_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='keycloak_ID',
            field=models.CharField(max_length=100),
        ),
    ]