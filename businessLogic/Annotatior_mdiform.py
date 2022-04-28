# -*- coding: utf-8 -*-
import copy
import os
import sys

basepath = os.path.abspath(os.sep.join([os.path.dirname(__file__), ".."]))
sys.path.append(basepath)
import traceback

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from businessLogic import pickle, user_pickle_path, user_pickle, settings_pickle, jobs_pickle, \
    jobs_pickle_path, image_annotation_pickle, image_annotation_pickle_path
from businessLogic.simple_windows import auth_login, jobs_pull
from ui.Annotator_ui import Ui_AnnotatiorUI
from utils.cvat_api import cvat_service
from utils.thread_manage import thread

'''定义主窗口'''


class mdiform(QMainWindow, Ui_AnnotatiorUI):  # 不可用QMainWindow,因为QLabel继承自QWidget
    download_Signal = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super(mdiform, self).__init__(parent)
        self.setupUi(self)

        self.login_status = False  # 登录状态
        self.auth_login_ui = auth_login(self)  # 登录界面
        url = settings_pickle["cvat_url"]
        self.cvat_service = cvat_service(url)  # cvat服务
        self.jobs_pull_ui = jobs_pull(self)  # jobs 拉取界面
        self.settings_ui = jobs_pull(self)  # jobs 拉取界面

        self.current_jobs_id = None  # jobs id
        self.current_images_id = None  # images id
        self.current_jobs_list_index = -1  # jobs list index
        self.current_images_list_index = -1  # images list index
        self.current_jobs_stage = "annotation"  # jobs的状态 [annotation validation acceptance]

        # region 按钮控件设置 action 然后自动连接到槽： on_控件对象名_信号名(self, 内置参数)
        self.jobs.setDefaultAction(self.action_on_jobs)
        self.pull_jobs.setDefaultAction(self.action_pull_jobs)  # 连接拉取jobs动作
        self.auth_login_ui.loginbutton.setDefaultAction(self.action_login)  # 连接登录动作
        self.jobs_pull_ui.updata_jobs_button.setDefaultAction(self.action_updata_jobs_list)
        self.jobs_pull_ui.download_Button.setDefaultAction(self.action_download_images)

        # 设置信号连接到指定槽
        self.auth_login_ui.remember_checkBox.stateChanged[int].connect(self.on_action_remember)  # 自动保存用户名密码，登录会话
        self.jobs_list.currentIndexChanged.connect(self.action_jobs_list_index_changed)  # 改变 jobs_list 触发
        self.images_list.currentIndexChanged.connect(self.action_images_list_index_changed)  # 改变 images_list 触发
        self.jobs_pull_ui.jobs_list.currentIndexChanged.connect(
            self.action_pull_ui_jobs_list_index_changed)  # 改变 jobs_list 触发

        self.load_local_information()
        # self.load_remote_information()
        # endregion

    # region 主界面功能区
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

            # pickle.dump(jobs_pickle, open(jobs_pickle_path, 'wb'))  # 本地化储存工作列表
            # pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))  # 本地化储存工作列表

    def load_local_information(self):  # 加载本地登录信息
        if user_pickle["user"]:  # 加载本地登录信息
            username = user_pickle["user"]["username"]
            password = user_pickle["user"]["password"]
            if user_pickle["remember"] and username and password:  # 记住密码自动填写
                # if user_pickle["auth_session"]:
                self.cvat_service.load_auth(user_pickle["auth_session"])
                login_status, user = self.cvat_service.user_self()
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

        if jobs_pickle["jobs_details"]:
            for jobs_id, jobs in jobs_pickle["jobs_details"].items():
                task_name = jobs["task_name"]
                project_name = jobs["project_name"]
                # 添加工作项目Item(item_icon, text, obj)
                stage = jobs["stage"]
                size = jobs["stop_frame"] - jobs["start_frame"]
                item_icon = QtGui.QIcon("")
                text = f'{project_name}-{task_name}-{jobs_id}(stage:{stage},size:{size})'
                item_data = {
                    "stage": stage,
                    "jobs_id": jobs_id,
                }
                self.jobs_list.addItem(item_icon, text, item_data)

    # 拉取工作列表到本地任务
    def pull_jobs_list_task(self, cvat_service):
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
                # pickle.dump(jobs_pickle, open(jobs_pickle_path, 'wb'))  # 本地化储存工作列表
                # pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))  # 本地化储存工作列表
            except Exception as e:
                info = traceback.format_exc()
                print(info)
        return {"code": 200, }

    # jobs_list 当前index改变触发
    @pyqtSlot(int)
    def action_jobs_list_index_changed(self, current_index):
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
            if jobs_id in image_annotation_pickle["frames_meta"]:
                current_jobs_images = image_annotation_pickle["frames_meta"][jobs_id]
                if current_jobs_images.keys():
                    self.images_list.clear()
                    for frame_id, images_data in current_jobs_images.items():
                        file_name = images_data["name"]
                        text = file_name
                        if frame_id not in image_annotation_pickle["images"][jobs_id]:
                            text += "(没有下载图像)"
                        data = {
                            "frame_id": frame_id,
                            "jobs_id": jobs_id,
                            "filename": file_name,
                        }
                        # data.update(images_data)
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

    # images_list 当前index改变触发
    @pyqtSlot(int)
    def action_images_list_index_changed(self, current_index):
        itemData = self.images_list.itemData(current_index)
        if itemData:
            frame_id = itemData["frame_id"]
            jobs_id = itemData["jobs_id"]
            if image_annotation_pickle["images"][jobs_id]:
                if frame_id in image_annotation_pickle["images"][jobs_id]:
                    images = image_annotation_pickle["images"][jobs_id][frame_id]
                    tmp = os.path.join(basepath, "tmp.jpg")
                    with open(tmp, "wb") as f:
                        f.write(images)
                    self.show_images.set_image(tmp)
                    os.remove(tmp)

    # endregion

    # region 子线程任务函数

    # 按下载图像注释按钮触发

    # 下载图像注释到本地
    def download_image_annotation_task(self, cvat_service):
        try:
            self.jobs_pull_ui.download_Button.setEnabled(False)
            self.jobs_pull_ui.progressBar.setMaximumSize(QtCore.QSize(16777215, 50))
        except Exception as e:
            info = traceback.format_exc()
            print(info)
        index = self.jobs_pull_ui.jobs_list.currentIndex()
        # import time
        # time.sleep(10)
        if self.login_status:
            try:
                jobs_id = None

                currentData = self.jobs_pull_ui.jobs_list.itemData(index)
                if currentData:
                    if "jobs_id" in currentData:
                        jobs_id = currentData["jobs_id"]

                if jobs_id in image_annotation_pickle["frames_meta"]:
                    current_jobs_frames_meta = copy.deepcopy(image_annotation_pickle["frames_meta"][jobs_id])
                    if current_jobs_frames_meta.keys():
                        size = len(image_annotation_pickle["frames_meta"][jobs_id])
                        annotations = cvat_service.get_jobs_annotations(jobs_id)
                        image_annotation_pickle["annotations"] = annotations
                        pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))
                        i = 0
                        for frame_id, frames_meta in current_jobs_frames_meta.items():
                            images_data = cvat_service.get_jobs_data(jobs_id, frame_id, "frame", "original")
                            image_annotation_pickle["images"][jobs_id][frame_id] = images_data
                            i += 1
                            self.download_Signal.emit(size, i)
                            pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))
                            self.jobs_pull_ui.jobs_list.setCurrentIndex(index)
            except Exception as e:
                info = traceback.format_exc()
                print(info)
        self.jobs_pull_ui.download_Button.setEnabled(True)
        self.jobs_pull_ui.progressBar.setMaximumSize(QtCore.QSize(16777215, 0))

    # 拉取工作列表到本地任务
    def pull_jobs_list_task(self, cvat_service):
        self.jobs_pull_ui.updata_jobs_button.setEnabled(False)
        if self.login_status:
            # 加载加载工作列表
            try:
                jobs_lines = cvat_service.get_jobs_list()
                self.jobs_pull_ui.jobs_list.clear()
                if jobs_lines:
                    jobs_pickle["jobs_details"].clear()
                    image_annotation_pickle["frames_meta"].clear()
                for index, jobs in enumerate(jobs_lines["results"]):
                    jobs_id = jobs["id"]
                    task_id = jobs["task_id"]
                    task_name = jobs["task_name"]
                    project_name = jobs["project_name"]
                    start_frame = jobs['start_frame']
                    stop_frame = jobs['stop_frame']

                    task_meta = self.cvat_service.get_tasks_data_meta(task_id)  # 拉取帧图像信息

                    if jobs_id not in image_annotation_pickle["images"][jobs_id]:
                        image_annotation_pickle["images"][jobs_id] = {}
                    jobs_frames_meta = {}
                    for frame_id in range(start_frame, stop_frame + 1):
                        jobs_frames_meta[frame_id] = task_meta["frames"][frame_id]
                        if jobs_id not in image_annotation_pickle["images"][jobs_id][frame_id]:
                            image_annotation_pickle["images"][jobs_id][frame_id] = None
                    # 需要校验本地和远程的差异性
                    jobs_pickle["jobs_details"][jobs_id] = jobs
                    for lable in jobs["labels"]:
                        lable_id = lable["id"]
                        lable_type = lable["name"]  # 这里在服务端固定名称 [region, tag], 定义到标签是 区域注释标签还是 图片标签，图像标签可以用于分类和文本检测
                        jobs_pickle["jobs_labels"][jobs_id][lable_id] = lable
                    image_annotation_pickle["frames_meta"][jobs_id] = jobs_frames_meta
                    if jobs_id not in image_annotation_pickle["annotation"][jobs_id]:
                        image_annotation_pickle["annotation"][jobs_id] = {}

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

                pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))  # 本地化储存图像注释
                pickle.dump(jobs_pickle, open(jobs_pickle_path, 'wb'))  # 本地化储存工作列表
            except Exception as e:
                info = traceback.format_exc()
                print(info)
        self.jobs_pull_ui.updata_jobs_button.setEnabled(True)

    # endregion

    # region jobs list 拉取界面功能
    @pyqtSlot()
    def on_action_pull_jobs_triggered(self):  # 主界面按下 pull_jobs 显示 jobs list 拉取界面
        current_jobs_id = None
        for jobs_id, jobs in jobs_pickle["jobs_details"].items():  # 加载本地jobs 到 jobs_list
            task_name = jobs["task_name"]
            project_name = jobs["project_name"]
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
        self.jobs_pull_ui.show()

    # 下载变更进度
    @pyqtSlot(int, int)
    def update_download_progress_to_ui(self, total, progress):
        print(total, progress)
        value = int((progress / total) * 100)
        self.jobs_pull_ui.progressBar.setProperty("value", value)

    #  jobs_list index 变化
    @pyqtSlot(int)
    def action_pull_ui_jobs_list_index_changed(self, current_index):  # jobs按下显示登录弹窗
        itemData = self.jobs_pull_ui.jobs_list.itemData(current_index)
        stage = itemData["stage"]
        jobs_id = itemData["jobs_id"]
        self.current_jobs_stage = stage
        self.current_jobs_id = jobs_id
        try:
            if jobs_id in image_annotation_pickle["frames_meta"]:
                current_jobs_images = image_annotation_pickle["frames_meta"][jobs_id]

                if current_jobs_images.keys():
                    self.jobs_pull_ui.images_list.clear()
                    for frame_id, frames_meta in current_jobs_images.items():
                        file_name = frames_meta["name"]
                        text = file_name
                        if frame_id not in image_annotation_pickle["images"][jobs_id]:
                            text += "(没有下载图像)"
                        data = {
                            "frame_id": frame_id,
                            "jobs_id": jobs_id,
                        }
                        self.jobs_pull_ui.images_list.addItem(text, data)
                else:
                    text = "(没有获取图像)"
                    self.jobs_pull_ui.images_list.clear()
                    self.jobs_pull_ui.images_list.addItem(text)
            else:
                text = "(没有获取图像)"
                self.jobs_pull_ui.images_list.clear()
                self.jobs_pull_ui.images_list.addItem(text)
        except Exception as e:
            info = traceback.format_exc()
            print(info)
        # print(current_index, itemData)

    # pull jobs界面按下updata jobs按钮 拉取所有jobs列表
    @pyqtSlot()
    def on_action_updata_jobs_list_triggered(self):
        self.thread_pull_jobs_list_task = thread(self.pull_jobs_list_task, f_args=[self.cvat_service], f_parameter={})
        self.thread_pull_jobs_list_task.start()  # 函数必须要返回 dict

    # pull jobs界面按下 download_images 按钮 下载 jobs images和注释
    @pyqtSlot()
    def on_action_download_images_triggered(self):
        self.download_Signal.connect(self.update_download_progress_to_ui)
        self.thread_download_image_annotation_task = thread(self.download_image_annotation_task,
                                                            f_args=[self.cvat_service], f_parameter={})
        self.thread_download_image_annotation_task.start()  # 函数必须要返回 dict

    # endregion

    # region auth_login 登录界面功能函数
    # 按下登录触发的行为
    @pyqtSlot()
    def on_action_on_jobs_triggered(self):  # jobs按下显示登录弹窗
        self.auth_login_ui.show()

    @pyqtSlot(int)
    def on_action_remember(self, is_checkbox):  # 自动保存密码被按下
        is_checkbox = bool(is_checkbox)
        user_pickle["remember"] = is_checkbox
        pickle.dump(user_pickle, open(user_pickle_path, 'wb'))

    @pyqtSlot()
    def on_action_login_triggered(self):  # 按下登录按钮
        username = self.auth_login_ui.username_dedit.text()
        password = self.auth_login_ui.passwor_dedit.text()
        if not self.login_status and user_pickle["user"]["username"] == username and user_pickle["user"][
            "password"] == password:
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
            print(user_pickle["user"], username, password)
            QMessageBox.warning(self, "登录提示", "用户已经登录不用重新登录", QMessageBox.Yes, QMessageBox.No)
            self.auth_login_ui.close()

    # endregion

    # region 设置界面功能
    @pyqtSlot()
    def on_action_on_jobs_triggered(self):  # jobs按下显示登录弹窗
        self.auth_login_ui.show()
    # endregion

'''主函数'''
if __name__ == "__main__":
    img_name = r"C:\Users\Mayzh\Pictures\1.PNG"
    app = QApplication(sys.argv)
    myshow = mdiform()
    myshow.show()
    myshow.show_images.set_image(img_name)
    sys.exit(app.exec_())
