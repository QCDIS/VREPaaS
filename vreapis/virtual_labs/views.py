from rest_framework import views
from rest_framework.response import Response
from virtual_labs.serializers import VirtualLabSerializer
from . import models


class Home(views.APIView):

    keycloak_roles = {
        'GET': ['default-roles-summer-school-22']
    }

    def get(self, request, format=None):

        print(request.roles)
        vlabs = models.VirtualLab.objects.all()
        return Response(VirtualLabSerializer(vlabs, many=True).data)
