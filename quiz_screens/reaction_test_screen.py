from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import QTimer, QTime, Qt
import random

class ReactionTestScreen(QWidget):
    def __init__(self, stack, on_finish=None):
        super().__init__()
        self.stack = stack
        self.on_finish = on_finish
        self.trials = 3
        self.results = []
        self.current_trial = 0
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.instruction_label = QLabel(" 반응속도 유형의 테스트가 걸렸습니다.\n"
                                        "'시작' 버튼을 누르면 반응속도 테스트가 시작됩니다.\n"
                                        "총 3번의 진행하고, 평균을 내서 400ms를 넘길 경우 탑승이 거부됩니다")
        self.layout.addWidget(self.instruction_label)

        # 전체 창을 채우는 반응 버튼
        self.test_button = QPushButton("시작")
        self.test_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.test_button.clicked.connect(self.handle_click)
        self.layout.addWidget(self.test_button)

        self.result_label = QLabel("")
        self.layout.addWidget(self.result_label)

        self.setLayout(self.layout)

    def handle_click(self):
        text = self.test_button.text()
        if text == "시작":
            self.start_test()
        elif text == "누르세요":
            self.record_reaction()
        elif text == "다음으로":
            self.next_or_finish()

    def start_test(self):
        delay = random.randint(2000, 5000)
        self.instruction_label.setText("잠시만 기다려주세요...")
        self.test_button.setEnabled(False)
        QTimer.singleShot(delay, self.enable_button)

    def enable_button(self):
        self.instruction_label.setText("지금 누르세요!")
        self.test_button.setText("누르세요")
        self.test_button.setEnabled(True)
        self.test_button.setStyleSheet("background-color: green; font-size: 24px;")
        self.start_time = QTime.currentTime()

    def record_reaction(self):
        end_time = QTime.currentTime()
        reaction_ms = self.start_time.msecsTo(end_time)
        self.results.append(reaction_ms)
        self.instruction_label.setText(f"{self.current_trial+1}회 반응 시간: {reaction_ms} ms")
        self.current_trial += 1
        self.test_button.setText("다음으로")
        self.test_button.setEnabled(True)
        self.test_button.setStyleSheet("")

    def next_or_finish(self):
        if self.current_trial < self.trials:
            self.instruction_label.setText("다음 테스트를 시작하려면 누르세요.")
            self.test_button.setText("시작")
        else:
            avg = sum(self.results) / len(self.results)
            self.instruction_label.setText(f"평균 반응 시간: {avg:.1f} ms")
            if self.on_finish:
                self.on_finish(avg)
            return
        self.test_button.setEnabled(True)
        self.test_button.setStyleSheet("")

