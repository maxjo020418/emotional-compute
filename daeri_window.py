from typing import Dict
import webbrowser

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

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        self._create_question_screen(main_layout)
        # _create_connecting_screen은 이제 _open_daeri_website에서 직접 처리하므로 필요 없음
        self._create_warning_screen(main_layout)
        self._create_shutdown_screen(main_layout)

        self.setLayout(main_layout)
        self.show_question_screen()

    def _create_question_screen(self, parent_layout):

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
        self.yes_button.clicked.connect(self._open_daeri_website)

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

    # _create_connecting_screen 메서드 삭제

    def _create_warning_screen(self, parent_layout):

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
        self.question_widget.hide()

        self.warning_widget.hide()
        self.shutdown_widget.hide()

    def show_question_screen(self):
        self._hide_all_screens()
        self.question_widget.show()

    def _open_daeri_website(self):
        daeri_url = "https://www.google.com/maps/search/%EB%8C%80%EB%A6%AC%EC%9A%B4%EC%A0%84?entry=ttu&g_ep=EgoyMDI1MDUyOC4wIKXMDSoASAFQAw%3D%3D"
        try:
            webbrowser.open(daeri_url)
            QMessageBox.information(self, "대리운전 시연", f"대리운전 서비스를 시연하기 위해 웹 브라우저를 엽니다:\n{daeri_url}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"웹 브라우저를 여는 데 실패했습니다: {e}")
        finally:
            self.close()


    def show_warning_screen(self):

        self._hide_all_screens()
        self.warning_widget.show()

    def _handle_ignition_after_warning(self):

        QMessageBox.warning(self, "시동 차단", "음주 상태이므로 시동이 차단됩니다.")
        self.close()

    def show_shutdown_message(self):

        self._hide_all_screens()
        self.shutdown_widget.show()
        QMessageBox.information(self, "시동 끄기", "차량 시동이 꺼집니다.")
        self.close()