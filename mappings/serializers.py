from rest_framework import serializers
from .models import PatientDoctorMapping
class MappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "assigned_at")
        read_only_fields = ("id", "assigned_at")
    def validate_patient(self, patient):
        user = self.context["request"].user
        if not patient or patient.created_by_id != user.id:
            raise serializers.ValidationError("Patient does not exist or is not accessible to you.")
        return patient
    def validate_doctor(self, doctor):
        if not doctor: raise serializers.ValidationError("Doctor does not exist.")
        return doctor
    def validate(self, attrs):
        patient = attrs.get("patient", getattr(self.instance, "patient", None))
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        if patient and doctor and PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exclude(pk=getattr(self.instance,"pk",None)).exists():
            raise serializers.ValidationError("This doctor is already assigned to this patient.")
        return attrs
