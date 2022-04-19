import sys

from PyQt5.Qt import QPixmap, QPoint, Qt, QPainter
from PyQt5.QtWidgets import QWidget, QApplication


class ImageBox(QWidget):
    def __init__(self):
        super(ImageBox, self).__init__()
        self.img = None
        self.scaled_img = None
        self.point = QPoint(0, 0)
        self.start_pos = None
        self.end_pos = None
        self.left_click = False
        self.scale = 1

    def init_ui(self):
        self.setWindowTitle("ImageBox")

    def set_image(self, img_path):
        """
        open image file
        :param img_path: image file path
        :return:
        """
        # img = QImageReader(img_path)
        # img.setScaledSize(QSize(self.size().width(), self.size().height()))
        # img = img.read()
        self.img = QPixmap(img_path)
        self.scaled_img = self.img

    def paintEvent(self, e):
        """
        接受绘画活动
        :param e: QPaintEvent
        :return:
        """
        if self.scaled_img:
            painter = QPainter()
            painter.begin(self)
            painter.scale(self.scale, self.scale)
            painter.drawPixmap(self.point / self.scale, self.scaled_img)
            painter.end()

    def mouseMoveEvent(self, e):
        """
        小部件的鼠标移动事件
        :param e: QMouseEvent
        :return:
        """
        if self.left_click and QApplication.keyboardModifiers() == Qt.ControlModifier:  # ctrl + 右击按住移动
            size = self.size().width()
            self.end_pos = e.pos() - self.start_pos
            self.point = self.point + self.end_pos
            self.start_pos = e.pos()
            self.repaint()

    def mousePressEvent(self, e):
        """
        小部件的鼠标按下事件
        :param e: QMouseEvent
        :return:
        """
        if e.button() == Qt.LeftButton:
            self.left_click = True
            self.start_pos = e.pos()

    def mouseReleaseEvent(self, e):
        """
        小部件的鼠标释放事件
        :param e: QMouseEvent
        :return:
        """
        if e.button() == Qt.LeftButton:
            self.left_click = False

    def wheelEvent(self, event):

        angle = event.angleDelta() / 8  # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
        angleY = angle.y()
        if angle and QApplication.keyboardModifiers() == Qt.ControlModifier:
            # 获取当前鼠标相对于view的位置
            if angleY > 0 and self.scale < 2:
                self.scale *= 1.1
            elif angleY < 0 and self.scale > 0.3:  # 滚轮下滚
                self.scale *= 0.9
            self.adjustSize()
            self.update()

    def keyPressEvent(self, event):
        print("按下：" + str(event.key()), Qt.Key_Control)
        print(QApplication.keyboardModifiers(), Qt.ControlModifier,
              QApplication.keyboardModifiers() == Qt.ShiftModifier)
        # if QApplication.keyboardModifiers() == Qt.ControlModifier:
        #         self.actionFile.save(self.action_text.toPlainText())
        #         self.status.showMessage("保存成功 %s" % self.file)


if __name__ == '__main__':
    img_name = r"C:\Users\Mayzh\Pictures\1.PNG"
    app = QApplication(sys.argv)
    box = ImageBox()
    box.show()
    box.set_image(img_name)
    app.exec_()
