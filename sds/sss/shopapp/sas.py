import torch
import torch
import cv2
import torch
import numpy as np
from PIL import Image

# Model
model = torch.hub.load("ultralytics/yolov5", "yolov5s") # or yolov5n - yolov5x6, custom

# Images
video_path = "C:/Users/kivvesh/Desktop/ddd/video/dod.mp4"  # or file, Path, PIL, OpenCV, numpy, list
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Преобразуем кадр в RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Применяем модель YOLOv5
    results = model(rgb_frame)

    # Получаем результаты в формате pandas DataFrame
    df = results.pandas().xyxy[0]

    # Отфильтровываем только объекты, которые являются человеком (class 0)
    person_df = df[df['class'] == 0]

    # Рисуем прямоугольники вокруг обнаруженных людей
    for index, row in person_df.iterrows():
        x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Выводим обработанный кадр
    cv2.imshow('Frame', frame)

    # Задержка для воспроизведения видео
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()