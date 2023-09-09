from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from assignments.models import AsgProfile, Assignment
from workflows.models import Workflow
from workflows.serializers import WorkflowSerializer



class AsgProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AsgProfile
        fields = (
            'display_name',
            'description',
        )


class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = [
            'username'
        ]

class AssignmentSerializer(serializers.ModelSerializer):


    class Meta:
        model = Assignment
        fields = (
            'title',
            'slug',
            'short_description',
            'vlab'
            
        )


class AssignmentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = (
            'title',
            'slug',
            'short_description',
            'long_description',
            'vlab'
        )


