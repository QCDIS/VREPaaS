from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from vreapis.views import GetSerializerMixin

from . import serializers
from . import models


class VirtualLabViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    lookup_field = "slug"
    queryset = models.VirtualLab.objects.all()
    serializer_class = serializers.VirtualLabDetailSerializer
    serializer_action_classes = {
        'list': serializers.VirtualLabSerializer
    }

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class VirtualLabInstanceViewSet(
        GetSerializerMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet,
        ):

    model = models.VirtualLabInstance
    queryset = model.objects.all()
    serializer_class = serializers.VirtualLabInstanceSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        vlab_slug = self.request.query_params.get('vlab_slug', None)
        if vlab_slug:
            return self.model.objects.filter(vlab__slug=vlab_slug)
        else:
            return self.model.objects.all()
