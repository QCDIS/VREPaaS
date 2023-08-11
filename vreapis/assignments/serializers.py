from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from assignments.models import AssignmentProfile, Assignments


class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = [
            'username'
        ]


class AssignmentsSerializer(serializers.ModelSerializer):

    endpoint = serializers.SerializerMethodField()

    def get_endpoint(self, assignment):
        return f"https://{assignments.fqdn}:{assignment.ingress_ssl_port}/{assignment.base_url}/"

    class Meta:
        model = Assignments
        fields = (
            'title',
            'slug',
            'description',
            'endpoint'
        )


class AssignmentDetailSerializer(serializers.ModelSerializer):

    endpoint = serializers.SerializerMethodField()

    def get_endpoint(self, vlab):
        return f"https://{vlab.fqdn}:{vlab.ingress_ssl_port}/{vlab.base_url}/" #?

    class Meta:
        model = Assignments
        extra_field_kwargs = {'url': {'lookup_field': 'slug'}}
        fields = (
            'title',
            'slug',
            'description',
            'endpoint'
        )
