# Generated by Django 4.0.10 on 2023-09-14 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_remove_student_assignments_enrolled_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='assignments_enrolled',
        ),
    ]
