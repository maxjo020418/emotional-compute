from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QButtonGroup, QRadioButton, QPushButton
from PyQt5.QtCore import Qt, QTimer
import random

class ProblemSolvingScreen(QWidget):
    """
    간단한 문제 10문제를 랜덤 순서로 제공하고, 제한시간(10초) 내 응답을 받음
    정답 개수를 on_finish에 전달
    """
    def __init__(self, stack, on_finish=None):
        super().__init__()
        self.stack = stack
        self.on_finish = on_finish
        self.questions = [
            ("35에 +1을 하고 -1을 한 뒤 다시 +1을 하면?", ["34", "35", "36", "37"], 2),
            ("1=1, 2=4, 3=9, 4=? 이 때 ?에 들어갈 값은?", ["1", "4", "8", "16"], 3),
            ("서울의 강 이름은?", ["한강", "금강", "영산강", "낙동강"], 0),
            ("희철이가 1000원을 가지고 있었는데 영민이가 500원을 빌려갈 경우 남은 돈은 얼마인가?", ["0원", "500원", "1000원", "1500원"], 1),
            ("물의 화학식은?", ["CO2", "H2O", "O2", "NaCl"], 1),
            ("10kg은 몇 g인가?", ["100g", "1000g", "10000g", "100000g"], 2),
            ("1킬로미터는 몇 미터인가?", ["100m", "1000m", "10000m", "100000m"], 1),
            ("다음 중 과일이 아닌 것은?", ["사과", "배", "포도", "배추"], 3),
            ("1+1^2+1 = ?", ["3", "2", "1", "4"], 0),
            ("0.1L는 몇 ml인가?", ["10ml", "100ml", "1000ml", "10000ml"], 1)
        ]
        random.shuffle(self.questions)
        self.current = 0
        self.score = 0
        self.time_limit = 10
        self.remaining = self.time_limit
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # 타이머 레이블
        self.timer_label = QLabel(f"남은 시간: {self.remaining}초")
        self.layout.addWidget(self.timer_label)

        # 질문 레이블
        self.question_label = QLabel("")
        self.layout.addWidget(self.question_label)

        # 선택지 라디오 버튼
        self.button_group = QButtonGroup(self)
        self.options = []
        for i in range(4):
            rb = QRadioButton("")
            self.button_group.addButton(rb, i)
            self.layout.addWidget(rb)
            self.options.append(rb)

        # 다음 버튼
        self.next_button = QPushButton("다음")
        self.next_button.clicked.connect(lambda: self.next_question(auto=False))
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)
        self.load_question()

    def start_timer(self):
        self.remaining = self.time_limit
        self.timer_label.setText(f"남은 시간: {self.remaining}초")
        self.timer.start(1000)

    def _update_timer(self):
        # 1초마다 호출: 남은 시간 감소 및 화면 갱신
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
            # 시간 초과 시 자동 제출
            self.next_question(auto=True)
        else:
            self.timer_label.setText(f"남은 시간: {self.remaining}초")

    def load_question(self):
        q, opts, ans = self.questions[self.current]
        self.question_label.setText(f"Q{self.current+1}. {q}")
        for rb, text in zip(self.options, opts):
            rb.setText(text)
            rb.setChecked(False)
        self.start_timer()

    def next_question(self, auto=False):
        correct = self.questions[self.current][2]
        selected = self.button_group.checkedId() if not auto else -1
        if selected == correct:
            self.score += 1
        self.current += 1
        if self.current < len(self.questions):
            self.load_question()
        else:
            self.timer.stop()
            if self.on_finish:
                self.on_finish(self.score)
            self.stack.setCurrentIndex(0)