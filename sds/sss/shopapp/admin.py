from django.contrib import admin

# Register your models here.
from .models import Employee, Role, Camera, EmployeeLoginLog
from django.contrib import admin
from .models import Role, Employee, Camera, EmployeeLoginLog

from django.contrib import admin
from .models import Role
# from sss.urls import admin_site  # Импортируем ваш admin_site
#
# # Удалите все @admin.register и используйте только ваш admin_site
# admin_site.register(Role)

#admin.site.register(Employee)
from django.contrib import admin
from .models import Camera, Employee, Role, EmployeeLoginLog
from django_otp.admin import OTPAdminSite
from .models import Role, Employee, Camera, EmployeeLoginLog
# Создаём экземпляр кастомной админки (как в urls.py)
admin_site = OTPAdminSite(name='OTPAdmin')



admin_site.register(Role)
# admin.site.register(SlopeCondition)
# admin.site.register(Notification)
admin_site.register(Camera)
from django.contrib import admin
from .models import Camera, Notification


# class CameraAdmin(admin.ModelAdmin):
#     def save_model(self, request, obj, form, change):
#         try:
#             if obj.condition == "ограниченный доступ":
#                 if not obj.slope_state:
#                     raise ValueError("Тип ограничения обязателен для состояния 'ограниченный доступ'.")
#                 if obj.slope_state == "по знаку" and not obj.sign_image:
#                     raise ValueError("Изображение знака обязательно при выборе 'по знаку'.")
#                 elif obj.slope_state == "по сетке" and obj.sign_image:
#                     raise ValueError("Изображение знака не требуется при выборе 'по сетке'.")
#             elif obj.slope_state:
#                 raise ValueError("Тип ограничения не требуется для этого состояния.")
#             elif obj.sign_image:
#                 raise ValueError("Изображение знака не требуется для этого состояния.")
#         except ValueError as e:
#             form.add_error(None, str(e))
#             return
#         super().save_model(request, obj, form, change)
#
#     class Media:
#         js = ('js/admin_dynamic_fields.js',)  # Подключаем кастомный JavaScript
# admin.py
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Employee
import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from django.contrib import admin
from .models import Employee
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Employee
import secrets
import string
from django.core.mail import send_mail
from django.conf import settings




class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('login', 'email', 'role')  # Можно добавить ФИО позже
    exclude = ('password',)

    def get_fields(self, request, obj=None):
        fields = ['login', 'email', 'role']
        if not obj:  # Только при создании
            fields.extend(['last_name', 'first_name', 'middle_name'])
        return fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Только при создании
            # Генерация пароля (как было раньше)
            chars = string.ascii_letters + string.digits
            raw_password = ''.join(secrets.choice(chars) for _ in range(12))
            obj.password = make_password(raw_password)

            # Отправка письма (как было раньше)
            try:
                send_mail(
                    'Ваши учетные данные',
                    f'Логин: {obj.login}\nПароль: {raw_password}',
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"Ошибка отправки: {e}")  # Логируем ошибку, но не падаем

        super().save_model(request, obj, form, change)

admin_site.register(Employee, EmployeeAdmin)


from django.utils import timezone



class EmployeeLoginLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'formatted_login_time', 'formatted_logout_time', 'ip_address')
    list_filter = ('employee', 'login_time')
    search_fields = ('employee__login', 'ip_address')
    readonly_fields = ('employee', 'login_time', 'logout_time', 'ip_address')

    def formatted_login_time(self, obj):
        return timezone.localtime(obj.login_time).strftime('%d %B %Y, %H:%M')
    formatted_login_time.short_description = 'Время входа'

    def formatted_logout_time(self, obj):
        if obj.logout_time:
            return timezone.localtime(obj.logout_time).strftime('%d %B %Y, %H:%M')
        return ""
    formatted_logout_time.short_description = 'Время выхода'

    def has_add_permission(self, request):
        return False  # Запрещаем ручное добавление записей

    def has_change_permission(self, request, obj=None):
        return False  # Запрещаем редактирование записей

    def has_delete_permission(self, request, obj=None):
        return False  # Запрещаем удаление записей




admin_site.register(EmployeeLoginLog, EmployeeLoginLogAdmin)

class NotificationAdmin(admin.ModelAdmin):



    def has_add_permission(self, request):
        return False  # Запрещаем ручное добавление записей

    def has_change_permission(self, request, obj=None):
        return False  # Запрещаем редактирование записей

    def has_delete_permission(self, request, obj=None):
        return False  # Запрещаем удаление записей

admin_site.register(Notification,NotificationAdmin)