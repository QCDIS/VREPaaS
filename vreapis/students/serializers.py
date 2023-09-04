from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from students.models import Student





class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = [
            'username'
        ]

class StudentSerializer(serializers.ModelSerializer):


    class Meta:
        model = Student
        fields = (
            'created',
            'keycloak_ID',
            'name',
            'assignments_enrolled',
            
        )



