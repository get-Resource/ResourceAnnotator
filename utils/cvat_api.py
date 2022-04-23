import json
import os

import requests

try:
    import _pickle as pickle
except ImportError:
    import pickle
basepath = os.path.abspath(os.sep.join([os.path.basename(__file__), ".."]))
serialize_basename = os.sep.join([basepath, "hyckle"])
os.makedirs(serialize_basename, exist_ok=True)


class cvat_service:
    # http://url/api/swagger/
    def __init__(self, url="http://111.67.195.173:9001", ):
        self.url = f"{url}"
        self.headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            'accept': '*/*',
            'Content-Type': 'application/json',
        }
        self.session = requests.session()

    # region auth 登录认证

    def auth_login(self, username, password, email=None):
        url = f"{self.url}/api/auth/login"
        body = {}
        if username:
            body.update({"username": username})
        if password:
            body.update({"password": password})
        if email:
            body.update({"email": email})
        headers = {}
        headers.update(self.headers)
        if list(self.session.cookies) == []:
            body = json.dumps(body)
            try:
                response = self.session.request(
                    "POST", url, headers=self.headers, data=body)
                text = json.loads(response.text)
                return text, self.session
            except requests.exceptions.ConnectionError as e:
                message = {
                    "error code": 400,
                    "message": f"无法连接服务，请检查网络情况，确保能访问: {url}",
                }
                return message
            except Exception as e:  # 服务器错误、无法访问url错误
                print(e)
        # print(self.session.cookies)
        # text = json.loads(response.text)

    def load_auth(self, sessio):
        if sessio:  # 本地存在则加载本地
            self.session = sessio
        return self.session

    # endregion

    # region jobs
    def get_jobs_list(self, filter=None, org=None, org_id=None, page=None, page_size=None, search=None, sort=None):
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
                    ],',
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
            body.update({"filter": filter})
        if org:
            body.update({"org": org})
        if org_id:
            body.update({"org_id": org_id})
        if page:
            body.update({"page": page})
        if page_size:
            body.update({"page_size": page_size})
        if search:
            body.update({"search": search})
        if sort:
            body.update({"sort": sort})

        try:
            response = self.session.request(
                "GET", url, headers=self.headers, data=body)
            text = response.text
            text = json.loads(text)
        except requests.exceptions.ConnectionError as e:
            text = e
        except json.decoder.JSONDecodeError as e:
            text = f"{e} : {text}"
        return text

    def get_jobs_details(self, id):
        """
        返回作业详细信息
        :filter str 可用的 filter_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        :org  str 组织唯一org
        :org_id str   组织标识符
        :page str 分页结果集中的页码
        :page_size int 每页返回的结果数。
        :search str  一个搜索词。可用的搜索字段：（'task_name'，'project_name'，'assignee'，'state'，'stage'）
        :sort str 排序结果时使用哪个字段。可用 ordering_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        return dict:
            {'url': 'http://111.67.195.173:9001/api/jobs/8', 'id': 8, 'task_id': 6, 'project_id': 2, 
                'assignee': {'url': 'http://111.67.195.173:9001/api/users/3', 
                'id': 3, 'username': 'tester', 'first_name': '万一', 'last_name': '诗人'
                }, 'dimension': '2d', 
                'labels': [
                    {'id': 2, 'name': 'obj', 'color': '#c06020', 
                    'attributes': [
                        {'id': 2, 'name': 'text', 'mutable': False, 'input_type': 'select', 'default_value': 'car_type', '
                        values': ['car_type', 'register_office', 'register_date', 'register_num', 'vin', 'owner']}
                    ]}
                ], 
                'bug_tracker': '', 'status': 'annotation', 'stage': 'annotation', 'state': 'new', 'mode': 'annotation', 
            'start_frame': 40, 'stop_frame': 45, 'data_chunk_size': 16, 'data_compressed_chunk_type': 'imageset'}

        """
        url = f"{self.url}/api/jobs/{id}"
        body = {}

        try:
            response = self.session.request(
                "GET", url, headers=self.headers, data=body)
            text = json.loads(response.text)
        except requests.exceptions.ConnectionError as e:
            text = e
        except json.decoder.JSONDecodeError as e:
            text = f"{e} : {text}"
        print(text)
        return text

    def get_jobs_annotations(self, id, filter=None, org=None, org_id=None, page=None, page_size=None, search=None,
                             sort=None):
        """
        :filter str 可用的 filter_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        :org  str 组织唯一org
        :org_id str   组织标识符
        :page str 分页结果集中的页码
        :page_size int 每页返回的结果数。
        :search str  一个搜索词。可用的搜索字段：（'task_name'，'project_name'，'assignee'，'state'，'stage'）
        :sort str 排序结果时使用哪个字段。可用 ordering_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        return dict:
        """
        url = f"{self.url}/api/jobs/{id}/annotations/"
        body = {}
        if filter:
            body.update({"filter": filter})
        if org:
            body.update({"org": org})
        if org_id:
            body.update({"org_id": org_id})
        if page:
            body.update({"page": page})
        if page_size:
            body.update({"page_size": page_size})
        if search:
            body.update({"search": search})
        if sort:
            body.update({"sort": sort})
        try:
            response = self.session.request(
                "GET", url, headers=self.headers, data=body)
            text = response.text
            text = json.loads(text)
        except requests.exceptions.ConnectionError as e:
            text = e
        except json.decoder.JSONDecodeError as e:
            text = f"{e} : {text}"
        print(text)
        return text

    def patch_jobs_annotations(self, id, action, annotations):
        """
        action [create,update,delete]
        annotations:
            action = create:
            {"shapes":[
                {"type":"rectangle","occluded":false,"z_order":0,
                    "points":[507.8126550868492,337.07593052109223,933.0794044665017,674.1392059553364],
                    "rotation":0,"attributes":[{"spec_id":"2","value":"car_type"}],
                    "frame":0,"label_id":2,"group":0,"source":"manual"},
                {"type":"rectangle","occluded":false,"z_order":0,
                    "points":[788.173697270473,819.0449131513651,1396.1476426799018,1304.1640198511177],
                    "rotation":0,"attributes":[{"spec_id":"2","value":"car_type"}],
                    "frame":0,"label_id":2,"group":0,"source":"manual"}],
            "tracks":[],"tags":[{"frame":0,"label_id":2,"group":0,"attributes":[{"spec_id":"2","value":"car_type"}]}],"version":0}
            {"shapes":[
                {"type":"rectangle","occluded":false,"z_order":0,
                    "rotation":0.0,"attributes":[{"spec_id":2,"value":"car_type"}],
                    "points":[507.8126550868492,337.07593052109223,933.0794044665017,674.1392059553364],
                    "id":16,"frame":0,"label_id":2,"group":0,"source":"manual"},
                {"type":"rectangle","occluded":false,"z_order":0,
                    "points":[788.173697270473,819.0449131513651,1396.1476426799018,1304.1640198511177],
                    "rotation":0.0,"attributes":[{"spec_id":2,"value":"car_type"}],
                    "id":17,"frame":0,"label_id":2,"group":0,"source":"manual"}]
            "tracks":[],"tags":[{"frame":0,"label_id":2,"id":2,"group":0,"attributes":[{"spec_id":"2","value":"car_type"}]}],"version":0}
            action = update:

            action = delete:
            {"shapes":[
                {"type":"polygon","occluded":false,"z_order":0,
                    "rotation":0,"attributes":[{"spec_id":2,"value":"car_type"}],
                    "points":[451.1103515625,1433.3193359375,951.9801488833746,1477.4208436724566,901.5781637717137,1694.7794044665025,441.6600496277915,1653.827791563277],"
                    id":12,"frame":0,"label_id":2,"group":0,"source":"manual"},
                {"type":"polygon","occluded":false,"z_order":0,
                    "rotation":0,"attributes":[{"spec_id":2,"value":"car_type"}]},
                    "points":[1109.486328125,333.92578125,1559.9540942928052,308.72481389578206,1563.104218362283,626.8873449131515,1005.532258064517,715.0908188585618],
                    "id":13,"frame":0,"label_id":2,"group":0,"source":"manual"],
                "tracks":[],"tags":[],"version":0}
        label_id 指的是 label id
        spec_id 指的是 attributes id
        return annotations dict 包含 return[key][N]["id"] = 服务器上的 shape id,key in [shapes,tags,tracks]
        """
        if action in ["create", "update", "delete"]:
            url = f"{self.url}/api/jobs/{id}/annotations/"
            try:
                response = self.session.request(
                    "PATCH", url, headers=self.headers, data=body)
                text = response.text
                text = json.loads(text)
            except requests.exceptions.ConnectionError as e:
                text = e
            except json.decoder.JSONDecodeError as e:
                text = f"{e} : {text}"
            print(text)
            return text

    def get_jobs_data(self, id, number=0, type="frame", quality="original"):
        """
        获取图片
        :id str 标识此作业的唯一整数值​​。
        :number  str 标识块或帧的唯一数值，与“预览”类型无关
        :quality str   指定请求数据的质量级别，与“预览”类型无关 [compressed,original]
        :type str 指定请求数据的类型[chunk ,context_image ,frame ,preview]
        return images bytes:
        """
        type_list = ["chunk", "frame", "preview"]
        quality_list = ["compressed", "original"]

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
            body.update({"number": str(number)})
        body.update({"quality": quality})
        body.update({"type": type})

        try:
            response = self.session.request(
                "GET", url, headers=headers, params=body)
            images = response.content
        except requests.exceptions.ConnectionError as e:
            images = e

        # with open(f"./{type}.jpg", 'wb') as f:
        #     f.write(images)
        return images

    def get_jobs_issues(self, id, filter=None, org=None, org_id=None, page=None, page_size=None, search=None,
                        sort=None):
        """
        :id str jobs id
        :filter str 可用的 filter_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        :org  str 组织唯一org
        :org_id str   组织标识符
        :page str 分页结果集中的页码
        :page_size int 每页返回的结果数。
        :search str  一个搜索词。可用的搜索字段：（'task_name'，'project_name'，'assignee'，'state'，'stage'）
        :sort str 排序结果时使用哪个字段。可用 ordering_fields: ['task_name', 'project_name', 'assignee', 'state', 'stage', 'id', 'task_id', 'project_id', 'updated_date']
        return issues list 
[
  {
    "id": 6, issues id
    "frame": 0, 帧id
    "position": [ issues 问题区域
      851.9736328125,
      99.7138671875,
      1280.8990234374996,
      349.6619140625007
    ],
    "job": 2,
    "owner": {  提出问题人
      "url": "http://111.67.195.173:9001/api/users/1",
      "id": 1,
      "username": "admin",
      "first_name": "",
      "last_name": ""
    },
    "assignee": null,
    "created_date": "2022-04-20T14:47:14.531895Z",
    "updated_date": null,
    "comments": [
      {
        "id": 6,
        "issue": 6,
        "owner": { 评论人
          "url": "http://111.67.195.173:9001/api/users/1",
          "id": 1,
          "username": "admin",
          "first_name": "",
          "last_name": ""
        },
        "message": "Wrong position", 评论内容
        "created_date": "2022-04-20T14:47:14.546797Z",
        "updated_date": "2022-04-20T14:47:14.546822Z"
      }
    ],
    "resolved": false
  }
]
        """
        url = f"{self.url}/api/jobs/{id}/issues"
        body = {}
        if filter:
            body.update({"filter": filter})
        if org:
            body.update({"org": org})
        if org_id:
            body.update({"org_id": org_id})
        if page:
            body.update({"page": page})
        if page_size:
            body.update({"page_size": page_size})
        if search:
            body.update({"search": search})
        if sort:
            body.update({"sort": sort})
        try:
            response = self.session.request(
                "GET", url, headers=self.headers, data=body)
            text = response.text
            text = json.loads(text)
        except requests.exceptions.ConnectionError as e:
            text = e
        except json.decoder.JSONDecodeError as e:
            text = f"{e} : {text}"
        print(text)
        return text

    # endregion

    # region task 任务
    def get_tasks_data_meta(self, id):
        """
        获取图片信息
        :id str 标识此作业的唯一整数值​​。
        return text dict:
        """
        type_list = ["chunk", "frame", "preview"]
        quality_list = ["compressed", "original"]

        url = f"{self.url}/api/tasks/{id}/data/meta"
        body = {}
        headers = {}
        headers.update(self.headers)
        try:
            response = self.session.request(
                "GET", url, headers=headers, params=body)
            text = response.text
            text = json.loads(text)
        except requests.exceptions.ConnectionError as e:
            text = e
        except json.decoder.JSONDecodeError as e:
            text = f"{e} : {text}"
        return text

    def get_tasks_data(self, id):
        """
        获取图片信息
        :id str 标识此作业的唯一整数值​​。
        return text dict:
        """
        type_list = ["chunk", "frame", "preview"]
        quality_list = ["compressed", "original"]

        url = f"{self.url}/api/tasks/{id}/data"
        body = {}
        headers = {}
        headers.update(self.headers)
        try:
            response = self.session.request(
                "GET", url, headers=headers, params=body)
            text = response.text
            text = json.loads(text)
        except requests.exceptions.ConnectionError as e:
            text = e
        except json.decoder.JSONDecodeError as e:
            text = f"{e} : {text}"
        return text

    # endregion


if __name__ == "__main__":
    api = cvat_service()
    body = {
        "username": "tester",
        # "email": "tester@test.com",
        "password": "Tester123"
    }
    api.auth_login(**body)
    api.get_jobs_list()
    # data = api.data(3, 1, "frame")
    # data = api.tasks_data_meta(6)
    data = api.get_jobs_details(8)
