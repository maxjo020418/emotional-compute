import sys
import cv2
import numpy as np
from typing import Tuple, Dict
from pathlib import Path

# from ferp.libs.Face import FacialLandmarkDetector
# from ferp.libs.FacialExpression import DataAnalyzer
# import ferp.libs.Face as Face

from deepface import DeepFace

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QSlider, QVBoxLayout, QHBoxLayout
)

from dashboard_window import DashWindow
from quiz_window import QuizWindow
from daeri_window import DaeriWindow

here = Path(__file__).resolve().parent
frontal = here / 'db' / 'xml' / 'haarcascade_frontalface_alt2.xml'
eye = here / 'db' / 'xml' / 'haarcascade_eye_tree_eyeglasses.xml'

class VideoThread(QThread):
    change_pixmap: pyqtSignal = pyqtSignal(np.ndarray, dict)

    face_cascade = cv2.CascadeClassifier(str(frontal))
    eyes_cascade = cv2.CascadeClassifier(str(eye))

    MODE = 1
    frame_check = 0  # 중간에 frame skipping 룔으로

    def run(self):
        cap = cv2.VideoCapture(0)
        print(type(self.change_pixmap))
        print(cap)

        while True:
            ret, frame = cap.read()  # bool, ndarray

            if ret and self.frame_check >= 60:
                detection_funcs = [
                    self.detect_face_cv,
                    self.detect_face_deepface,
                ]
                self.change_pixmap.emit(*detection_funcs[self.MODE](frame))
            
            elif ret:
                self.change_pixmap.emit(frame, {})
            
            self.frame_check += 1

    def detect_face_cv(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)

        info = dict()

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

    @staticmethod
    def detect_face_deepface(frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        analyze_data = DeepFace.analyze(frame, 
                                        actions = [
                                            # 'age', 
                                            'emotion'
                                        ], 
                                        enforce_detection=False,
                                        silent=True,
                                        )[0]
        # find_data = DeepFace.find(frame, './db')
        # info['df'] = find_data

        dummy = {'x': 0, 'y': 0, 'w': 0, 'h': 0, 'left_eye': (0, 0), 'right_eye': (0, 0)}
        region = analyze_data.get('region', dummy)

        # Draw on face
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        cv2.rectangle(frame, top_left, bottom_right, color=(0, 255, 0), thickness=2)

        # Draw on eyes
        for eye in ["left_eye", "right_eye"]:
            center = region[eye]
            if center != (0, 0):  # Ensure the eye was detected
                cv2.circle(frame, center, radius=10, color=(255, 0, 0), thickness=2)

        return frame, analyze_data


class BackstageWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('백스테이지 console')

        # video widget
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background: black;")

        # dash panel
        self.stop_btn = QPushButton("Stop")
        self.acc_btn = QPushButton("Acc")
        self.ign_btn = QPushButton("Ignition")

        # manual action panel
        self.is_drunk_btn = QPushButton("Drunk")
        self.quiz_btn = QPushButton("Quiz")
        self.daeri_btn = QPushButton("Daeri")

        self.quiz_btn.clicked.connect(self.show_quiz)
        self.daeri_btn.clicked.connect(self.show_daeri)

        # info panel
        self.emotion_stat = QLabel("test")

        # dash panel layouts
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.ign_btn)
        btn_layout.addWidget(self.acc_btn)

        # set manual action button layouts
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.is_drunk_btn)
        action_layout.addWidget(self.quiz_btn)
        action_layout.addWidget(self.daeri_btn)

        # vertical main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(action_layout)
        main_layout.addWidget(self.emotion_stat)

        self.setLayout(main_layout)

        # Start video thread
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap.connect(self.update_image)
        self.video_thread.start()

        # other windows (quiz, daeri):
        # MUST PUT AT BOTTOM (get_signals)
        self.qw = QuizWindow(self.get_signals())
        self.dw = DaeriWindow(self.get_signals())
        self.dash = DashWindow(self.get_signals())

        self.dash.show()

        print('\nBackstage Thread READY\n' + '='*25)

    def get_signals(self) -> Dict[str, pyqtSignal]:
        return \
            {
                'video_stream': self.video_thread.change_pixmap,

                'is_drunk': self.is_drunk_btn.clicked,
                'quiz': self.quiz_btn.clicked,
                'daeri': self.daeri_btn.clicked,

                'stop_btn': self.stop_btn.clicked,
                'acc_btn': self.acc_btn.clicked,
                'ign_btn': self.ign_btn.clicked,
            }

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

        # Display info
        self.emotion_stat.setText(info.get('dominant_emotion'))

    def show_quiz(self):
        self.qw.show()

    def show_daeri(self):
        self.dw.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BackstageWin()
    win.show()
    sys.exit(app.exec_())
