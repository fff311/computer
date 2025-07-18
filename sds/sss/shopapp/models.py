from django.db import models

from django.contrib.auth.hashers import make_password, check_password
class Role(models.Model):
    role = models.CharField(max_length=30,verbose_name="Роль сотрудника")
    def __str__(self):
        return self.role

    class Meta:
        verbose_name = "Роль сотрудника"
        verbose_name_plural = "Роли сотрудников"



class Employee(models.Model):
    # Новые поля
    last_name = models.CharField(max_length=50, default='',verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, default='',verbose_name="Имя")
    middle_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")

    # Старые поля (как было)
    login = models.CharField(max_length=20, verbose_name="Логин")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    role = models.ForeignKey('Role', on_delete=models.CASCADE, verbose_name="Роль")
    email = models.EmailField(verbose_name="Эл.почта")

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.login  # Можно изменить на вывод ФИО позже

    def get_login_logs(self):
        return self.employeeloginlog_set.all().order_by('-login_time')

    class Meta:
        verbose_name = "Информацию о сотрудниках"
        verbose_name_plural = "Информация о сотрудниках"

# class SlopeCondition(models.Model):
#     name = models.CharField(max_length=30, verbose_name="Состояние склона")
#
#     def __str__(self):
#         return self.name


class Camera(models.Model):
    number = models.CharField(max_length=30, verbose_name="Номер склона")
    video_file = models.FileField(upload_to='camera_videos/', blank=True, null=True, verbose_name="Видео камеры")
    condition = models.CharField(
        max_length=50,
        choices=[
            #("ограниченный доступ", "Ограниченный доступ"),
            ("открытая трасса", "Открытая трасса"),
            ("Закрытая трасса", "Закрытая трасса"),
        ],
        verbose_name="Состояние склона"
    )
    # slope_state = models.CharField(
    #     max_length=30,
    #     choices=[
    #         ("по знаку", "По знаку"),
    #         ("по сетке", "По сетке"),
    #     ],
    #     blank=True,
    #     null=True,
    #     verbose_name="Тип ограничения"
    # )
    # sign_image = models.ImageField(upload_to='sign_images/', blank=True, null=True, verbose_name="Изображение знака")

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Информацию о камере/склоне"
        verbose_name_plural = "Информация о камере/склоне"


from django.db import models

# class Notification(models.Model):
#     title = models.CharField(max_length=100)
#     message = models.TextField()
#     image = models.CharField(max_length=255, null=True, blank=True)  # Поле для хранения URL изображения
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title


from django.utils import timezone


class EmployeeLoginLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="Время входа")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="Время выхода")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")

    def formatted_login_time(self):
        return timezone.localtime(self.login_time).strftime('%d %B %Y, %H:%M')

    def formatted_logout_time(self):
        if self.logout_time:
            return timezone.localtime(self.logout_time).strftime('%d %B %Y, %H:%M')
        return ""

    class Meta:
        verbose_name = "Лог входа сотрудника"
        verbose_name_plural = "Логи входов сотрудников"
        ordering = ['-login_time']

class Notification(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Сообщение")
    image = models.ImageField(upload_to='notifications/', null=True, blank=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ['-created_at']