from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout

# Настройка Django
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
        spacing: 10

        Label:
            text: "Авторизация"
            font_size: 24

        GridLayout:
            cols: 2
            rows: 2
            spacing: 10

            Label:
                text: "Логин:"
            TextInput:
                id: login
                multiline: False

            Label:
                text: "Пароль:"
            TextInput:
                id: passwd
                password: True
                multiline: False

        Button:
            text: "Войти"
            size_hint_y: None
            height: 50
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


class LoginScreen(Screen):
    def process_login(self):
        try:
            # Получаем логин и пароль из полей ввода
            login = self.ids.login.text.strip()
            password = self.ids.passwd.text.strip()

            # Ищем пользователя в базе данных по логину
            employee = Employee.objects.get(login=login)

            # Проверяем пароль с использованием check_password()
            if check_password(password, employee.password):
                self.show_popup(f"Добро пожаловать, {login}!")
                self.manager.current = "custom"
                print(f"Успешная авторизация! {employee.login} в сети")
                cameras = Camera.objects.all()
                if cameras.exists():
                    custom_screen = self.manager.get_screen('custom')
                    custom_screen.display_videos(cameras)
                self.manager.current = "custom"



            else:
                print("Неверный пароль.")
        except Employee.DoesNotExist:
            print("Пользователь с таким логином не найден.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def show_popup(self, message):
        popup = Popup(title='Успешная авторизация', content=Label(text=message), size_hint=(None, None),
                      size=(400, 100))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)


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


class CustomScreen(Screen):
    def display_videos(self, cameras):
        """Получает все видео из базы данных и отображает их."""
        video_grid = self.ids.video_grid
        video_grid.clear_widgets()

        for camera in cameras:
            if camera.video_file:
                container = BoxLayout(orientation='vertical')
                video_path = camera.video_file.path
                condition_name = str(camera.condition)
                print(camera.condition)
                condition = condition_name.strip().lower()

                if str(condition) == 'открытая трасса':
                    label = Label(text=f"Склон {camera.number}", size_hint=(1, 0.1))
                    video_player = VideoPlayer(source=video_path, state="play", options={"eos": "loop"})

                    # Скрытие элементов управления (это не работает напрямую, но можно попробовать)
                    video_player.controls = False  # Это не работает в Kivy, так как controls не является свойством VideoPlayer

                    container = BoxLayout(orientation='vertical')
                    container.add_widget(video_player)
                    container.add_widget(label)
                    video_grid.add_widget(container)

                elif condition == 'закрытая трасса':
                    label = Label(text=f"Склон {camera.number}", size_hint=(1, 0.1))
                    image_widget = KivyImage()
                    container.add_widget(image_widget)
                    video_grid.add_widget(container)
                    self.apply_yolo([camera], image_widget)

    def apply_yolo(self, cameras, image_widget):
        """Применяет модель YOLOv5 к видео."""
        model = torch.hub.load("ultralytics/yolov5", "yolov5s")

        for camera in cameras:
            if camera.video_file:
                cap = cv2.VideoCapture(camera.video_file.path)

                # Запускаем обработку кадров в потоке
                thread = threading.Thread(target=self.process_frames, args=(cap, model, image_widget))
                thread.start()
                # Удалите вызов play_video, так как он не нужен в этом случае
                # threading.Thread(target=self.play_video, args=(image_widget,)).start()

    def process_frames(self, cap, model, image_widget):
        """Обрабатывает кадры видео."""
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Применяем модель YOLOv5 напрямую к кадру в формате BGR
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(rgb_frame)
            df = results.pandas().xyxy[0]

            # Фильтруем только людей
            person_df = df[df['class'] == 0]

            # Рисуем прямоугольники вокруг обнаруженных людей на копии исходного кадра
            frame_copy = frame.copy()
            for index, row in person_df.iterrows():
                x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 0, 255), 10)

            # Переворачиваем кадр по вертикали
            flipped_frame = cv2.flip(frame_copy, 0)

            # Преобразуем кадр в RGB для отображения в Kivy
            rgb_flipped_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)

            # Обновляем интерфейс Kivy в основном потоке
            Clock.schedule_once(lambda dt: self.update_image(image_widget, rgb_flipped_frame))

            frame_count += 1

            # Задержка для воспроизведения видео
            cv2.waitKey(1)

        cap.release()

    def update_image(self, image_widget, frame):
        """Обновляет изображение в Kivy."""
        # Преобразуем кадр в формат, подходящий для Kivy
        height, width, channel = frame.shape
        bytes_per_line = 3 * width

        # Поворот кадра на 180 градусов (не нужно, так как уже перевернули)
        qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # Создание текстуры из кадра
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(frame.tobytes(order=None), colorfmt='rgb', bufferfmt='ubyte')
        image_widget.texture = texture

    def play_video(self, image_widget):
        """Воспроизводит видео."""
        frame_count = 0
        while True:
            image_path = f"temp_{frame_count}.png"
            if not os.path.exists(image_path):
                break

            # Загрузите изображение из файла
            img = cv2.imread(image_path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Переворачиваем кадр по вертикали
            flipped_img = cv2.flip(rgb_img, 0)

            # Обновите интерфейс Kivy в основном потоке
            Clock.schedule_once(lambda dt: self.update_image(image_widget, flipped_img))

            frame_count += 1
            time.sleep(0.033)


class LoginApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CustomScreen(name="custom"))
        return sm


if __name__ == "__main__":
    try:
        LoginApp().run()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")



