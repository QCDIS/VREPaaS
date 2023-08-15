from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from assignments.models import VM, SDIAProvision, Topology, AsgProfile, Assignment
from workflows.models import Workflow
from workflows.serializers import WorkflowSerializer


class VMSerializer(serializers.ModelSerializer):

    class Meta:
        model = VM
        fields = (
            'name',
            'role',
            'disk_size',
            'mem_size',
            'num_cores'
        )


class TopologySerializer(serializers.ModelSerializer):

    class Meta:
        model = Topology
        fields = (
            'provider',
            'domain'
        )


class SDIAProvisionSerializer(serializers.ModelSerializer):

    vms = VMSerializer(many=True)
    topology = TopologySerializer()

    class Meta:
        model = SDIAProvision
        fields = (
            'topology',
            'vms'
        )


class AsgProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AsgProfile
        fields = (
            'display_name',
            'description',
            'image'
        )


class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = [
            'username'
        ]


class AssignmentDetailSerializer(serializers.ModelSerializer):

    endpoint = serializers.SerializerMethodField()

    def get_endpoint(self, vlab):
        return f"https://{vlab.fqdn}:{vlab.ingress_ssl_port}/{vlab.base_url}/"

    class Meta:
        model = Assignment
        fields = (
            'title',
            'slug',
            'description',
            'endpoint'
        )


class AssignmentDetailSerializer(serializers.ModelSerializer):

    endpoint = serializers.SerializerMethodField()

    def get_endpoint(self, vlab):
        return f"https://{vlab.fqdn}:{vlab.ingress_ssl_port}/{vlab.base_url}/"

    class Meta:
        model = Assignment
        extra_field_kwargs = {'url': {'lookup_field': 'slug'}}
        fields = (
            'title',
            'slug',
            'description',
            'endpoint'
        )
