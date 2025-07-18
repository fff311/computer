from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .forms import LoginForm
from .models import Employee

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .forms import LoginForm
from .models import Employee, Camera

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data['username']
            password_input = form.cleaned_data['password']

            try:
                employee = Employee.objects.get(login=login_input)

                if check_password(password_input, employee.password):
                    # Аутентификация успешна
                    request.session['user_id'] = employee.id  # Сохраняем ID сотрудника в сессии

                    role = employee.role.role  # Получаем название роли

                    if role == 'оператор':
                        return redirect('operator')  # Перенаправляем на страницу оператора
                    elif role == 'спасатель':
                        return redirect('spasatel')  # Перенаправляем на страницу спасателя
                    elif role == 'administrator':
                        return redirect('/admin/')  # Перенаправление на панель администратора
                    else:
                        messages.error(request, "Неизвестная роль")
                        return render(request, 'shopapp/login.html', {'form': form})
                else:
                    messages.error(request, "Неправильный логин или пароль")
                    return render(request, 'shopapp/login.html', {'form': form})

            except Employee.DoesNotExist:
                messages.error(request, "Неправильный логин или пароль")
                return render(request, 'shopapp/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'shopapp/login.html', {'form': form})
from django.shortcuts import render


def spasatel_view(request):
    # Здесь код для отображения страницы спасателя
    return render(request, 'shopapp/spasatel.html')
from django.shortcuts import render, get_object_or_404
from .models import Camera
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render
from .models import Camera


from django.shortcuts import redirect
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')


from django.shortcuts import render
from .models import Camera
import cv2
import torch
from PIL import Image
import numpy as np
import requests
from io import BytesIO
import os
import cv2
import torch

# Загрузка модели YOLOv5


import transliterate
from django.shortcuts import render

import langdetect
#
# import cv2
# from django.shortcuts import render
# import os
#
# import cv2
# import torch
# from django.http import StreamingHttpResponse
#
# # Загрузите модель YOLOv5 (это должно быть сделано один раз)
# #model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
#
#
# def gen(camera):
#     cap = cv2.VideoCapture(camera.video_file.path)
#
#     while True:
#         ret, frame = cap.read()
#
#         if not ret:
#             # Перезапустите видео если оно закончилось
#             cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Установите позицию на начало файла
#
#             ret, frame = cap.read()  # Прочитайте первый кадр
#
#             if not ret:
#                 break
#
#         # Примените модель только если состояние равно "закрытая трасса"
#         if camera.condition.name == "закрытая трасса":
#             results = model(frame)
#
#             for result in results.xyxy[0]:
#                 x1, y1, x2, y2, conf, cls_id = result.cpu().numpy()
#
#                 cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color=(0, 255, 0), thickness=3)
#
#                 class_name = f"Person ({conf:.4f})"
#
#                 cv2.putText(frame,
#                             text=class_name,
#                             org=(int(x1), int(y1 - 10)),
#                             fontFace=cv2.FONT_HERSHEY_SIMPLEX,
#                             fontScale=0.6,
#                             color=(255, 255, 255),
#                             thickness=1)
#
#         _, buffer = cv2.imencode('.jpg', frame)
#
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
#
#     cap.release()
#
# def video_feed(request, camera_id):
#     camera = Camera.objects.get(id=camera_id)
#
#     return StreamingHttpResponse(gen(camera),
#                                  content_type='multipart/x-mixed-replace; boundary=frame')
#
# def operator_view(request):
#     cameras = Camera.objects.all()
#
#     current_user = Employee.objects.get(id=request.user.id)
#
#     return render(request,
#                   template_name='shopapp/operator.html',
#                   context={'cameras': cameras,
#                            'current_user': current_user})
#
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.views.decorators.csrf import csrf_exempt
#
#
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
#
# import json
# import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from django.core.files.storage import FileSystemStorage
#
#
from shopapp.models import Notification
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
@csrf_exempt
def receive_notification(request):

    if request.method == "POST":
        try:
            data = request.POST
            title = data.get("title")
            message = data.get("message")
            image = request.FILES.get('image')

            # Создаём уведомление
            notification = Notification.objects.create(
                title=title,
                message=message
            )

            # Сохраняем изображение если есть
            if image:
                notification.image = image
                notification.save()
                print(f"Уведомление {notification.id} создано с изображением")
            else:
                print(f"Уведомление {notification.id} создано без изображения")

            return JsonResponse({
                "success": True,
                "message": "Уведомление получено",
                "notification_id": notification.id
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


def view_notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'shopapp/notifications.html', {'notifications': notifications})
