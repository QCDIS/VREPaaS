from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from assignments.models import AsgProfile, Assignment, File
from workflows.models import Workflow
from workflows.serializers import WorkflowSerializer
from virtual_labs.models import VirtualLab
from students.models import Student

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

class VirtualLabSerializer(serializers.ModelSerializer):

    endpoint = serializers.SerializerMethodField()

    def get_endpoint(self, vlab):
        return f"https://{vlab.fqdn}:{vlab.ingress_ssl_port}/{vlab.base_url}/"

    class Meta:
        model = VirtualLab
        fields = (
            'title',
            'slug',
            'description',
            'endpoint'
        )



class AssignmentSerializer(serializers.ModelSerializer):

    vlab = VirtualLabSerializer(many=False)

    class Meta:
        model = Assignment
        fields = (
            'title',
            'slug',
            'short_description',
            'vlab'
            
        )

class StudentSerializer(serializers.ModelSerializer):


    class Meta:
        model = Student
        fields = (
            'created',
            'keycloak_ID',
            'name',
            'slug',
            'assignments_enrolled',
            
        )

class FileSerializer(serializers.ModelSerializer):


    class Meta:
        model = File
        fields = (
            'file',
        )



class AssignmentDetailSerializer(serializers.ModelSerializer):

    vlab = VirtualLabSerializer(many=False)
    enrolled_students = StudentSerializer(many=True)
    files = FileSerializer(many=True)
    class Meta:
        model = Assignment
        fields = (
            'title',
            'slug',
            'short_description',
            'long_description',
            'vlab',
            'enrolled_students',
            'files'
        )


