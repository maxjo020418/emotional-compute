# quiz_window.py
from typing import Dict
import sys
import random
from PyQt5.QtWidgets import QWidget, QStackedLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtBoundSignal

# 각 퀴즈별 화면 클래스 임포트
from screens.reaction_test_screen import ReactionTestScreen
from screens.problem_solving_screen import ProblemSolvingScreen

class QuizWindow(QWidget):
    def __init__(self, signals: Dict[str, pyqtBoundSignal]) -> None:
        super().__init__()
        self.setWindowTitle("음주 측정 퀴즈 선택창")
        self.signals = signals

        # 화면 스택 설정
        self.stack = QStackedLayout(self)

        # 메인 안내 페이지
        self.main_page = QWidget()
        main_layout = QVBoxLayout(self.main_page)
        main_layout.addWidget(QLabel("음주 측정 퀴즈를 시작하겠습니다."))
        main_layout.addWidget(QLabel("*3번의 반응속도 결과의 평균을 구해 400ms가 안될 경우 차량 탑승이 거부됩니다."))
        main_layout.addWidget(QLabel("*문제를 풀게되실 경우 80점 초과가 아닐 경우 탑승이 거부됩니다."))
        main_layout.addWidget(QLabel("*문제 유형은 무작위입니다."))

        start_btn = QPushButton("퀴즈 시작")
        start_btn.clicked.connect(self.start_random_quiz)
        main_layout.addWidget(start_btn)
        self.stack.addWidget(self.main_page)

        # 구현된 퀴즈만 리스트에 추가
        self.screens = [
            ReactionTestScreen(self.stack, on_finish=self._handle_reaction),
            ProblemSolvingScreen(self.stack, on_finish=self._handle_problem)
        ]
        for screen in self.screens:
            self.stack.addWidget(screen)

        self.setLayout(self.stack)
        self.stack.setCurrentWidget(self.main_page)

    def start_random_quiz(self):
        # 구현된 퀴즈 중 랜덤 선택하여 화면 전환
        quiz_screen = random.choice(self.screens)
        self.stack.setCurrentWidget(quiz_screen)

    def _next_screen(self):
        idx = self.stack.currentIndex() + 1
        if idx < self.stack.count():
            self.stack.setCurrentIndex(idx)
        else:
            self._finish_quiz()

    def _handle_reaction(self, average_reaction_ms: float):
        # 평균 반응시간을 받아 처리
        print(f"[결과] 평균 반응 속도: {average_reaction_ms:.1f}ms")
        # 판단 기준: 400ms 초과면 프로세스 종료
        if average_reaction_ms > 400:
            QMessageBox.warning(self, "결과", "반응 속도가 너무 느립니다. 차량 운전이 거부됩니다.") #ign_btn
            sys.exit(0)
        else:
            QMessageBox.information(self, "결과", "운전이 가능합니다.") #acc_btn
            self.close()

    def _handle_problem(self, score: int):
        # 인지 능력 테스트 결과 처리 (10점 만점)
        print(f"[결과] 인지 능력 점수: {score}점")
        if score < 8:
            QMessageBox.warning(self, "결과", "점수가 부적합합니다. 차량 운전이 거부됩니다.")
            sys.exit(0)
        else:
            QMessageBox.information(self, "결과", "운전이 가능합니다.")
            self.close()

    def _finish_quiz(self):
        # 퀴즈 종료 후 처리
        self.signals['quiz'].emit(-1)
        self.stack.setCurrentWidget(self.main_page)
