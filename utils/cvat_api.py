
import requests
import json
from requests.auth import HTTPDigestAuth
class cvat_service:

    def __init__(self,url = "http://111.67.195.173:9001",):
        self.url = f"{url}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            # 'accept': 'application/vnd.cvat+json',
            'Content-Type': 'application/json',
        }
        self.auth_key = ""
    # region auth 登录认证
    def auth_login(self,username,email,password):
        url = f"{self.url}/api/auth/login"
        session=requests.session()
        body = {
        "username": username,
        "email": email,
        "password": password
        }
        print(self.url)
        body =json.dumps(body)
        response = requests.request("POST",url, headers=self.headers, data=body)
        text = json.loads(response.text)
        self.auth_key = text["key"]
        print(text,self.auth_key)
    # endregion
    
api = cvat_service()
body = {
    "username": "tester",
    "email": "tester@test.com",
    "password": "Tester123"
}
api.auth_login(**body)