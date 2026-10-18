from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Doctor
from .serializers import DoctorSerializer
class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    queryset = Doctor.objects.all()
    def perform_create(self, serializer): serializer.save(created_by=self.request.user)
    def perform_update(self, serializer):
        if self.get_object().created_by_id != self.request.user.id: raise PermissionDenied("Only the doctor record's creator may update it.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id: raise PermissionDenied("Only the doctor record's creator may delete it.")
        instance.delete()
