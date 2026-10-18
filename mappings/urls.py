from django.urls import path
from .views import MappingListCreateView, PatientMappingsOrDeleteView
urlpatterns = [path("", MappingListCreateView.as_view(), name="mapping-list"), path("<int:item_id>/", PatientMappingsOrDeleteView.as_view(), name="patient-mappings-or-delete")]
