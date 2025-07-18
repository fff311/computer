from django.contrib.auth.backends import BaseBackend
from .models import Employee
from django.contrib.auth.hashers import check_password

class EmployeeBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            employee = Employee.objects.get(login=username)
            if check_password(password, employee.password):
                return employee
        except Employee.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return None