from django.urls import path
from .views import home_page, job_detail, profile, admin, get_ai, upload

urlpatterns = [
    path('', home_page, name='home'),
    path('jobs/<str:job_id>/', job_detail, name='job_detail'),  # Job detail page
    path('profile/', profile, name='profile'),
    path('admin/', admin, name='admin'),
    path("ai/", get_ai, name="ai"),
    path("upload/", upload, name="upload"),
]