from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
#Config.set('graphics', 'width', '500')  # Ширина окна
#Config.set('graphics', 'height', '300')  # Высота окна
# Настройка Django
from kivy.core.window import Window
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sss.settings')
try:
    django.setup()
except Exception as e:
    print(f"Ошибка настройки Django: {e}")
    exit()

from shopapp.models import Employee
from django.contrib.auth.hashers import check_password

# Загрузка KV-строки
KV = '''
<LoginScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 20
        size_hint: (0.4, 0.6)

        pos_hint: {'center_x': 0.5} 

        Widget:
            size_hint_y: 1
        Label:
            text: "Авторизация"
            font_size: 24
            size_hint_y: None
            height: self.texture_size[1] + 20
            halign: 'center'
            text_size: self.width, None


        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            spacing: 15
            # Центрируем весь блок с логином и паролем
            size_hint_x: None
            width: 320
            pos_hint: {'center_x': 0.5}

            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                spacing: 10

                Label:
                    text: "Логин:"
                    size_hint_x: None
                    width: 80
                    font_size: 18
                    halign: 'right'
                    valign: 'middle'
                    text_size: self.size

                TextInput:
                    id: login
                    multiline: False
                    size_hint_x: 1
                    font_size: 18
                    height: 40
                    size_hint_y: None

            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                spacing: 10

                Label:
                    text: "Пароль:"
                    size_hint_x: None
                    width: 80
                    font_size: 18
                    halign: 'right'
                    valign: 'middle'
                    text_size: self.size

                TextInput:
                    id: passwd
                    password: True
                    multiline: False
                    size_hint_x: 1
                    font_size: 18
                    height: 40
                    size_hint_y: None

        Button:
            text: "Войти"
            size_hint_y: None
            height: 50
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5}
            on_press: root.process_login()

<CustomScreen>:
    ScrollView:
        size_hint_y: None
        height: root.height
        GridLayout:
            id: video_grid
            cols: 2  # Количество видео в строке
            size_hint_y: None
            height: self.minimum_height
            row_default_height: 300
            row_force_default: True
            GridLayout:
                id: image_box
                cols: 2  # Количество изображений в строке
                size_hint_y: None
                height: self.minimum_height
                row_default_height: 300
                row_force_default: True

'''
from shopapp.models import Camera

Builder.load_string(KV)
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from shopapp.models import EmployeeLoginLog
from django.utils import timezone

class LoginScreen(Screen):


    def set_small_window(self, dt):
        Window.size = (500, 300)
        Window.minimum_width, Window.minimum_height = 500, 300
        Window.maximum_width, Window.maximum_height = 500, 300
        # Принудительно сдвинуть окно на 1 пиксель и обратно
        Window.left += 1
        Window.left -= 1

    def process_login(self):
        try:
            login = self.ids.login.text.strip()
            password = self.ids.passwd.text.strip()

            if not login or not password:
                self.show_error_popup("Логин и пароль не могут быть пустыми")
                return

            employee = Employee.objects.get(login=login)

            if check_password(password, employee.password):
                App.get_running_app().current_user = login
                EmployeeLoginLog.objects.create(
                    employee=employee,
                    ip_address=self.get_client_ip()
                )
                self.show_success_popup(f"Добро пожаловать, {login}!")
                print(f"Успешная авторизация! {employee.login} в сети")

                # Увеличиваем окно до нормального размера после входа
                Window.size = (1024, 768)
                Window.minimum_width, Window.minimum_height = 800, 600
                Window.maximum_width, Window.maximum_height = 1920, 1080

                # Переходим на экран с камерами
                screen_manager = self.manager
                if 'custom' in screen_manager.screen_names:
                    screen_manager.remove_widget(screen_manager.get_screen('custom'))

                custom_screen = CustomScreen(name='custom')
                screen_manager.add_widget(custom_screen)

                cameras = Camera.objects.all()
                if cameras.exists():
                    custom_screen.display_videos(cameras)

                screen_manager.current = "custom"
            else:
                self.show_error_popup("Неверный пароль")

        except Employee.DoesNotExist:
            self.show_error_popup("Пользователь не найден")
        except Exception as e:
            self.show_error_popup(f"Ошибка авторизации: {str(e)}")
            print(f"Произошла ошибка: {e}")


    def show_success_popup(self, message):
        """Показывает всплывающее окно об успехе"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))

        popup = Popup(title='Успех',
                      content=content,
                      size_hint=(None, None),
                      size=(400, 200))

        # Закрываем попап через 1 секунду
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
        popup.open()

    def show_error_popup(self, message):
        """Показывает всплывающее окно об ошибке"""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))

        button = Button(text='OK', size_hint=(1, 0.3))
        popup = Popup(title='Ошибка',
                      content=content,
                      size_hint=(None, None),
                      size=(400, 200))

        button.bind(on_press=popup.dismiss)
        content.add_widget(button)
        popup.open()

    def get_client_ip(self):
        """Получаем IP адрес клиента (упрощенная версия)"""
        import socket
        return socket.gethostbyname(socket.gethostname())

    # В класс CustomScreen добавим запись о выходе
    def exit_to_login(self, instance):
        """Обработчик кнопки выхода"""
        # Получаем последнюю запись о входе текущего пользователя
        from shopapp.models import EmployeeLoginLog
        last_login = EmployeeLoginLog.objects.filter(
            employee__login=App.get_running_app().current_user
        ).last()

        if last_login:
            last_login.logout_time = timezone.now()
            last_login.save()

    def on_pre_enter(self, *args):
        # Очищаем поля при каждом входе на экран
        self.ids.login.text = ''
        self.ids.passwd.text = ''
        # Другие действия по изменению размера окна, которые у вас уже есть
        Clock.schedule_once(self.set_small_window, 0.1)

Builder.load_string(KV)
import os

os.environ["KIVY_VIDEO"] = "ffpyplayer"
from kivy.uix.videoplayer import VideoPlayer
import torch
import cv2
import torch
import numpy as np
from PIL import Image
from kivy.uix.image import Image as KivyImage
import threading
import threading
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from PyQt5.QtGui import QImage
from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.image import Image as KivyImage
from kivy.graphics.texture import Texture
import cv2
import torch
import numpy as np
import threading

import requests
import multiprocessing as mp
from multiprocessing import Queue
import cv2
import torch
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import multiprocessing as mp
from multiprocessing import Queue
import cv2
import torch
import requests
import multiprocessing as mp
from multiprocessing import Queue
import cv2
import torch
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.uix.video import Video  # Исправленный импорт
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import torch
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.uix.video import Video
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import queue
import threading

import threading
import queue
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

import cv2
import torch
import requests
import threading
import queue
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.uix.video import Video
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import cv2
import torch
import queue
import threading
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.anchorlayout import AnchorLayout
import cv2
import torch
import queue
import threading
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.video import Video
from kivy.uix.popup import Popup
from kivy.uix.button import Button
import requests

import time  # Добавляем недостающий импорт
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from dotenv import load_dotenv

load_dotenv()
class CustomScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_paused = False
        self.last_frame = None
        self.frame_queue = queue.Queue(maxsize=2)
        self.processed_queue = queue.Queue(maxsize=2)
        self.stop_event = threading.Event()
        self.yolo_thread = None
        self.video_thread = None
        self.current_popup = None
        self.resume_timer = None
        self.image_widget = None
        self.fps = 30
        self.last_update_time = 0
        self.yolo_fps = 30
        self.last_yolo_time = 0
        self.last_popup_time = 0  # время последнего показа popup
        self.popup_cooldown = 10
        main_layout = BoxLayout(orientation='vertical')

        # Создаем панель для кнопки выхода (5% высоты экрана)
        top_panel = BoxLayout(size_hint=(1, 0.05))

        # Создаем кнопку выхода
        exit_button = Button(
            text='Выход',
            size_hint=(0.1, 1),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        exit_button.bind(on_press=self.exit_to_login)
        top_panel.add_widget(exit_button)

        # Создаем ScrollView для видео (95% высоты экрана)
        self.scroll_view = ScrollView(
            size_hint=(1, 0.95),
            do_scroll_x=False,
            do_scroll_y=True
        )

        # Создаем GridLayout для видео
        self.video_grid = GridLayout(
            cols=2,
            size_hint_y=None,
            spacing=10,
            padding=10,
            row_default_height=300,
            row_force_default=True
        )
        self.video_grid.bind(minimum_height=self.video_grid.setter('height'))
        self.scroll_view.add_widget(self.video_grid)

        # Добавляем все в основной контейнер
        main_layout.add_widget(top_panel)
        main_layout.add_widget(self.scroll_view)
        self.add_widget(main_layout)
    def display_videos(self, cameras):
        """Основной метод для отображения видео"""
        self.video_grid.clear_widgets()

        for camera in cameras:
            if not hasattr(camera, 'video_file') or not camera.video_file:
                print(f"У камеры {getattr(camera, 'number', 'N/A')} нет видеофайла")
                continue

            container = BoxLayout(orientation='vertical', size_hint_y=None, height=300)
            video_path = camera.video_file.path
            condition = str(getattr(camera, 'condition', '')).strip().lower()

            label = Label(text=f"Склон {getattr(camera, 'number', 'N/A')}", size_hint=(1, 0.1))

            if condition == 'открытая трасса':
                try:
                    video = Video(source=video_path, state='play', options={'eos': 'loop'})
                    video.volume = 0
                    container.add_widget(video)
                except Exception as e:
                    print(f"Ошибка создания видео: {e}")
                    continue

            elif condition == "закрытая трасса":
                self.image_widget = KivyImage()
                container.add_widget(self.image_widget)
                self.start_processing(video_path)
            else:
                print('flk;bdlkhghfg')
            container.add_widget(label)
            self.video_grid.add_widget(container)

        # Обновляем высоту GridLayout
        self.video_grid.height = max(
            self.scroll_view.height,
            self.video_grid.minimum_height
        )

    def start_processing(self, video_path):
        """Запуск обработки видео с частотой 5 FPS"""
        self.stop_event.clear()

        # Поток для чтения видео
        self.video_thread = threading.Thread(
            target=self.video_reader,
            args=(video_path, self.frame_queue, self.stop_event),
            daemon=True
        )
        self.video_thread.start()

        # Поток для обработки YOLO
        self.yolo_thread = threading.Thread(
            target=self.yolo_processor,
            args=(self.frame_queue, self.processed_queue, self.stop_event),
            daemon=True
        )
        self.yolo_thread.start()

        # Устанавливаем частоту обновления UI (5 FPS)
        Clock.schedule_interval(self.update_ui, 1.0 / self.yolo_fps)

    def video_reader(self, video_path, frame_queue, stop_event):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = max(1, int(1000 / fps)) if fps > 0 else 30

        while cap.isOpened() and not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break

            try:
                while not frame_queue.empty():
                    frame_queue.get_nowait()
                frame_queue.put(frame, timeout=0.1)
            except queue.Full:
                pass

            cv2.waitKey(delay)
        cap.release()

    def yolo_processor(self, input_queue, output_queue, stop_event):
        model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=True)

        while not stop_event.is_set():
            try:
                current_time = time.time()
                # Пропускаем обработку если не прошло достаточно времени
                if current_time - self.last_yolo_time < 1.0 / self.yolo_fps:
                    time.sleep(0.01)  # Небольшая задержка для уменьшения нагрузки на CPU
                    continue

                frame = input_queue.get(timeout=0.5)
                self.last_yolo_time = current_time  # Обновляем время последней обработки

                # Уменьшаем размер кадра для ускорения обработки
                small_frame = cv2.resize(frame, (640, 360))
                results = model(small_frame)

                # Масштабируем результаты обратно к исходному размеру
                frame_copy = frame.copy()
                h_ratio = frame.shape[0] / small_frame.shape[0]
                w_ratio = frame.shape[1] / small_frame.shape[1]

                # Отрисовываем bounding boxes для обнаруженных людей (класс 0)
                for *box, conf, cls in results.xyxy[0]:
                    if int(cls) == 0:
                        x1, y1, x2, y2 = map(int, [
                            box[0] * w_ratio,
                            box[1] * h_ratio,
                            box[2] * w_ratio,
                            box[3] * h_ratio
                        ])
                        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 0, 255), 2)

                # Очищаем очередь от старых кадров
                while not output_queue.empty():
                    output_queue.get_nowait()

                # Помещаем обработанный кадр в очередь
                output_queue.put((frame_copy, len(results.xyxy[0]) > 0))

            except queue.Empty:
                continue  # Если очередь пуста, продолжаем цикл
            except Exception as e:
                if not stop_event.is_set():
                    print(f"YOLO обработка: {e}")
                continue

    def update_ui(self, dt):
        if self.image_widget is None or self.video_paused:
            return

        try:
            if not self.processed_queue.empty():
                frame, detected = self.processed_queue.get_nowait()

                # Конвертируем кадр для отображения
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]),
                    colorfmt='bgr'
                )
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.image_widget.texture = texture

                if detected:
                    current_time = time.time()
                    # Проверяем, прошло ли достаточно времени с последнего показа popup
                    if current_time - self.last_popup_time > self.popup_cooldown:
                        self.last_frame = frame
                        self.video_paused = True
                        self.show_popup()
                        self.last_popup_time = current_time

        except Exception as e:
            print(f"Ошибка обновления UI: {e}")

    def show_popup(self):
        if self.current_popup is not None:
            return

        layout = BoxLayout(orientation='vertical', spacing=0, padding=0)

        if self.last_frame is not None:
            rgb_frame = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
            flipped_frame = cv2.flip(rgb_frame, 0)

            texture = Texture.create(
                size=(flipped_frame.shape[1], flipped_frame.shape[0]),
                colorfmt='rgb'
            )
            texture.blit_buffer(
                flipped_frame.tobytes(order=None),
                colorfmt='rgb',
                bufferfmt='ubyte'
            )

            # Создаем интерактивное изображение с обработчиком клика
            image = ClickableImage(
                texture=texture,
                allow_stretch=True,
                keep_ratio=True,
                size_hint_y=None,
                height=350
            )
            layout.add_widget(image)

        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(250, 50),
            spacing=20,
            padding=0
        )

        yes_button = Button(text="Да", size_hint=(None, None), size=(100, 40))
        no_button = Button(text="Нет", size_hint=(None, None), size=(100, 40))

        yes_button.bind(on_press=self.on_yes_pressed)
        no_button.bind(on_press=self.on_no_pressed)

        buttons_layout.add_widget(yes_button)
        buttons_layout.add_widget(no_button)

        buttons_anchor = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint_y=None,
            height=50,
            padding=0
        )
        buttons_anchor.add_widget(buttons_layout)

        layout.add_widget(buttons_anchor)

        self.current_popup = Popup(
            title='Обнаружение объекта',
            content=layout,
            size_hint=(None, None),
            size=(400, image.height + buttons_anchor.height)
        )
        self.current_popup.open()
    def on_yes_pressed(self, instance):
        # self.send_notification()
        # self.close_popup()

        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None
        self.video_paused = False
        self.show_send_choice_popup()

    def show_send_choice_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        label = Label(text="Выберите способ отправки сообщения:")
        layout.add_widget(label)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=50)

        telegram_button = Button(text="Телеграм бот")
        rescuer_button = Button(text="Страница спасателя")

        telegram_button.bind(on_press=self.send_to_telegram)
        rescuer_button.bind(on_press=self.send_to_rescuer_page)

        buttons_layout.add_widget(telegram_button)
        buttons_layout.add_widget(rescuer_button)

        layout.add_widget(buttons_layout)

        self.send_choice_popup = Popup(
            title="Выбор отправки",
            content=layout,
            size_hint=(None, None),
            size=(400, 150),
            auto_dismiss=True
        )
        self.send_choice_popup.open()

    def send_to_telegram(self, instance):
        self.send_choice_popup.dismiss()
        self.video_paused = False  # Снимаем паузу с видео
        self.last_popup_time = time.time()  # Обновляем время последнего показа окна

        # Запускаем отправку в отдельном потоке, чтобы не блокировать UI
        threading.Thread(target=self._send_telegram_message, daemon=True).start()
        self.close_popup()

    def _send_telegram_message(self):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        message = "Внимание! Человек был обнаружен на видео."
        image_path = "temp_image.jpg"
        if self.last_frame is not None:
            cv2.imwrite(image_path, self.last_frame)
        else:
            print("Нет кадра для отправки")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(image_path, 'rb') as photo:
            payload = {'chat_id': chat_id, 'caption': message, 'parse_mode': 'Markdown'}
            files = {'photo': photo}
            try:
                response = requests.post(url, data=payload, files=files)
                if response.status_code == 200:
                    print("Отправлено в Telegram!")
                else:
                    print(f"Ошибка при отправке: {response.content}")
            except Exception as e:
                print(f"Ошибка: {e}")

    def send_to_rescuer_page(self, instance):
        self.send_choice_popup.dismiss()
        self.video_paused = False  # Снимаем паузу с видео
        self.last_popup_time = time.time()  # Обновляем время последнего показа окна

        threading.Thread(target=self.send_notification, daemon=True).start()
        self.close_popup()
        print("Отправлено на страницу спасателя")



    def on_no_pressed(self, instance):
        self.close_popup()
        self.resume_timer = Clock.schedule_once(lambda dt: self.resume_video(), 5)

    def resume_video(self):
        self.video_paused = False
        self.resume_timer = None

    def close_popup(self):
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None
        self.video_paused = False

    def send_notification(self):
        url = "http://127.0.0.1:8000/shopapp/api/receive_notification/"  # Новый URL для отправки уведомления
        cv2.imwrite('temp_image.jpg', self.last_frame)

        data = {"title": "Обнаружение человека", "message": "Обнаружен человек на видео"}
        files = {'image': open('temp_image.jpg', 'rb')}

        try:
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                print("Уведомление отправлено успешно")
            else:
                print(f"Ошибка отправки уведомления, статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def exit_to_login(self, instance):
        """Обработчик кнопки выхода с записью времени выхода"""
        # Получаем текущего пользователя
        current_user_login = App.get_running_app().current_user

        if current_user_login:
            try:
                # Находим сотрудника
                employee = Employee.objects.get(login=current_user_login)

                # Находим последнюю запись о входе этого сотрудника без времени выхода
                last_login = EmployeeLoginLog.objects.filter(
                    employee=employee,
                    logout_time__isnull=True
                ).order_by('-login_time').first()

                if last_login:
                    # Устанавливаем текущее время как время выхода
                    last_login.logout_time = timezone.now()
                    last_login.save()
                    print(f"Записали время выхода для пользователя {current_user_login}")

            except Employee.DoesNotExist:
                print(f"Пользователь {current_user_login} не найден")
            except Exception as e:
                print(f"Ошибка при записи времени выхода: {e}")

        # Останавливаем все процессы
        self.on_leave()

        # Получаем экран авторизации
        login_screen = self.manager.get_screen('login')

        # Очищаем поля логина и пароля
        login_screen.ids.login.text = ''
        login_screen.ids.passwd.text = ''

        # Переключаемся на экран авторизации
        self.manager.current = 'login'

        # Очищаем виджеты видео, если нужно
        if hasattr(self, 'video_grid'):
            self.video_grid.clear_widgets()

    def on_leave(self):
        """Очистка ресурсов при выходе"""
        self.stop_event.set()

        # Останавливаем потоки
        if self.yolo_thread and self.yolo_thread.is_alive():
            self.yolo_thread.join(timeout=0.5)
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=0.5)

        # Останавливаем таймеры
        if self.resume_timer:
            self.resume_timer.cancel()
        Clock.unschedule(self.update_ui)

        # Закрываем все попапы
        self.close_popup()

class ClickableImage(KivyImage):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.show_enlarged_image()
            return True
        return super().on_touch_down(touch)

    def show_enlarged_image(self):
        # Открываем новое окно с увеличенным изображением
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Копируем текстуру, чтобы показать в большем размере
        enlarged_image = KivyImage(
            texture=self.texture,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1)
        )

        popup_layout.add_widget(enlarged_image)

        close_button = Button(text='Закрыть', size_hint=(1, None), height=40)
        popup_layout.add_widget(close_button)

        popup = Popup(
            title='Увеличенное изображение',
            content=popup_layout,
            size_hint=(None, None),
            size=(800, 600)
        )

        close_button.bind(on_press=popup.dismiss)
        popup.open()


class LoginApp(App):
    current_user = None
    def build(self):
        sm = ScreenManager()

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CustomScreen(name="custom"))
        return sm

    def on_stop(self):
        if self.current_user:
            try:
                last_login = EmployeeLoginLog.objects.filter(
                    employee__login=self.current_user,
                    logout_time__isnull=True
                ).latest('login_time')

                if last_login:
                    last_login.logout_time = timezone.now()
                    last_login.save()
            except EmployeeLoginLog.DoesNotExist:
                pass


if __name__ == "__main__":
    try:
        # Важно для корректной работы многопроцессорности в Windows
        mp.freeze_support()
        LoginApp().run()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
