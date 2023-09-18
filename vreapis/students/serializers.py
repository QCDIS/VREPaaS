from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from students.models import Student
from assignments.serializers import AssignmentSerializer




class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = [
            'username'
        ]

class StudentSerializer(serializers.ModelSerializer):
    # assignments = serializers.SerializerMethodField()

    # def get_assignments(self, obj):
    #     return AssignmentSerializer(obj.assignment_set, many=True)

    class Meta:
        model = Student
        fields = (
            'created',
            'keycloak_ID',
            'name',
            'slug',
            # 'assignments'
        )



