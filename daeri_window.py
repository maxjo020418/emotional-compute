from typing import Dict

from PyQt5.QtCore import pyqtBoundSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout


class DaeriWindow(QWidget):
    def __init__(self, signals: Dict[str, pyqtBoundSignal]) -> None:
        super().__init__()
        self.setWindowTitle("대리운전화면")
        self.signals = signals
        self.resize(400, 300)
        self._setup_ui()
        print('\nDaeriWindow Thread READY\n' + '=' * 25)

    def _setup_ui(self):
        #ui설정 위젯 생성
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        self._create_question_screen(main_layout)
        self._create_connecting_screen(main_layout)
        self._create_warning_screen(main_layout)
        self._create_shutdown_screen(main_layout)

        self.setLayout(main_layout)
        self.show_question_screen()

    def _create_question_screen(self, parent_layout):
        #질문 화면 생성
        self.question_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.question_label = QLabel("대리 운전 어플을\n열겠습니까?")
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.question_label)

        button_hbox = QHBoxLayout()
        self.yes_button = QPushButton("예")
        self.yes_button.setFixedSize(120, 50)
        self.yes_button.setStyleSheet(
            "font-size: 20px; padding: 10px; background-color: #4CAF50; color: white; border-radius: 10px;")
        self.yes_button.clicked.connect(self.show_connecting_screen)

        self.no_button = QPushButton("아니오")
        self.no_button.setFixedSize(120, 50)
        self.no_button.setStyleSheet(
            "font-size: 20px; padding: 10px; background-color: #f44336; color: white; border-radius: 10px;")
        self.no_button.clicked.connect(self.show_warning_screen)

        button_hbox.addStretch(1)
        button_hbox.addWidget(self.yes_button)
        button_hbox.addSpacing(20)
        button_hbox.addWidget(self.no_button)
        button_hbox.addStretch(1)

        layout.addLayout(button_hbox)
        self.question_widget.setLayout(layout)
        parent_layout.addWidget(self.question_widget)

    def _create_connecting_screen(self, parent_layout):
        #대리 연결중 화면
        self.connecting_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.connecting_label = QLabel("대리 어플 접속 중...")
        self.connecting_label.setAlignment(Qt.AlignCenter)
        self.connecting_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.connecting_label)

        self.connecting_widget.setLayout(layout)
        parent_layout.addWidget(self.connecting_widget)
        self.connecting_widget.hide()

    def _create_warning_screen(self, parent_layout):
        #경고문 화면
        self.warning_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.warning_label = QLabel(
            "음주운전시 최대\n2년 이상 5년 이하의 징역이나\n"
            "1천만원 이상 2천만원 이하의 벌금이 부과됩니다.\n"
            "그래도 시동 거시겠습니까?"
        )
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet("font-size: 18px; color: red; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.warning_label)

        button_hbox = QHBoxLayout()
        self.warning_yes_button = QPushButton("예")
        self.warning_yes_button.setFixedSize(120, 50)
        self.warning_yes_button.setStyleSheet(
            "font-size: 20px; padding: 10px; background-color: #f44336; color: white; border-radius: 10px;")
        self.warning_yes_button.clicked.connect(self._handle_ignition_after_warning)

        self.warning_no_button = QPushButton("아니오")
        self.warning_no_button.setFixedSize(120, 50)
        self.warning_no_button.setStyleSheet(
            "font-size: 20px; padding: 10px; background-color: #4CAF50; color: white; border-radius: 10px;")
        self.warning_no_button.clicked.connect(self.show_shutdown_message)

        button_hbox.addStretch(1)
        button_hbox.addWidget(self.warning_yes_button)
        button_hbox.addSpacing(20)
        button_hbox.addWidget(self.warning_no_button)
        button_hbox.addStretch(1)

        layout.addLayout(button_hbox)
        self.warning_widget.setLayout(layout)
        parent_layout.addWidget(self.warning_widget)
        self.warning_widget.hide()

    def _create_shutdown_screen(self, parent_layout):
        #시동차단 화면
        self.shutdown_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.shutdown_label = QLabel("시동을 끕니다")
        self.shutdown_label.setAlignment(Qt.AlignCenter)
        self.shutdown_label.setStyleSheet("font-size: 24px; font-weight: bold; color: blue;")
        layout.addWidget(self.shutdown_label)

        self.shutdown_widget.setLayout(layout)
        parent_layout.addWidget(self.shutdown_widget)
        self.shutdown_widget.hide()

    def _hide_all_screens(self):
        #화면숨기기
        self.question_widget.hide()
        self.connecting_widget.hide()
        self.warning_widget.hide()
        self.shutdown_widget.hide()

    def show_question_screen(self):
        self._hide_all_screens()
        self.question_widget.show()

    def show_connecting_screen(self):
        #질문 화면연결
        self._hide_all_screens()
        self.connecting_widget.show()
        QMessageBox.information(self, "대리 호출", "대리운전 어플로 이동합니다.")
        self.close()

    def show_warning_screen(self):
        #경고화면연결
        self._hide_all_screens()
        self.warning_widget.show()

    def _handle_ignition_after_warning(self):\
        #차단화면연결
        QMessageBox.warning(self, "시동 차단", "음주 상태이므로 시동이 차단됩니다.")
        self.close()

    def show_shutdown_message(self):
        #끄기화면연결
        self._hide_all_screens()
        self.shutdown_widget.show()
        QMessageBox.information(self, "시동 끄기", "차량 시동이 꺼집니다.")
        self.close()