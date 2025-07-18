from django.urls import path
from . import views


from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

    #path('operator/', views.operator_view, name='operator'),
    path('spasatel/', views.spasatel_view, name='spasatel'), # Добавьте эту строку
    path('logout/', views.logout_view, name='logout'),
    path('api/receive_notification/', views.receive_notification, name='receive_notification'),
    path('test-notification/', views.view_notifications, name='test_notification'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path

