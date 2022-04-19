# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from Annotator_ui import Ui_AnnotatiorUI

'''定义主窗口'''


class myWindow(QMainWindow, Ui_AnnotatiorUI):  # 不可用QMainWindow,因为QLabel继承自QWidget
    def __init__(self, parent=None):
        super(myWindow, self).__init__(parent)
        self.setupUi(self)


'''主函数'''
if __name__ == "__main__":
    img_name = r"C:\Users\Mayzh\Pictures\1.PNG"
    app = QApplication(sys.argv)
    myshow = myWindow()
    myshow.show()
    myshow.show_images.set_image(img_name)
    sys.exit(app.exec_())
