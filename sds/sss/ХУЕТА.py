from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QLineEdit, QPushButton, QFormLayout
from PyQt5.QtGui import QMovie, QImage, QPixmap
from PyQt5.QtCore import Qt
from django.db import models
from django.contrib.auth.hashers import check_password
import cv2
import torch
import threading

# Настройка Django
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sss.settings')
try:
    django.setup()
except Exception as e:
    print(f"Ошибка настройки Django: {e}")
    exit()

from shopapp.models import Employee, Camera

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        label = QLabel("Авторизация")
        label.setStyleSheet("font-size: 24pt;")

        form_layout = QFormLayout()
        self.login_input = QLineEdit()
        self.passwd_input = QLineEdit()
        self.passwd_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow(QLabel("Логин:"), self.login_input)
        form_layout.addRow(QLabel("Пароль:"), self.passwd_input)

        button = QPushButton("Войти")
        button.clicked.connect(self.process_login)

        layout.addWidget(label)
        layout.addLayout(form_layout)
        layout.addWidget(button)

        self.setLayout(layout)

    def open_video_screen(self):
        cameras = Camera.objects.all()
        if cameras.exists():
            custom_screen = CustomScreen()
            custom_screen.display_videos(cameras)
            custom_screen.show()
        else:
            print("Нет видео в базе данных.")

    def process_login(self):
        try:
            # Получаем логин и пароль из полей ввода
            login = self.login_input.text().strip()
            password = self.passwd_input.text().strip()

            # Ищем пользователя в базе данных по логину
            employee = Employee.objects.get(login=login)

            # Проверяем пароль с использованием check_password()
            if check_password(password, employee.password):
                print(f"Добро пожаловать, {login}!")
                print(f"Успешная авторизация! {employee.login} в сети")

                # Закрываем текущее окно
                self.close()

                # Открываем новое окно в отдельном потоке
                thread = threading.Thread(target=self.open_video_screen)
                thread.start()

            else:
                print("Неверный пароль.")
        except Employee.DoesNotExist:
            print("Пользователь с таким логином не найден.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

class CustomScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Видео")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.video_grid = QGridLayout()
        layout.addLayout(self.video_grid)

        self.setLayout(layout)

    def display_videos(self, cameras):
        """Получает все видео из базы данных и отображает их."""
        row_val = 0
        col_val = 0
        for camera in cameras:
            if camera.video_file:
                label = QLabel(f"Склон {camera.number}")
                self.video_grid.addWidget(label, row_val, col_val)

                if camera.condition == 'открытая трасса':
                    movie_label = QLabel()
                    movie_label.setMovie(QMovie(camera.video_file.path))
                    movie_label.movie().start()
                    self.video_grid.addWidget(movie_label, row_val + 1, col_val)

                elif camera.condition == 'закрытая трасса':
                    # Применение модели YOLOv5
                    self.apply_yolo(camera)

                col_val += 1
                if col_val > 1:
                    col_val = 0
                    row_val += 2

    def apply_yolo(self, camera):
        """Применяет модель YOLOv5 к видео."""
        model = torch.hub.load("ultralytics/yolov5", "yolov5s")
        cap = cv2.VideoCapture(camera.video_file.path)

        # Запускаем обработку кадров в потоке
        thread = threading.Thread(target=self.process_frames, args=(cap, model))
        thread.start()

    def process_frames(self, cap, model):
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
                cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Отображаем обработанный кадр
            height, width, channel = frame_copy.shape
            bytes_per_line = 3 * width
            qimg = QImage(frame_copy.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            label = QLabel()
            label.setPixmap(QPixmap.fromImage(qimg).scaled(320, 240))
            self.video_grid.addWidget(label, 1, len(self.video_grid.columnCount()))

            frame_count += 1

            # Задержка для воспроизведения видео
            cv2.waitKey(1)

        cap.release()

if __name__ == "__main__":
    app = QApplication([])
    login_screen = LoginScreen()
    login_screen.show()
    video = CustomScreen()
    video.show()
    app.exec_()


