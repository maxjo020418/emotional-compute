from typing import Dict

from PyQt5.QtCore import pyqtBoundSignal
from PyQt5.QtWidgets import QWidget

class DashWindow(QWidget):
    def __init__(self, signals: Dict[str, pyqtBoundSignal]) -> None:
        super().__init__()
        self.setWindowTitle("계기판")
        self.signals = signals
        """ SIGNALS:
        'video_stream' -> returns: (np.ndarray, dict)
        'is_drunk', 'quiz', 'daeri'
        'stop_btn', 'acc_btn', 'ign_btn'
        """

        # test
        self.resize(400, 300)
        signals['ign_btn'].connect(self.is_ign)

        # 알림용 __init__ 마지막에 두기
        print('\nDashWindow Thread READY\n' + '=' * 25)
    
    @staticmethod
    def is_ign():
        print('ign called!')