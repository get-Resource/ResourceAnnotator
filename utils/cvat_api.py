
from cv2 import ellipse
import requests
import os
import json
from requests.auth import HTTPDigestAuth
import _pickle as pickle
try:
    import _pickle as pickle
except ImportError:
    import pickle
basepath = os.path.abspath(os.sep.join([os.path.basename(__file__),".."]))
serialize_basename =  os.sep.join([basepath,"serialize"])
os.makedirs(serialize_basename,exist_ok=True)
session_path =  os.sep.join([serialize_basename,"auth.session"])

class cvat_service:
    # http://url/api/swagger/
    def __init__(self, url="http://111.67.195.173:9001",):
        self.url = f"{url}"
        self.headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            'accept': '*/*',
            'Content-Type': 'application/json',
        }
        self.session = requests.session()
        self.session.auth
        self.n = self.session.cookies
    # region auth 登录认证

    def auth_login(self, username,  password,email = None):
        url = f"{self.url}/api/auth/login"
        body = {}
        if username:
            body.update({"username":username})
        if password:
            body.update({"password":password})
        if email:
            body.update({"email":email})

        headers = {}
        headers.update(self.headers)

        if os.path.exists(session_path):
            #加载session
            with open(session_path, 'rb') as f:
                self.session = pickle.load(f)
        if list(self.session.cookies) == []:
            body = json.dumps(body)
            response = self.session.request(
                "POST", url, headers=self.headers, data=body)
            text = json.loads(response.text)
            self.auth_key = text["key"]
            
            print(text["key"])
        with open(session_path,'wb') as f:
            pickle.dump(self.session, f)
        print(self.session.cookies)
        # text = json.loads(response.text)
    # endregion


    # region jobs 任务
    def jobs_list(self, filter=None, org=None, org_id=None, page=None, page_size=None, search=None, sort=None):
        """
        :filter str 可用的 filter_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        :org  str 组织唯一org
        :org_id str   组织标识符
        :page str 分页结果集中的页码
        :page_size int 每页返回的结果数。
        :search str  一个搜索词。可用的搜索字段：（'task_name'，'project_name'，'assignee'，'state'，'stage'）
        :sort str 排序结果时使用哪个字段。可用 ordering_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        return dict:
        {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": "http: //111.67.195.173:9001/api/jobs/3",
                    "id": 3,
                    "task_id": 5,
                    "project_id": 2,
                    "assignee": {
                        "url": "http://111.67.195.173:9001/api/users/3",
                        "id": 3,
                        "username": "tester",
                        "first_name": "万一",
                        "last_name": "诗人"
                    },
                    "dimension": "2d",
                    "labels": [
                        {
                            "id": 2,
                            "name": "obj",
                            "color": "#c06020",
                            "attributes": [
                                {
                                    "id": 2,
                                    "name": "text",
                                    "mutable": False,
                                    "input_type": "select",
                                    "default_value": "car_type",
                                    "values": [
                                        "car_type",
                                        "register_office",
                                        "register_date",
                                        "register_num",
                                        "vin",
                                        "owner"
                                    ]
                                }
                            ]
                        }
                    ],
                    "bug_tracker": "",
                    "status": "validation",
                    "stage": "acceptance",
                    "state": "new",
                    "mode": "annotation",
                    "start_frame": 0,
                    "stop_frame": 12,
                    "data_chunk_size": 26,
                    "data_compressed_chunk_type": "imageset"
                }
            ]
        }
        """
        url = f"{self.url}/api/jobs"
        body = {}
        if filter:
            body.update({"filter":filter})
        if org:
            body.update({"org":org})
        if org_id:
            body.update({"org_id":org_id})
        if page:
            body.update({"page":page})
        if page_size:
            body.update({"page_size":page_size})
        if search:
            body.update({"search":search})
        if sort:
            body.update({"sort":sort})

        try:
            response = self.session.request("GET", url, headers=self.headers, data=body)
        except requests.exceptions.ConnectionError:
            pass
        text = json.loads(response.text)
        print(text)
        
    def data(self, id, number = 0, type ="frame", quality ="original"):
        """
        :id str 标识此作业的唯一整数值​​。
        :number  str 标识块或帧的唯一数值，与“预览”类型无关
        :quality str   指定请求数据的质量级别，与“预览”类型无关 [compressed,original]
        :type str 指定请求数据的类型[chunk ,context_image ,frame ,preview]
        return images bolb:
        """
        type_list = ["chunk" ,"frame" ,"preview"]  
        quality_list = ["compressed" ,"original"]

        url = f"{self.url}/api/jobs/{id}/data"

        headers = {}
        headers.update(self.headers)
        body = {}
        if type not in type_list:
            type = type_list[1]
        if type == "chunk":
            number = 0
        if quality not in quality_list:
            quality = quality_list[0]
        if number < 0:
            number = 0
        if number is not None:
            body.update({"number":str(number)})
        body.update({"quality":quality})
        body.update({"type":type})

        try:
            response = self.session.request("GET", url, headers=headers, params=body)
        except requests.exceptions.ConnectionError:
            pass
        text = response.content
        with open("./test.jpg", 'wb') as f:
            f.write(text)
        return text
        # self.auth_key = text["key"]
        # http://111.67.195.173:9001/api/jobs
    # endregion


api = cvat_service()
body = {
    "username": "tester",
    # "email": "tester@test.com",
    "password": "Tester123"
}
api.auth_login(**body)
api.jobs_list()
data = api.data(3,1,"frame")


