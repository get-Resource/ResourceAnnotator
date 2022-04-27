# -*- coding: utf-8 -*-
import copy
import os
import sys
basepath = os.path.abspath(os.sep.join([os.path.dirname(__file__), ".."]))
sys.path.append(basepath)
import traceback

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from businessLogic import pickle, user_pickle_path, user_pickle, settings_pickle, jobs_pickle, \
    jobs_pickle_path, image_annotation_pickle, image_annotation_pickle_path
from businessLogic.simple_windows import auth_login, jobs_pull
from ui.Annotator_ui import Ui_AnnotatiorUI
from utils.cvat_api import cvat_service
from utils.thread_manage import thread

'''定义主窗口'''


class mdiform(QMainWindow, Ui_AnnotatiorUI):  # 不可用QMainWindow,因为QLabel继承自QWidget
    # finishSignal = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super(mdiform, self).__init__(parent)
        self.setupUi(self)

        self.login_status = False  # 登录状态
        self.auth_login_ui = auth_login(self)  # 登录界面
        url = settings_pickle["cvat_url"]
        self.cvat_service = cvat_service(url)
        self.jobs_pull_ui = jobs_pull(self)  # jobs 拉取界面

        self.current_jobs_id = None  # jobs的状态 annotation validation acceptance
        self.current_jobs_stage = "annotation"  # jobs的状态 annotation validation acceptance

        # region 设置动作，使其自动连接到 action_on_jobs 槽
        self.jobs.setDefaultAction(self.action_on_jobs)
        self.pull_jobs.setDefaultAction(self.action_pull_jobs)  # 连接拉取jobs动作
        self.auth_login_ui.loginbutton.setDefaultAction(self.action_login)  # 连接登录动作
        self.jobs_pull_ui.updata_jobs_button.setDefaultAction(self.action_updata_jobs_list)

        # 设置连接槽
        self.auth_login_ui.remember_checkBox.stateChanged[int].connect(self.on_action_remember)  # 自动保存用户名密码，登录会话
        self.jobs_list.currentIndexChanged.connect(self.action_jobs_list_index_changed)  # 改变 jobs_list 触发

        self.load_local_information()
        # self.load_remote_information()
        # endregion

    # region 自定义功能函数
    def load_remote_information(self):  # 加载远程工作资料(工作列表、图片数据、注释数据)
        if self.login_status:
            # 加载加载工作列表
            jobs_lines = self.cvat_service.get_jobs_list()
            # jobs_pickle["jobs"] = jobs_lines
            for index, jobs in enumerate(jobs_lines["results"]):
                jobs_id = jobs["id"]
                task_id = jobs["task_id"]
                task_name = jobs["task_name"]
                project_name = jobs["project_name"]
                start_frame = jobs['start_frame']
                stop_frame = jobs['stop_frame']

                jobs_pickle["task_details"][task_id] = {}
                jobs_pickle["task_details"][task_id].update({"jobs": jobs})
                task_meta = self.cvat_service.get_tasks_data_meta(task_id)
                jobs_frames_meta = {}
                for frame_id in range(start_frame, stop_frame + 1):
                    jobs_frames_meta[frame_id] = task_meta["frames"][frame_id]
                    # print(jobs_frames_meta)
                jobs_pickle["task_details"][task_id].update({"frames_meta": jobs_frames_meta})

                # 添加工作项目Item(item_icon, text, obj)
                stage = jobs["stage"]
                size = jobs["stop_frame"] - jobs["start_frame"]
                item_icon = QtGui.QIcon("")
                text = f'{project_name}-{task_name}-{jobs_id}(size:{size})'
                item_data = {
                    "stage": stage,
                    "jobs_id": jobs_id,
                }

                #
                image_annotation_pickle["images"][jobs_id] = jobs_frames_meta
                self.jobs_list.addItem(item_icon, text, item_data)

            pickle.dump(jobs_pickle, open(jobs_pickle_path, 'wb'))  # 本地化储存工作列表
            pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))  # 本地化储存工作列表

    def load_local_information(self):  # 加载本地资料
        if user_pickle["user"]:  # 加载本地登录信息
            username = user_pickle["user"]["username"]
            password = user_pickle["user"]["password"]
            if user_pickle["remember"] and username and password:  # 记住密码自动填写
                # if user_pickle["auth_session"]:
                self.cvat_service.load_auth(user_pickle["auth_session"])
                login_status,user = self.cvat_service.user_self()
                self.login_status = login_status
                if not login_status:
                    QMessageBox.warning(self, "登录提示", "用户需要重新登录", QMessageBox.Yes,
                                        QMessageBox.No)
                else:
                    username = user["username"]
                    # password = user["password"]
                    self.auth_login_ui.passwor_dedit.setText(password)
                    self.auth_login_ui.username_dedit.setText(username)
                    self.auth_login_ui.remember_checkBox.setChecked(True)


    def pull_jobs_list_task(self, cvat_service):  # 拉取工作列表到本地
        if self.login_status:
            # 加载加载工作列表
            try:
                jobs_lines = cvat_service.get_jobs_list()
                # jobs_pickle["jobs"] = jobs_lines
                for index, jobs in enumerate(jobs_lines["results"]):
                    print(jobs)
                    jobs_id = jobs["id"]
                    task_id = jobs["task_id"]
                    task_name = jobs["task_name"]
                    project_name = jobs["project_name"]
                    start_frame = jobs['start_frame']
                    stop_frame = jobs['stop_frame']

                    task_meta = self.cvat_service.get_tasks_data_meta(task_id)
                    jobs_frames_meta = {}
                    for frame_id in range(start_frame, stop_frame + 1):
                        jobs_frames_meta[frame_id] = task_meta["frames"][frame_id]
                        # print(jobs_frames_meta)

                    # 添加工作项目Item(item_icon, text, obj)
                    stage = jobs["stage"]
                    size = jobs["stop_frame"] - jobs["start_frame"]
                    item_icon = QtGui.QIcon("")
                    text = f'{project_name}-{task_name}-{jobs_id}(stage:{stage},size:{size})'
                    item_data = {
                        "stage": stage,
                        "jobs_id": jobs_id,
                    }
                    self.jobs_pull_ui.jobs_list.addItem(item_icon, text, item_data)

                    jobs_pickle["task_details"][task_id] = jobs
                    image_annotation_pickle["images"][jobs_id] = jobs_frames_meta
                pickle.dump(jobs_pickle, open(jobs_pickle_path, 'wb'))  # 本地化储存工作列表
                pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))  # 本地化储存工作列表
            except Exception as e:
                info = traceback.format_exc()
                print(info)
        return {"code": 200, }

    # endregion

    # region 自定义信号槽

    # jobs_list 当前index改变触发
    @pyqtSlot(int)
    def action_jobs_list_index_changed(self, current_index):  # jobs按下显示登录弹窗
        itemData = self.jobs_list.itemData(current_index)
        stage = itemData["stage"]
        jobs_id = itemData["jobs_id"]
        self.current_jobs_stage = stage
        self.current_jobs_id = jobs_id
        if stage == "annotation":  # 注释
            pass
        if stage == "validation":  # 验证
            pass
        if stage == "acceptance":  # 验收
            pass
        try:
            if jobs_id in image_annotation_pickle["images"]:
                current_jobs_images = image_annotation_pickle["images"][jobs_id]
                if current_jobs_images.keys():
                    self.images_list.clear()
                    for frame_id, images_data in current_jobs_images.items():
                        file_name = images_data["name"]
                        text = file_name
                        if "images_data" not in images_data:
                            text += "(没有下载图像)"
                        data = {
                            "frame_id": frame_id,
                        }
                        data.update(images_data)
                        self.images_list.addItem(text, data)
                else:
                    text = "(没有获取图像)"
                    self.images_list.addItem(text)
            else:
                text = "(没有获取图像)"
                self.images_list.addItem(text)
        except Exception as e:
            info = traceback.format_exc()
            print(info)
        print(current_index, itemData)
        # jobs_pickle["current_jobs_id"] = jobs_id

    @pyqtSlot(int)
    def on_action_remember(self, is_checkbox):  # jobs按下登录
        is_checkbox = bool(is_checkbox)
        user_pickle["remember"] = is_checkbox
        pickle.dump(user_pickle, open(user_pickle_path, 'wb'))
        # print(is_checkbox)

    # endregion
    # region 自动连接的槽： on_控件对象名_信号名(self, 内置参数)
    @pyqtSlot()
    def on_action_on_jobs_triggered(self):  # jobs按下显示登录弹窗
        self.auth_login_ui.show()

    @pyqtSlot()
    def on_action_updata_jobs_list_triggered(self):  # 在 pull jobs界面按下updata jobs按钮 拉取所有jobs列表
        self.pull_jobs_list_task = thread(self.pull_jobs_list_task, f_args=[self.cvat_service], f_parameter={})
        self.pull_jobs_list_task.start()  # 函数必须要返回 dict

    @pyqtSlot()
    def on_action_pull_jobs_triggered(self):  # pull_jobs 按下显示jobs 拉取弹窗
        self.jobs_pull_ui.show()

    @pyqtSlot()
    def on_action_download_image_annotation_triggered(self):  # 按下载图像注释按钮触发
        if self.login_status:
            jobs_id = self.current_jobs_id
            # self.cvat_service.get_jobs_data()

            if jobs_id in image_annotation_pickle["images"]:
                current_jobs_images = copy.deepcopy(image_annotation_pickle["images"][jobs_id])
                if current_jobs_images.keys():
                    # self.images_list.clear()
                    for frame_id, images_data in current_jobs_images.items():
                        file_name = images_data["name"]
                        text = file_name
                        if "images_data" not in images_data:
                            text += "(没有下载图像)"
                            # image_annotation_pickle["images"][jobs_id]

                            frame_data = self.cvat_service.get_jobs_data(jobs_id, frame_id, "frame", "original")
                            image_annotation_pickle["images"][jobs_id][frame_id]["images_data"] = frame_data
                            tmp = f"./{frame_id}.jpg"
                            with open(tmp, 'wb') as f:
                                f.write(frame_data)
                            self.show_images.set_image(tmp)
                            # os.remove(tmp)
                            return
                        data = {
                            "frame_id": frame_id,
                        }
                        data.update(images_data)
                        # self.images_list.addItem(text, data)
                else:
                    text = "(没有获取图像)"
                    # self.images_list.addItem(text)
            else:
                text = "(没有获取图像)"
                # self.images_list.addItem(text)
        else:
            pass

    # auth_login 登录界面触发的行为

    @pyqtSlot()
    def on_action_login_triggered(self):  # 登录按钮按下到远程登录
        username = self.auth_login_ui.username_dedit.text()
        password = self.auth_login_ui.passwor_dedit.text()
        if not self.login_status and user_pickle["user"]["username"] == username and user_pickle["user"]["password"] == password :
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
                print(username, mes)
                QMessageBox.warning(self, "登录失败", mes, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            print(user_pickle["user"],username,password)
            QMessageBox.warning(self, "登录提示", "用户已经登录不用重新登录", QMessageBox.Yes, QMessageBox.No)
            self.auth_login_ui.close()
    # endregion


'''主函数'''
if __name__ == "__main__":
    img_name = r"C:\Users\Mayzh\Pictures\1.PNG"
    app = QApplication(sys.argv)
    myshow = mdiform()
    myshow.show()
    myshow.show_images.set_image(img_name)
    sys.exit(app.exec_())
