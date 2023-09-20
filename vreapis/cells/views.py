from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from vreapis.views import GetSerializerMixin

from . import models, serializers


class CellsViewSet(GetSerializerMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Cell.objects.all()
    serializer_class = serializers.CellSerializer
    serializer_action_classes = {
        'list': serializers.CellSerializer
    }

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request)
