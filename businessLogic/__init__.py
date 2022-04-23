import os

try:
    import _pickle as pickle
except ImportError:
    import pickle

basepath = os.path.abspath(os.sep.join([os.path.dirname(__file__), ".."]))
serialize_basename = os.sep.join([basepath, "pickle"])
os.makedirs(serialize_basename, exist_ok=True)
# 用户
user_pickle_path = os.sep.join([serialize_basename, "user.pickle"])
if os.path.exists(user_pickle_path):
    user_pickle = pickle.load(open(user_pickle_path, 'rb'))
else:
    user_pickle = {}
if "user" not in user_pickle:
    user_pickle["user"] = {"username": None, "password": None, }
    print(user_pickle["user"], 111)
if "remember" not in user_pickle:
    user_pickle["remember"] = False
if "auth_key" not in user_pickle:
    user_pickle["auth_key"] = None
if "auth_session" not in user_pickle:
    user_pickle["auth_session"] = None
pickle.dump(user_pickle, open(user_pickle_path, 'wb'))
# 工作
jobs_pickle_path = os.sep.join([serialize_basename, "jobs.pickle"])
if os.path.exists(jobs_pickle_path):
    jobs_pickle = pickle.load(open(jobs_pickle_path, 'rb'))
else:
    jobs_pickle = {}
if "current_jobs_id" not in jobs_pickle:
    jobs_pickle["current_jobs_id"] = None
if "jobs" not in jobs_pickle:
    jobs_pickle["jobs"] = {}
if "task_details" not in jobs_pickle:
    jobs_pickle["task_details"] = {}
pickle.dump(jobs_pickle, open(jobs_pickle_path, 'wb'))
# 图像注释
image_annotation_pickle_path = os.sep.join([serialize_basename, "image_annotation.pickle"])
if os.path.exists(image_annotation_pickle_path):
    image_annotation_pickle = pickle.load(open(image_annotation_pickle_path, 'rb'))
else:
    image_annotation_pickle = {}
pickle.dump(image_annotation_pickle, open(image_annotation_pickle_path, 'wb'))
# 配置设置
settings_pickle_path = os.sep.join([serialize_basename, "settings.pickle"])
if os.path.exists(settings_pickle_path):
    settings_pickle = pickle.load(open(settings_pickle_path, 'rb'))
else:
    settings_pickle = {}
if "cvat_url" not in settings_pickle:
    settings_pickle["cvat_url"] = "http://111.67.195.173:9001"
pickle.dump(settings_pickle, open(settings_pickle_path, 'wb'))
