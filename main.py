from PyQt5.QtWidgets import QApplication
import sys

from cam_backstage import BackstageWin

"""
별도로 윈도우 테스트시에는
__name__ == "__main__" guard로 감싸서 하고
모두 다 테스트할 경우에는 이 main.py총해서 돌리기
"""

"⬇️⬇️⬇️ DEBUG ⬇️⬇️⬇️"
VID_DEBUG = True

app = QApplication(sys.argv)

win = BackstageWin(VID_DEBUG)
win.show()
sys.exit(app.exec_())
