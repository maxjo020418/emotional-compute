# screens/memory_test_screen.py

from typing import Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer
import random

class MemoryTestScreen(QWidget):
    """
    기억력 테스트:
    0) 안내 메시지를 보여줍니다:
       "기억력 테스트가 걸렸습니다.
        *총 3번 진행하는데, 2번 미만으로 맞출 시 탑승이 거부됩니다.
        공의 순서와 색깔을 잘 기억하세요."
    1) '시작' 버튼을 누르면 바로 4개의 컬러 공을 화면에 표시하고 5초 동안 기억 시간을 제공합니다.
    2) 5초 후 공을 숨기고, 콤보박스로 사용자가 본 순서의 색을 선택하게 합니다.
    3) 이 과정을 총 3회 반복하며, 완벽히 맞춘 라운드 수를 셉니다.
    4) on_finish(correct_count) 콜백으로 맞춘 횟수를 전달합니다.
    """
    COLORS = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Black']

    def __init__(self, stack, on_finish: Callable[[int], None] = None):
        super().__init__()
        self.stack = stack
        self.on_finish = on_finish

        self.rounds = 3
        self.current_round = 0
        self.correct_rounds = 0
        self.sequence = []

        # 메인 레이아웃
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # 0) 안내 메시지
        self.notice = QLabel(
            "기억력 테스트가 걸렸습니다.\n"
            "*총 3번 진행하는데, 2번 미만으로 맞출 시 탑승이 거부됩니다.\n"
            "공의 순서와 색깔을 잘 기억하세요."
        )
        self.notice.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.notice)

        # ↓ 시작 버튼 추가
        self.start_btn = QPushButton("시작")
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

        # 테스트 UI: 초기에는 모두 숨김
        self._build_test_ui()
        for w in (self.instruction, self.timer_label,
                  *self.circle_labels, *self.combo_boxes, self.next_btn):
            w.hide()

        # 기억 타이머
        self.mem_timer = QTimer(self)
        self.mem_timer.timeout.connect(self._update_mem_timer)

    def _build_test_ui(self):
        # --- 설명 레이블 ---
        self.instruction = QLabel(
            "동그란 공 4개의 색 순서를 기억하세요."
        )
        self.instruction.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.instruction)

        # --- 타이머 라벨 ---
        self.timer_label = QLabel("")
        self.timer_label.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.timer_label)

        # --- 공 표시 영역 ---
        self.circles_layout = QHBoxLayout()
        self.circle_labels = []
        for _ in range(4):
            frame = QFrame()
            vbox = QVBoxLayout(frame)
            circle = QLabel()
            circle.setFixedSize(50, 50)
            circle.setStyleSheet("border-radius:25px; background: gray;")
            vbox.addWidget(circle, alignment=Qt.AlignCenter)
            self.circle_labels.append(circle)
            self.circles_layout.addWidget(frame)
        self.layout.addLayout(self.circles_layout)

        # --- 콤보박스 영역 ---
        self.slot_layout = QHBoxLayout()
        self.combo_boxes = []
        for _ in range(4):
            box = QComboBox()
            self.combo_boxes.append(box)
            self.slot_layout.addWidget(box)
        self.layout.addLayout(self.slot_layout)

        # --- 제출 버튼 ---
        self.next_btn = QPushButton("제출")
        self.next_btn.clicked.connect(self._submit_answer)
        self.layout.addWidget(self.next_btn, alignment=Qt.AlignCenter)

    def _on_start_clicked(self):
        # ‘시작’ 누르면 바로 첫 라운드 시작
        self.start_btn.hide()
        self.notice.hide()
        self._start_round()

    def _start_round(self):
        # 이전 notice 숨기기
        self.notice.hide()

        # 라운드 UI 보여주기
        self.instruction.show()
        self.timer_label.show()
        for c in self.circle_labels:
            c.show()

        # 시퀀스 생성 및 공 색 표시
        self.sequence = random.sample(self.COLORS, 4)
        for color, circle in zip(self.sequence, self.circle_labels):
            circle.setStyleSheet(f"border-radius:25px; background: {color.lower()};")

        # 5초 기억 타이머
        self.remaining = 5
        self.timer_label.setText(f"남은 시간: {self.remaining}초")
        self.mem_timer.start(1000)

    def _update_mem_timer(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.mem_timer.stop()
            # 공 숨기기
            for c in self.circle_labels:
                c.setStyleSheet("border-radius:25px; background: lightgray;")
            self.timer_label.hide()
            # 콤보·제출 보이기
            for box in self.combo_boxes:
                box.clear()
                box.addItems(self.sequence)
                box.show()
            self.next_btn.show()
        else:
            self.timer_label.setText(f"남은 시간: {self.remaining}초")

    def _submit_answer(self):
        # 정답 체크
        selected = [box.currentText() for box in self.combo_boxes]
        if selected == self.sequence:
            self.correct_rounds += 1
        self.current_round += 1

        # 현재 라운드 UI 숨기기
        self.instruction.hide()
        self.timer_label.hide()
        for c in self.circle_labels:
            c.hide()
        for box in self.combo_boxes:
            box.hide()
        self.next_btn.hide()

        # 다음 라운드 or 종료
        if self.current_round < self.rounds:
            # 대기 메시지 표시
            self.notice.setText("잠시만 기다려주세요...")
            self.notice.show()
            # 5초 뒤 바로 다음 라운드 시작
            QTimer.singleShot(5000, self._start_round)
        else:
            if self.on_finish:
                self.on_finish(self.correct_rounds)
            self.stack.setCurrentIndex(0)
