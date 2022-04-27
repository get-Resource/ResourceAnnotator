import traceback

from PyQt5.QtCore import QThread, pyqtSignal


class thread(QThread):  # 定义一个工作线程，后面会调用和重写
    # 使用信号和UI主线程通讯，参数是发送信号时附带参数的数据类型，可以是str、int、list等
    finishSignal = pyqtSignal(int)

    def __init__(self, function, f_args=[], f_parameter={}):
        super(thread, self).__init__()
        self.function = function
        self.f_args = f_args
        self.f_parameter = f_parameter


    def run(self):  # 线程启动后会自动执行,这里是逻辑实现的代码
        print(f'{self.function} Start... ,args : {self.f_args}; parameter : {self.f_parameter} ; ')
        try:
            self.function(*self.f_args, **self.f_parameter)
            # return_dict =
        except Exception as e:
            info = traceback.format_exc()
            print(info)
        # self.finishSignal.emit(return_dict) #发射信号
