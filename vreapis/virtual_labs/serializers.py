from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.contrib.auth.models import User
from virtual_labs.models import VM, SDIAProvision, Topology, VLProfile, VirtualLab, Workflow


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


class VLProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VLProfile
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


class WorkflowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workflow


class VirtualLabSerializer(serializers.ModelSerializer):

    endpoint = serializers.SerializerMethodField()

    def get_endpoint(self, vlab):
        return f"https://{vlab.fqdn}:{vlab.ingress_ssl_port}/{vlab.base_url}"

    class Meta:
        model = VirtualLab
        fields = (
            'title',
            'slug',
            'description',
            'endpoint'
        )


class VirtualLabDetailSerializer(serializers.ModelSerializer):

    endpoint = serializers.SerializerMethodField()

    def get_endpoint(self, vlab):
        return f"https://{vlab.fqdn}:{vlab.ingress_ssl_port}/{vlab.base_url}"

    class Meta:
        model = VirtualLab
        extra_field_kwargs = {'url': {'lookup_field': 'slug'}}
        fields = (
            'title',
            'slug',
            'description',
            'endpoint'
        )
