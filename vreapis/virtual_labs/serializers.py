from dataclasses import fields
from rest_framework import serializers

from virtual_labs.models import VM, SDIAProvision, Topology, VLProfile, VirtualLab


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


class VirtualLabSerializer(serializers.ModelSerializer):

    provision = SDIAProvisionSerializer()

    class Meta:

        model = VirtualLab
        fields = (
            'title',
            'description',
            'provision'
        )