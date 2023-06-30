# -*- coding: utf-8 -*-
# !/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import json
import sys
import logging
import os
import cv2
import numpy as np
from flask import Flask, redirect, url_for, request, render_template
import FlaskTest
import time
from multiprocessing import Process
# sys.path.append(".")
from api_count.count import invoke
from flask_cors import CORS
import utils

app = Flask(__name__)
##r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
CORS(app, resources=r'/*')
out_port= 9600
updsink_port_num=5400
@app.route('/')
def index():
    return render_template("login.html")

@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      print(1)
      user = request.form['nm']
      return redirect(url_for('success',name = user))
   else:
      print(2)
      user = request.args.get('nm')
      return redirect(url_for('success',name = user))

def alibaba(name,inputURL):
    result=0
    for i in range(1000):
        result += i
        print('hello,%s,%d' % (inputURL, i))
        time.sleep(5)

@app.route('/stop',methods = ['GET'])
def stop():
      port = request.args.get('port')
      print("port="+port)
      code,msg,data=utils.killProcessByPort(int(port))
      returnMSG=json.dumps({"code":code,"msg":msg,"data":data})
      return (returnMSG)

@app.route('/push2',methods = ['GET'])
def push2():
      global out_port
      host_ip=utils.get_host_ip()
      inputURL = request.args.get('url')
      # logging.INFO("inputURL")
      print("inputUrl="+inputURL)
      my_process = Process(target=invoke, args=('H264',4000000,inputURL,'nvinfer',out_port))
      my_process.start()
      returnURL="rtsp://%s:%d/aibox"%(host_ip,out_port)
      print("returnURL=%s"%(returnURL))
      returnMSG=json.dumps({"code":200,"msg":"","data":returnURL})
      return (returnMSG)

@app.route('/push',methods = ['GET'])
def push():
      global out_port
      host_ip = utils.get_host_ip()
      inputURL = request.args.get('url')
      print("inputUrl="+inputURL)
      my_process = Process(target=invoke, args=('H264',4000000,inputURL,'nvinfer',out_port))
      my_process.start()
      returnURL = "rtsp://%s:%d/aibox" % (host_ip, out_port)
      print("returnURL=%s"%(returnURL))
      out_port = out_port + 1
      returnMSG=json.dumps({"code":200,"msg":"","data":returnURL})
      return (returnMSG)

@app.route('/pushimg',methods=['GET','POST'])
def pushimg():
    #
    img = base64.b64decode(str(request.form['image']))
    image_data = np.fromstring(img, np.uint8)
    image_data = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    cv2.imwrite('01.jpg', image_data)
    print(image_data)
    return 'koukou'

@app.route('/count', methods=['POST'])
def count():
    global out_port
    global updsink_port_num
    method="count"
    host_ip = utils.get_host_ip()
    json_data = request.get_json()
    print("host_ip=%s,json_data=%s" % (host_ip,json_data))
    if 'rtsp_url' in json_data and 'callback_url' and 'task_id' in json_data:
        try:
            rtsp_url = json_data['rtsp_url']
            callback_url = json_data['callback_url']
            task_id = json_data["task_id"]
            my_process = Process(target=invoke, name=task_id,args=('H264', 4000000, rtsp_url, 'nvinfer', out_port,callback_url,method,task_id))
            my_process.start()
            returnURL = "rtsp://%s:%d/aibox" % (host_ip, out_port)
            print("returnURL=%s" % (returnURL))
            out_port = out_port + 1
            updsink_port_num = updsink_port_num+1
            returnMSG = json.dumps({"code": 200, "msg": "invoke count process successfully", "data": returnURL})
            return (returnMSG)
        except:
            returnMSG = json.dumps({"code": -1, "msg": "exception,please check ", "data": ""})
            return (returnMSG)

    else:
        returnMSG = json.dumps({"code": 201, "msg": "错误!请提供rtsp_url、callback_url和task_id", "data": ""})
        return (returnMSG)

if __name__ == '__main__':

    app.run(host="0.0.0.0",port=5002)

