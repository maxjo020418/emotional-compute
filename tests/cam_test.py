import sys
import cv2
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal, pyqtBoundSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QSlider, QVBoxLayout, QHBoxLayout
)

class VideoThread(QThread):
    change_pixmap: pyqtBoundSignal = pyqtSignal(np.ndarray, dict)

    face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt2.xml')
    eyes_cascade = cv2.CascadeClassifier('./haarcascade_eye_tree_eyeglasses.xml')

    def run(self):
        cap = cv2.VideoCapture(0)
        print(type(self.change_pixmap))
        print(cap)

        while True:
            ret, frame = cap.read()  # bool, ndarray
            if ret:
                self.change_pixmap.emit(*self.detect_face(frame))

    def detect_face(self, frame: np.ndarray) -> (np.ndarray, dict):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)

        info = {}

        # Detect faces
        faces = self.face_cascade.detectMultiScale(frame_gray)
        info["faces_num"] = len(faces)

        for (x, y, w, h) in faces:
            center = (x + w // 2, y + h // 2)
            frame = cv2.ellipse(frame, center, (w // 2, h // 2), 0, 0, 360, (255, 0, 255), 4)

            face_roi = frame_gray[y:y + h, x:x + w]
            info["face_roi"] = face_roi

            # In each face, detect eyes
            eyes = self.eyes_cascade.detectMultiScale(face_roi)
            info["eyes_num"] = len(eyes)

            for (x2, y2, w2, h2) in eyes:
                eye_center = (x + x2 + w2 // 2, y + y2 + h2 // 2)
                radius = int(round((w2 + h2) * 0.25))
                frame = cv2.circle(frame, eye_center, radius, (255, 0, 0), 4)

        return frame, info

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('test')

        # video widget
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background: black;")

        # info/control panel
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")

        # set layouts
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Start video thread
        self.thread = VideoThread()
        self.thread.change_pixmap.connect(self.update_image)
        self.thread.start()

    def update_image(self, cv_img: np.ndarray, info: dict):
        """
        cv_img is the `frame` from the change_pixmap signal
        """

        # Convert BGR to RGB
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        # Wrap in QImage
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # Display
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
