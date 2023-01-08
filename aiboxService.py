import base64
import json
import logging
import os
import cv2
import numpy as np
from flask import Flask, redirect, url_for, request, render_template
import FlaskTest
import time
from multiprocessing import Process
from aibox import invoke
app = Flask(__name__)
out_port= 9600
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

def getReturnURL(out_port):
    return_url="rtsp://192.168.1.6:%d/ds-test"%(out_port)
    return return_url


def alibaba(name,inputURL):
    result=0
    for i in range(1000):
        result += i
        print('hello,%s,%d' % (inputURL, i))
        time.sleep(5)

@app.route('/push',methods = ['GET'])
def push():
      global out_port
      inputURL = request.args.get('url')
      # logging.INFO("inputURL")
      print("inputUrl="+inputURL)
      my_process = Process(target=invoke, args=('H264',4000000,inputURL,'nvinfer',out_port))
      my_process.start()
      returnURL="rtsp://192.168.1.6:%d/aibox"%(out_port)
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

if __name__ == '__main__':

    app.run(host="0.0.0.0",port=5000)

    print("come on ")
