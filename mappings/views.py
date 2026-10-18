from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import MappingSerializer
class MappingListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = PatientDoctorMapping.objects.filter(patient__created_by=request.user).select_related("patient", "doctor")
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        return paginator.get_paginated_response(MappingSerializer(page, many=True).data)
    def post(self, request):
        serializer = MappingSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class PatientMappingsOrDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, item_id):
        patient = get_object_or_404(Patient, pk=item_id, created_by=request.user)
        qs = PatientDoctorMapping.objects.filter(patient=patient).select_related("patient", "doctor")
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        return paginator.get_paginated_response(MappingSerializer(page, many=True).data)
    def delete(self, request, item_id):
        mapping = get_object_or_404(PatientDoctorMapping, pk=item_id, patient__created_by=request.user)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
