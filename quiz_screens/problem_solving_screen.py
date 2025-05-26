# quiz_screens/problem_solving_screen.py

from typing import Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QButtonGroup, QRadioButton, QPushButton
)
from PyQt5.QtCore import Qt, QTimer
import random

class ProblemSolvingScreen(QWidget):
    """
    간단한 문제 10문제를 랜덤 순서로 제공하고, 제한시간(10초) 내 응답을 받음
    정답 개수를 on_finish 콜백으로 전달
    """
    def __init__(self, stack, on_finish: Callable[[int], None] = None):
        super().__init__()
        self.stack     = stack
        self.on_finish = on_finish

        # — 퀴즈 준비 —
        full_questions = [
            ("35에 +1을 하고 -1을 한 뒤 다시 +1을 하면?", ["34", "35", "36", "37"], 2),
            ("1=1, 2=4, 3=9, 4=? 이 때 ?에 들어갈 값은?", ["1", "4", "8", "16"], 3),
            ("서울의 강 이름은?", ["한강", "금강", "영산강", "낙동강"], 0),
            ("희철이가 1000원을 가지고 있었는데 영민이가 500원을 빌려갈 경우 남은 돈은 얼마인가?", ["0원", "500원", "1000원", "1500원"], 1),
            ("물의 화학식은?", ["CO2", "H2O", "O2", "NaCl"], 1),
            ("10kg은 몇 g인가?", ["100g", "1000g", "10000g", "100000g"], 2),
            ("1킬로미터는 몇 미터인가?", ["100m", "1000m", "10000m", "100000m"], 1),
            ("다음 중 과일이 아닌 것은?", ["사과", "배", "포도", "배추"], 3),
            ("1+1^2+1 = ?", ["3", "2", "1", "4"], 0),
            ("0.1L는 몇 ml인가?", ["10ml", "100ml", "1000ml", "10000ml"], 1),
            ("7 + 8 = ?", ["14", "15", "16", "17"], 1),
            ("12 - 5 = ?", ["6", "7", "8", "9"], 1),
            ("6 × 4 = ?", ["20", "22", "24", "26"], 2),
            ("81 ÷ 9 = ?", ["7", "8", "9", "10"], 2),
            ("15 + 27 = ?", ["40", "41", "42", "43"], 2),
            ("50 - 18 = ?", ["30", "32", "34", "36"], 1),
            ("9 × 7 = ?", ["54", "60", "63", "66"], 2),
            ("48 ÷ 6 = ?", ["6", "7", "8", "9"], 2),
            ("14 + 19 = ?", ["31", "32", "33", "34"], 2),
            ("100 - 45 = ?", ["50", "52", "55", "57"], 2),
        ]
        self.questions  = random.sample(full_questions, 10)
        self.current    = 0
        self.score      = 0
        self.time_limit = 10
        self.remaining  = self.time_limit

        # — 타이머 설정 —
        # (1) 문제 풀이 제한 시간 (1초 단위)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        # — 레이아웃 준비 —
        main_layout = QVBoxLayout(self)

        # (A) Notice 화면 + 시작 버튼
        self.notice = QLabel(
            "판단력 유형 테스트가 걸렸습니다\n"
            "* '시작' 버튼을 누르면 바로 퀴즈가 시작됩니다.\n"
            "* 80점 미만일 경우 탑승이 거부됩니다."
        )
        self.notice.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.notice)

        self.start_btn = QPushButton("시작")
        self.start_btn.clicked.connect(self._on_start_clicked)
        main_layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

        # (B) Quiz 화면
        self.quiz_page = QWidget()
        quiz_layout = QVBoxLayout(self.quiz_page)
        quiz_layout.setAlignment(Qt.AlignTop)

        # 타이머 라벨
        self.timer_label = QLabel(f"남은 시간: {self.time_limit}초")
        quiz_layout.addWidget(self.timer_label)
        # 질문 라벨
        self.question_label = QLabel("")
        quiz_layout.addWidget(self.question_label)
        # 보기(라디오 버튼)
        self.button_group = QButtonGroup(self.quiz_page)
        self.options = []
        for idx in range(4):
            rb = QRadioButton("")
            self.button_group.addButton(rb, idx)
            quiz_layout.addWidget(rb)
            self.options.append(rb)
        # 다음(제출) 버튼
        self.next_btn = QPushButton("다음")
        self.next_btn.clicked.connect(lambda: self._answer(False))
        quiz_layout.addWidget(self.next_btn)

        # 처음엔 숨김
        self.quiz_page.hide()
        main_layout.addWidget(self.quiz_page)

        self.setLayout(main_layout)

    def _on_start_clicked(self):
        # 시작 버튼 눌리면 바로 퀴즈 화면으로 전환
        self.start_btn.hide()
        self.notice.hide()
        self.quiz_page.show()
        self._load_question()

    def _load_question(self):
        q, opts, ans = self.questions[self.current]
        self.question_label.setText(f"Q{self.current+1}. {q}")
        for rb, text in zip(self.options, opts):
            rb.setText(text)
            rb.setChecked(False)

        # 타이머 리셋 후 시작
        self.remaining = self.time_limit
        self.timer_label.setText(f"남은 시간: {self.remaining}초")
        self.timer.start(1000)

    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
            self._answer(auto=True)
        else:
            self.timer_label.setText(f"남은 시간: {self.remaining}초")

    def _answer(self, auto: bool):
        picked  = self.button_group.checkedId() if not auto else -1
        correct = self.questions[self.current][2]
        if picked == correct:
            self.score += 1

        self.current += 1
        self.timer.stop()

        if self.current < len(self.questions):
            # 즉시 다음 문제 로드
            self._load_question()
        else:
            if self.on_finish:
                self.on_finish(self.score)
            self.stack.setCurrentIndex(0)
