from PyQt5.QtWidgets import QApplication
import sys

from cam_backstage import BackstageWin

app = QApplication(sys.argv)

win = BackstageWin()
win.show()
sys.exit(app.exec_())
