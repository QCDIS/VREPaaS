from sys import stdout
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from . import serializers
from . import models
from workflows.models import Workflow
from workflows.serializers import WorkflowSerializer
import requests
from vreapis.views import GetSerializerMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from students.models import Student

class AssignmentViewSet(GetSerializerMixin, viewsets.ModelViewSet):


    lookup_field = "slug"
    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentDetailSerializer
    serializer_action_classes = {
        'list': serializers.AssignmentSerializer
    }

    def update(self, request,slug, *args, **kwargs):
        try:
            obj = models.Assignment.objects.get(slug=slug)
            student = Student.objects.get(keycloak_ID=request.data['student_id'])
            ids = []
            for stud in obj.enrolled_students.all():
                ids.append(stud.slug)
            if request.data['type'] in ['enroll', 'un-enroll']:
                if request.data['student_id'] in ids:
                    obj.enrolled_students.remove(student)
                    return Response('removed')
                obj.enrolled_students.add(student)
                return Response('added')
            else:
                return Response(request.data['student_id'] in ids)
        except: 
            return Response('something went wrong')
    







