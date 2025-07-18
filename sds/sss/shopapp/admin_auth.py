from django.contrib.auth.views import LoginView
from django.urls import path

urlpatterns = [
    path('', LoginView.as_view(template_name='admin/login.html')),
]
