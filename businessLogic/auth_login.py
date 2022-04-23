from PyQt5.QtWidgets import QWidget

from ui.auth_login import Ui_auth_login


class auth_login(QWidget, Ui_auth_login):
    def __init__(self, parent=None):
        # super().__init__()
        super(auth_login, self).__init__()
        self.setupUi(self)  # 构造UI界面
