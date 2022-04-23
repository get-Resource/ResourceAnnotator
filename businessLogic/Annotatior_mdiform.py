# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from businessLogic import pickle, user_pickle_path, user_pickle, settings_pickle, jobs_pickle, \
    jobs_pickle_path
from businessLogic.auth_login import auth_login
from ui.Annotator_ui import Ui_AnnotatiorUI
from utils.cvat_api import cvat_service

'''定义主窗口'''


class Mdiform(QMainWindow, Ui_AnnotatiorUI):  # 不可用QMainWindow,因为QLabel继承自QWidget
    def __init__(self, parent=None):
        super(Mdiform, self).__init__(parent)
        self.setupUi(self)

        self.login_status = False
        self.auth_login = auth_login(self)
        url = settings_pickle["cvat_url"]
        self.cvat_service = cvat_service(url)
        self.load_local_information()
        self.load_remote_information()

        # region 设置动作
        self.jobs.setDefaultAction(self.action_on_jobs)

        # auth_login widget
        self.auth_login.loginbutton.setDefaultAction(self.action_login)
        # self.auth_login.remember_checkBox.addAction(self.action_remember)
        self.auth_login.remember_checkBox.stateChanged[int].connect(self.on_action_remember)

        # endregion

    # region 自定义功能函数
    def load_remote_information(self):  # 加载远程工作资料
        if self.login_status:  # 加载本地登录信息
            jobs_lines = self.cvat_service.get_jobs_list()
            jobs_pickle["jobs"] = jobs_lines
            for jobs_id, jobs in enumerate(jobs_lines["results"]):
                # print(json.dumps(jobs,indent=4))
                task_id = jobs["task_id"]
                task = self.cvat_service.get_tasks_data(task_id)
                task_meta = self.cvat_service.get_tasks_data_meta(task_id)
                jobs_pickle["task_details"][task_id] = {}
                jobs_pickle["task_details"][task_id].update({"task": task})
                jobs_pickle["task_details"][task_id].update({"task_meta": task_meta})
                # 需要获取工作名称、项目名称、任务名称
                # print(json.dumps(task,indent=4))
                # task_name = task["name"]
                task_name = jobs["project_id"]
                state = jobs["state"]
                size = jobs["stop_frame"] - jobs["start_frame"]
                self.jobs_list.addItem(QtGui.QIcon(""), f'{task_name}(size:{size})')
            pickle.dump(jobs_pickle, open(jobs_pickle_path, 'wb'))

    def load_local_information(self):  # 加载本地资料
        if user_pickle["user"]:  # 加载本地登录信息
            username = user_pickle["user"]["username"]
            password = user_pickle["user"]["password"]
            if user_pickle["remember"] and username and password:  # 记住密码自动填写
                self.auth_login.passwor_dedit.setText(username)
                self.auth_login.username_dedit.setText(password)
                self.auth_login.remember_checkBox.setChecked(True)
                if user_pickle["auth_session"]:
                    self.cvat_service.load_auth(user_pickle["auth_session"])
                    self.login_status = True

    # auth_login 登录界面触发的行为
    @pyqtSlot(int)
    def on_action_remember(self, ischeckBox):  # jobs按下显示登录弹窗
        ischeckBox = bool(ischeckBox)
        user_pickle["remember"] = ischeckBox
        pickle.dump(user_pickle, open(user_pickle_path, 'wb'))
        # print(ischeckBox)

    # endregion
    # region 自动连接的槽： on_控件对象名_信号名(self, 内置参数)
    @pyqtSlot()
    def on_action_on_jobs_triggered(self):  # jobs按下显示登录弹窗
        self.auth_login.show()

    # auth_login 登录界面触发的行为

    @pyqtSlot()
    def on_action_login_triggered(self):  # 登录按钮按下到远程登录
        username = self.auth_login.username_dedit.text()
        password = self.auth_login.passwor_dedit.text()
        if not self.login_status:
            message, session = self.cvat_service.auth_login(username, password)
            if "key" in message:  # 登录成功
                self.login_status = True
                user_pickle["user"]["username"] = username
                user_pickle["user"]["password"] = password
                user_pickle["auth_key"] = message["key"]
                user_pickle["auth_session"] = session
                pickle.dump(user_pickle, open(user_pickle_path, 'wb'))
                QMessageBox.information(self, "登录成功", "登录成功!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            else:
                mes = ""
                for key, value in message.items():
                    mes += f"{key}:{value}\n"
                QMessageBox.warning(self, "登录失败", mes, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            QMessageBox.warning(self, "登录提示", "用户已经登录不用重新登录", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    # endregion

'''主函数'''
if __name__ == "__main__":
    img_name = r"C:\Users\Mayzh\Pictures\1.PNG"
    app = QApplication(sys.argv)
    myshow = Mdiform()
    myshow.show()
    myshow.show_images.set_image(img_name)
    sys.exit(app.exec_())
