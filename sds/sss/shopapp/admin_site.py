from django_otp.admin import OTPAdminSite
from django.contrib.auth.models import User, Group
from django_otp.plugins.otp_totp.models import TOTPDevice

class OTPAdmin(OTPAdminSite):
    pass

admin_site = OTPAdmin(name='OTPAdmin')
admin_site.register(User)
admin_site.register(Group)
admin_site.register(TOTPDevice)