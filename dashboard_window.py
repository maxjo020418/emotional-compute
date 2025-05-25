from typing import Dict
from daeri_window import DaeriWindow
from quiz_window import QuizWindow

from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QMainWindow, QStackedWidget, QDialog, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPainter, QPolygon, QPen, QFont
from PyQt5.QtCore import QPoint, Qt, QTimer, pyqtBoundSignal

import sys
import math
from collections.abc import Callable


class DashWindow(QMainWindow):
    def __init__(self, signals: Dict[str, pyqtBoundSignal]) -> None:
        super().__init__()
        self.signals = signals
        self.setWindowTitle("계기판")
        self.setGeometry(100, 100, 600, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 초기 위젯: 측정 중 (MeasSig)
        self.measuring_ui = MeasSig(self.handle_signal_input)
        self.stack.addWidget(self.measuring_ui)
    

    def handle_signal_input(self, signal):
        if signal == "test_confirm":
            self.test_confirm_ui = TestConfirmDialog(self.handle_signal_input)
            self.stack.addWidget(self.test_confirm_ui)
            self.stack.setCurrentWidget(self.test_confirm_ui)
        elif signal == "MeasSig":
            self.measuring_ui = MeasSig(self.handle_signal_input)
            self.stack.addWidget(self.measuring_ui)
            self.stack.setCurrentWidget(self.measuring_ui)
        elif signal == "shutdown":
            self.shutdown_ui = ShutdownUI()
            self.stack.addWidget(self.shutdown_ui)
            self.stack.setCurrentWidget(self.shutdown_ui)
        # elif signal == "daeri_app":
        #     self.daeri_ui = DaeriWindow()
        #     self.stack.addWidget(self.daeri_ui)
        #     self.stack.setCurrentWidget(self.daeri_ui)
        # elif signal == "quiz":
        #     self.quiz_ui = QuizWindow()
        #     self.stack.addWidget(self.quiz_ui)
        #     self.stack.setCurrentWidget(self.quiz_ui)
        else:
            self.status_ui = StatusUI(signal, self.handle_signal_input)
            self.stack.addWidget(self.status_ui)
            self.stack.setCurrentWidget(self.status_ui)


class MeasSig(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.status = 0
        self.dot_count = 0
        self.switch_callback = switch_callback

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()                

        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_text)
        self.loading_timer.start(500)

    def keyPressEvent(self, a0):
        # 0 입력 시 운전 가능, 1 입력 시 운전 불가능
        if a0.key() == Qt.Key_0:
            self.switch_callback(0)
        elif a0.key() == Qt.Key_1:
            self.switch_callback(1)

    def update_loading_text(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.update()

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("맑은 고딕", 13))

        center_x = self.width() // 2
        center_y = self.height() // 2

        pen = QPen(Qt.red, 4)
        painter.setPen(pen)
        side = 140
        height = math.sqrt(3) / 2 * side
        top_y = center_y - height / 2
        triangle = QPolygon([
            QPoint(center_x, int(top_y)),
            QPoint(center_x - side // 2, int(top_y + height)),
            QPoint(center_x + side // 2, int(top_y + height)),
        ])
        painter.drawPolygon(triangle)

        dot_text = "." * self.dot_count
        lines = ["운전", "가능 여부", f"측정중{dot_text}"]

        painter.setPen(Qt.black)
        fm = painter.fontMetrics()
        line_height = fm.height()
        total_height = line_height * len(lines)
        start_y = center_y - total_height // 2 + line_height + 5

        for i, line in enumerate(lines):
            text_width = fm.horizontalAdvance(line)
            painter.drawText(center_x - text_width // 2, start_y + i * line_height, line)


class StatusUI(QWidget):
    def __init__(self, status: int, switch_callback=None):
        super().__init__()
        self.status = status
        self.dot_count = 0
        self.switch_callback = switch_callback

        self.btn_done = QPushButton("측정완료", self)
        self.btn_done.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 6px;")
        self.btn_done.resize(80, 40)
        self.btn_done.move(80, 80) 

        if status == 1:
            # 불가능일 때만 추가 버튼
            self.btn_retry = QPushButton("재검사", self)
            self.btn_test = QPushButton("2차 테스트", self)
            self.btn_daeri = QPushButton("대리 App", self)

            for i, btn in enumerate([self.btn_retry, self.btn_test, self.btn_daeri]):
                btn.setStyleSheet("background-color: lightgray; border: 2px solid black; border-radius: 6px;")
                btn.resize(80, 40)
                btn.move(400, 20 + i * 50)
            
            self.btn_retry.clicked.connect(self.go_to_MeasSig)
            self.btn_test.clicked.connect(self.go_to_test_confirm)
            self.btn_daeri.clicked.connect(self.go_to_daeri_app)

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("맑은 고딕", 16))

        center_x = self.width() // 2
        center_y = self.height() // 2

        if self.status == 0:
            # 운전 가능 (초록 원)
            pen = QPen(Qt.green, 4)
            painter.setPen(pen)
            radius = 60
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
            lines = ["현재", "운전", "가능"]
        else:
            # 운전 불가능 (빨간 삼각형)
            pen = QPen(Qt.red, 4)
            painter.setPen(pen)
            side = 140
            height = math.sqrt(3) / 2 * side
            top_y = center_y - height / 2
            triangle = QPolygon([
                QPoint(center_x, int(top_y)),
                QPoint(center_x - side // 2, int(top_y + height)),
                QPoint(center_x + side // 2, int(top_y + height)),
            ])
            painter.drawPolygon(triangle)
            lines = ["현재", "운전", "불가능"]

        painter.setPen(Qt.black)
        fm = painter.fontMetrics()
        line_height = fm.height()
        total_height = line_height * len(lines)
        start_y = center_y - total_height // 2 + line_height + 5

        for i, line in enumerate(lines):
            text_width = fm.horizontalAdvance(line)
            painter.drawText(center_x - text_width // 2, start_y + i * line_height, line)

    def go_to_test_confirm(self):
        if self.switch_callback:
            self.switch_callback("test_confirm")  # MainWindow에 신호 전달

    def go_to_MeasSig(self):
        if self.switch_callback:
            self.switch_callback("MeasSig")
    def go_to_daeri_app(self):
        if self.switch_callback:
            self.switch_callback("daeri_app")


class TestConfirmDialog(QDialog):
    def __init__(self, parent_callback: Callable):
        super().__init__()
        self.setWindowTitle("2차 테스트 확인")
        self.setFixedSize(500,200)
        self.parent_callback: Callable = parent_callback

        center_x = self.width() // 2
        center_y = self.height() // 2

        self.label = QLabel("테스트를 진행할까요?", self)
        self.label.setStyleSheet("border: 2px solid red; border-radius: 10px; padding: 10px;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(center_x - 150, center_y - 50, 300, 100)

        self.btn_yes = QPushButton("예")
        self.btn_no = QPushButton("아니요")

        for i, btn in enumerate((self.btn_yes, self.btn_no)):
            btn.setFixedSize(80, 40)
            btn.setStyleSheet("border: 2px solid black; border-radius: 6px; background-color: white;")
            btn.move(center_x - 90 + i * 100, center_y + 10)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.btn_yes)
        h_layout.addWidget(self.btn_no)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(h_layout)
        self.setLayout(layout)

        self.btn_yes.clicked.connect(self.accept)
        self.btn_no.clicked.connect(self.reject_and_notify)

    def accept(self):
        self.accept()
        self.parent_callback("quiz")

    def reject_and_notify(self):
        self.reject()
        self.parent_callback("shutdown")  # MainWindow에 'shutdown' 신호 전달

class ShutdownUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: lightgray;")
        self.label = QLabel("시동을 끕니다", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("맑은 고딕", 25))
        self.label.setStyleSheet("border: 2px solid black; border-radius: 10px; padding: 20px;")
        self.label.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)
