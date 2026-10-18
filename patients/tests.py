from rest_framework.test import APITestCase
from django.urls import resolve
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
User = get_user_model()
class HealthcareAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="a@example.com", name="A User", password="SafePass123!abc")
        self.other = User.objects.create_user(email="b@example.com", name="B User", password="SafePass123!abc")
        self.client.force_authenticate(self.user)
    def test_protected_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get("/api/patients/").status_code, 401)
        self.assertEqual(self.client.get("/api/doctors/").status_code, 401)
        self.assertEqual(self.client.get("/api/mappings/").status_code, 401)
    def test_registration_and_duplicate(self):
        url="/api/auth/register/"
        data={"name":"New User","email":"new@example.com","password":"StrongPassword123!"}
        self.assertEqual(self.client.post(url,data).status_code,201)
        self.assertEqual(self.client.post(url,data).status_code,400)
        self.assertNotIn("password",self.client.post(url,{**data,"email":"third@example.com"}).data)
    def test_login_success_and_failure(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post("/api/auth/login/",{"email":"a@example.com","password":"SafePass123!abc"}).status_code,200)
        self.assertEqual(self.client.post("/api/auth/login/",{"email":"a@example.com","password":"wrong"}).status_code,401)
    def test_patient_isolation_crud_and_owner_protection(self):
        data={"name":"Patient","date_of_birth":"1990-01-01","gender":"female","created_by":self.other.id}
        response=self.client.post("/api/patients/",data)
        self.assertEqual(response.status_code,201)
        patient=Patient.objects.get(pk=response.data["id"])
        self.assertEqual(patient.created_by,self.user)
        self.assertEqual(self.client.get("/api/patients/").data["count"],1)
        self.assertEqual(self.client.get(f"/api/patients/{patient.id}/").status_code,200)
        updated = self.client.put(f"/api/patients/{patient.id}/", {**data, "name":"Updated", "created_by":self.other.id})
        self.assertEqual(updated.status_code,200)
        patient.refresh_from_db()
        self.assertEqual(patient.created_by,self.user)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/patients/{patient.id}/").status_code,404)
        self.assertEqual(self.client.put(f"/api/patients/{patient.id}/",data).status_code,404)
        self.assertEqual(self.client.delete(f"/api/patients/{patient.id}/").status_code,404)
    def test_doctor_crud_and_ownership(self):
        data={"name":"Dr One","specialization":"Cardiology","email":"dr@example.com","phone":"123"}
        created=self.client.post("/api/doctors/",data)
        self.assertEqual(created.status_code,201)
        doctor=Doctor.objects.get(pk=created.data["id"])
        self.assertEqual(self.client.get("/api/doctors/").status_code,200)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/doctors/{doctor.id}/").status_code,200)
        self.assertEqual(self.client.put(f"/api/doctors/{doctor.id}/",data).status_code,403)
        self.assertEqual(self.client.delete(f"/api/doctors/{doctor.id}/").status_code,403)
        self.client.force_authenticate(self.user)
        updated=self.client.put(f"/api/doctors/{doctor.id}/",{**data,"name":"Dr Updated","created_by":self.other.id})
        self.assertEqual(updated.status_code,200)
        doctor.refresh_from_db()
        self.assertEqual(doctor.created_by,self.user)
        self.assertEqual(self.client.delete(f"/api/doctors/{doctor.id}/").status_code,204)
    def test_mapping_create_list_patient_retrieval_delete_and_rejections(self):
        patient=Patient.objects.create(name="P",date_of_birth="1990-01-01",gender="other",created_by=self.user)
        doctor=Doctor.objects.create(name="D",specialization="General",email="d@example.com",phone="123",created_by=self.other)
        data={"patient":patient.id,"doctor":doctor.id}
        created=self.client.post("/api/mappings/",data)
        self.assertEqual(created.status_code,201)
        self.assertEqual(self.client.post("/api/mappings/",data).status_code,400)
        self.assertEqual(self.client.get("/api/mappings/").data["count"],1)
        self.assertEqual(self.client.get(f"/api/mappings/{patient.id}/").data["count"],1)
        self.assertEqual(self.client.post("/api/mappings/",{"patient":patient.id,"doctor":doctor.id}).status_code,400)
        other_patient=Patient.objects.create(name="Other P",date_of_birth="1990-01-01",gender="other",created_by=self.other)
        self.assertEqual(self.client.post("/api/mappings/",{"patient":other_patient.id,"doctor":doctor.id}).status_code,400)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(f"/api/mappings/{created.data['id']}/").status_code,404)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f"/api/mappings/{created.data['id']}/").status_code,204)
        self.assertEqual(self.client.post("/api/mappings/",{"patient":99999,"doctor":doctor.id}).status_code,400)
        self.assertEqual(self.client.post("/api/mappings/",{"patient":patient.id,"doctor":99999}).status_code,400)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/mappings/{patient.id}/").status_code,404)


    def test_jwt_login_issues_usable_access_token(self):
        self.client.force_authenticate(user=None)
        response=self.client.post("/api/auth/login/",{"email":"a@example.com","password":"SafePass123!abc"})
        self.assertEqual(response.status_code,200)
        self.assertIn("access",response.data)
        self.assertIn("refresh",response.data)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        self.assertEqual(self.client.get("/api/doctors/").status_code,200)

    def test_owner_can_delete_patient_and_unauthenticated_detail_is_rejected(self):
        patient=Patient.objects.create(name="Owned",date_of_birth="1990-01-01",gender="other",created_by=self.user)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(f"/api/patients/{patient.id}/").status_code,401)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f"/api/patients/{patient.id}/").status_code,204)

    def test_root_returns_service_info(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "message": "Healthcare Backend API is running",
            "status": "success",
            "endpoints": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "patients": "/api/patients/",
                "doctors": "/api/doctors/",
                "mappings": "/api/mappings/",
                "admin": "/admin/",
            },
        })

    def test_documented_api_paths_resolve_for_expected_methods(self):
        routes = [
            ("POST", "/api/auth/register/"), ("POST", "/api/auth/login/"),
            ("POST", "/api/patients/"), ("GET", "/api/patients/"),
            ("GET", "/api/patients/1/"), ("PUT", "/api/patients/1/"), ("DELETE", "/api/patients/1/"),
            ("POST", "/api/doctors/"), ("GET", "/api/doctors/"),
            ("GET", "/api/doctors/1/"), ("PUT", "/api/doctors/1/"), ("DELETE", "/api/doctors/1/"),
            ("POST", "/api/mappings/"), ("GET", "/api/mappings/"),
            ("GET", "/api/mappings/1/"), ("DELETE", "/api/mappings/1/"),
        ]
        for method, url in routes:
            with self.subTest(method=method, url=url):
                callback = resolve(url).func
                if hasattr(callback, "actions"):
                    self.assertIn(method.lower(), callback.actions)
                else:
                    self.assertTrue(callable(getattr(callback.view_class, method.lower(), None)))
