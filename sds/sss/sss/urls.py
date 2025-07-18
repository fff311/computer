"""
URL configuration for sss project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path, include
# from two_factor.urls import urlpatterns as tf_urls
#
# urlpatterns = [
#     path('', include(tf_urls)),  # подключаем список путей из two_factor.urls
#     path('admin/', admin.site.urls),
#     path('shopapp/', include('shopapp.urls')),
# ]
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django_otp.admin import OTPAdminSite
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice

from django.urls import path, include
from shopapp.admin import admin_site  # Импортируем из admin.py

from django.contrib.auth.views import redirect_to_login
# from django.urls import path, include
# from shopapp.admin import admin_site  # Убедитесь, что импортируете ваш admin_site
#
# urlpatterns = [
#     path('admin/', admin_site.urls),
#     path('shopapp/', include('shopapp.urls')),
# ]
from django.contrib import admin
import random
import string

from django.urls import path, include
from django.views.generic.base import RedirectView
from shopapp.admin import admin_site  # ваш кастомный админ

def generate_random_path(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Генерируем случайный путь для админки
ADMIN_PATH = f'admin-{generate_random_path()}/'

urlpatterns = [
    path('', RedirectView.as_view(url='/' + ADMIN_PATH, permanent=False)),
    path(ADMIN_PATH, admin_site.urls),
    path('shopapp/', include('shopapp.urls')),
]
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic.base import RedirectView
from shopapp.admin import admin_site
import random
import string
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)