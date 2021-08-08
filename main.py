# -*- coding:utf-8 -*-
import os.path
import random
import string

import requests
from tkinter import *
import tkinter.filedialog
import time

now_upload_dir = 0  # 1720942
now_file = None
now_file_path = ""


def login_sdp(username, password):
    data = {"mobile": username, "password": password}
    r = requests.post("https://shandianpan.com/api/login", data=data)
    r_json = r.json()
    if r_json['code'] == 0:
        user_token = r_json['data']['token']
        print("登录成功")
        print(user_token)
        return user_token
    else:
        print("登录失败")
        return 0


def get_files(token, page, dir_id):
    # 获取文件信息
    data = {"token": user_token, "page": page, "id": dir_id}
    r = requests.post("https://shandianpan.com/api/pan", data=data)
    r_json = r.json()
    if r_json['code'] == 0:
        file_list_json = r_json['data']
        return file_list_json
    else:
        print(r.text)
        print("操作失败")
        return 0


def get_file_list(token, page, dir_id):
    # 获取文件列表 如果page == 0 则获取全部
    if page == 0:
        page_num = 1
        while True:
            file_list_json = get_files(token=token, page=page_num, dir_id=dir_id)
            page_num = page_num + 1
            if not file_list_json:
                break
            for item in file_list_json:
                print(item)
    else:
        file_list_json = get_files(token=token, page=page, dir_id=dir_id)
        for item in file_list_json:
            print(item)


def get_redirect_file_url(token, file_id):
    # 获取文件名修改后的文件直链
    params = {
        "id": file_id,
        "token": token
    }
    r = requests.get("https://shandianpan.com/api/pan/file-download", params=params)
    print("带后缀的文件直链：" + r.url)
    f2 = open("带后缀的文件列表.txt", 'a+', encoding='utf-8')
    f2.write("文件名：" + os.path.split(now_file.name)[1] + "\t文件直链：" + r.url + "\n")


def mkdir(token, dir_name):
    # 创建文件夹
    data = {
        "token": token,
        "id": "0",
        "name": dir_name
    }
    r = requests.post("https://shandianpan.com/api/pan/mkdir", data=data)
    if r.status_code == 200:
        print("新建文件夹成功")
        r_json = r.json()
        if r_json['code'] == 0:
            return r_json['data']['dir_info']['id']
        return 0


def rename_file(token, file_id, modify_name):
    # 文件重命名
    data = {
        "token": token,
        "id": file_id,
        "name": modify_name
    }
    r = requests.post("https://shandianpan.com/api/pan/change", data=data)
    if r.status_code == 200:
        print(modify_name)
        r_json = r.json()
        if r_json['code'] == 0:
            return 0


def file_pre_upload(token, file_path, again):
    # 文件预上传
    # 如果again==true,代表是由于文件夹满了，二次上传的
    global now_upload_dir  # 申明使用全局变量
    global now_file  # 当前上传的文件
    if again:
        now_file = now_file
    else:
        now_file = open(file_path, 'rb')
    file_name = now_file.name
    file_size = os.path.getsize(file_path) / 1024 / 1024
    print("文件名：" + os.path.basename(now_file.name))
    print("文件大小：" + str(file_size))
    if file_size <= 100:
        data = {
            "token": token,
            "name": file_name,
            "id": now_upload_dir
        }
        while True:
            r = requests.post("https://shandianpan.com/api/pan/upload", data=data)
            if r.status_code == 200:
                break
            elif r.status_code == 429:
                print("上传太快了，系统自动暂停10秒钟")
                time.sleep(10)  # 暂停10秒钟
        r_json = r.json()
        if r_json['code'] == 0:
            return r_json['data']
        else:
            print(r.text)
            print("操作失败")
            return 1
    else:
        print("文件过大")
        return 2


def upload_file(token, file_pre_upload_json):
    print("正在上传···")
    # 文件上传
    data = {
        "token": token,
        "key": file_pre_upload_json['key'],
        "ossAccessKeyId": file_pre_upload_json['accessid'],
        "policy": file_pre_upload_json['policy'],
        "signature": file_pre_upload_json['signature'],
        "callback": file_pre_upload_json['callback']
    }

    files = {
        "file": now_file
    }

    r = requests.post("https://sdpan.oss-cn-hangzhou.aliyuncs.com/", data=data, files=files)
    r_json = r.json()
    if r_json['code'] == 0:
        print("上传完成")
        print("文件直链：" + "https://oss.shandianpan.com/" + file_pre_upload_json['key'])
        f1 = open("文件列表.txt", 'a+', encoding='utf-8')
        f1.write("文件名：" + os.path.split(now_file.name)[1] + "\t文件直链：" + "https://oss.shandianpan.com/" +
                 file_pre_upload_json[
                     'key'] + "\n")
        return r_json['data']['id']
    elif r_json['code'] == 1:
        print("该文件夹文件数已达最大，正在自动新建文件夹")
        now_upload_dir = mkdir(token=user_token, dir_name=''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))  # 文件夹名是随机字符串
        print("新的文件夹ID:" + str(now_upload_dir))
        # 重新预上传
        again_file_pre_upload_json = file_pre_upload(token=user_token, file_path=now_file_path, again=True)
        upload_file(token=user_token, file_pre_upload_json=again_file_pre_upload_json)
        return 1
    else:
        print(r.text)
        print("操作失败")
        return 2


print("By：轻芒 群号：857994945 V1.4")
username = input("请输入用户名：")
password = input("请输入密码：")
user_token = login_sdp(username=username, password=password)  # 登录
print("\n\n操作提示：")
print("现有两个命令如下，如使用rename_put，上传的文件需没有后缀名，并手动指定后缀名")
print("如果上传的是不包含后缀的文件，需注意文件名中不能出现‘.’字符")
print("1. 批量上传文件：put")
print("2. 批量上传文件并保留文件名：rename_put\n")
count_code = input("请输入指令：")
if count_code == "put":
    if user_token != 0:
        print("请选择文件")
        root = Tk()
        p = tkinter.filedialog.askopenfilenames()
        root.quit()
        try:
            for item in p:
                print("开始预上传")
                file_pre_upload_json = file_pre_upload(user_token, item, again=False)  # 文件预上传 ,用来获取下次上传的参数
                if file_pre_upload_json != 1 and file_pre_upload_json != 2:
                    # 预上传成功
                    print("开始上传")
                    r_code = upload_file(user_token, file_pre_upload_json)  # 开始上传
                else:
                    pass
        except Exception as e:
            print(e)
            print("文件不存在")
elif count_code == "ls":
    get_file_list(token=user_token, page=0, dir_id=0)
elif count_code == "mkdir":
    dir_id = mkdir(token=user_token)
    print(dir_id)
elif count_code == "rename_put":
    if user_token != 0:
        suffix = input("请输入批量上传的文件后缀：")
        print("请选择文件")
        root = Tk()
        p = tkinter.filedialog.askopenfilenames()
        root.quit()
        try:
            for item in p:
                print("开始预上传")
                file_pre_upload_json = file_pre_upload(user_token, item, again=False)  # 文件预上传 ,用来获取下次上传的参数
                if file_pre_upload_json != 1 and file_pre_upload_json != 2:
                    # 预上传成功
                    print("开始上传")
                    r_code = upload_file(user_token, file_pre_upload_json)  # 开始上传
                    if r_code != 1 and r_code != 2:
                        print("开始执行重命名")
                        r = rename_file(token=user_token, file_id=r_code,
                                        modify_name=os.path.basename(now_file.name) + "." + suffix)
                        if r == 0:
                            # 获取文件名修改后的文件直链
                            get_redirect_file_url(token=user_token, file_id=r_code)

        except Exception as e:
            print(e)
            print("文件不存在")
