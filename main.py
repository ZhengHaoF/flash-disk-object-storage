# -*- coding:utf-8 -*-
import os.path
import random
import string

import requests
from tkinter import *
import tkinter.filedialog
import time

now_upload_dir = 1720942


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


def mkdir(token, dir_name):
    # 创建文件夹
    data = {
        "token": token,
        "id": "0",
        "name": dir_name
    }
    r = requests.post("https://shandianpan.com/api/pan/mkdir", data=data)
    if r.status_code == 200:
        print(r.text)
        print("新建文件夹成功")
        r_json = r.json()
        if r_json['code'] == 0:
            return r_json['data']['dir_info']['id']
        return 0


def file_pre_upload(token, file_name):
    # 文件预上传
    data = {
        "token": token,
        "name": file_name,
        "id": now_upload_dir
    }
    while True:
        r = requests.post("https://shandianpan.com/api/pan/upload", data=data)
        print("文件预上传")
        print(r.status_code)
        print(r.text)
        if r.status_code == 200:
            break
        elif r.status_code == 429:
            print("上传太快了，系统自动暂停10秒钟")
            time.sleep(10)  # 暂停10秒钟
    r_json = r.json()
    if r_json['code'] == 0:
        return r_json['data']
    else:
        print("操作失败")
        return 0


def upload_file(token, file_pre_upload_json, file):
    global now_upload_dir  # 申明使用全局变量
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
        "file": file
    }

    r = requests.post("https://sdpan.oss-cn-hangzhou.aliyuncs.com/", data=data, files=files)
    print("文件上传")
    print(r)
    print(r.text)
    r_json = r.json()
    if r_json['code'] == 0:
        print("上传完成")
        print("文件直链：" + "https://oss.shandianpan.com/" + file_pre_upload_json['key'])
        f.close()
        f1 = open("文件列表.txt", 'a+', encoding='utf-8')
        f1.write("文件名：" + os.path.split(f.name)[1] + "\t文件直链：" + "https://oss.shandianpan.com/" + file_pre_upload_json[
            'key'] + "\n")
        return 0
    elif r_json['code'] == 1:
        print("该文件夹文件数已达最大，正在自动新建文件夹")
        now_upload_dir = mkdir(token=user_token, dir_name=''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))  # 文件夹名是随机字符串
        print("新的文件夹ID:" + str(now_upload_dir))
        return 1
    else:
        print("操作失败")
        return 2


# get_file_list(get_files(user_token, "1"))  # 获取文件列表
print("By：轻芒 群号：857994945")
username = input("请输入用户名：")
password = input("请输入密码：")
username = "19157700744"
password = "54ZhengHF"
user_token = login_sdp(username=username, password=password)  # 登录
count_code = input("请输入指令：")
if count_code == "put":
    if user_token != 0:
        while True:
            print("请选择文件")
            root = Tk()
            p = tkinter.filedialog.askopenfilenames()
            root.quit()
            try:
                for item in p:
                    f = open(item, 'rb')
                    file_name = f.name
                    file_size = os.path.getsize(item) / 1024 / 1024
                    print("文件名：" + os.path.basename(f.name))
                    print("文件大小：" + str(file_size))
                    if file_size <= 100:
                        print("正在上传···")
                        file_pre_upload_json = file_pre_upload(user_token,
                                                               os.path.basename(f.name))  # 文件预上传 ,用来获取下次上传的参数
                        r_code = upload_file(user_token, file_pre_upload_json, f)  # 开始上传
                        if r_code == 0:
                            # 正常
                            pass
                        elif r_code == 1:
                            # 文件夹满了
                            file_pre_upload_json = file_pre_upload(user_token,
                                                                   os.path.basename(f.name))  # 文件预上传 ,用来获取下次上传的参数
                            r_code = upload_file(user_token, file_pre_upload_json, f)  # 开始上传
                        else:
                            print("SB")
                    else:
                        print("文件过大")
            except Exception as e:
                print(e)
                print("文件不存在")
elif count_code == "ls":
    get_file_list(token=user_token, page=0, dir_id=1720942)
elif count_code == "mkdir":
    dir_id = mkdir(token=user_token)
    print(dir_id)
