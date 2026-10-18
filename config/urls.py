from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView


def api_root(request):
    return JsonResponse({
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


urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/patients/", include("patients.urls")),
    path("api/doctors/", include("doctors.urls")),
    path("api/mappings/", include("mappings.urls")),
]
