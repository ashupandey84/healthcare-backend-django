from django.db import models
from patients.models import Patient
from doctors.models import Doctor
class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="doctor_mappings")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patient_mappings")
    assigned_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=("patient", "doctor"), name="unique_patient_doctor_assignment")]
        ordering = ["-assigned_at"]
