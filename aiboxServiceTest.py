# This is a sample Python script.\
# rtsp://417u0941d0.wicp.vip:8554/live/2
# -*- coding: utf-8 -*-
import requests
import requests
import base64
def pushTest():
    url = 'http://172.18.20.30:5000/push?url=rtsp://417u0941d0.wicp.vip:8554/live/2'
    cookies = {'Cookie':'xxxxx'}
    r = requests.get(url, cookies = cookies)
    #print(r.text)
    print(r.content)
def pushImgTest():
    # 将图片数据转成base64格式
    with open('bailuzhou.jpg', 'rb') as f:
        img = base64.b64encode(f.read()).decode()
    image = []
    image.append(img)
    res = {"image": image}
    # 访问服务
    _ = requests.post("http://127.0.0.1:5000/pushimg", data=res)

if __name__ == '__main__':
    # pushTest()
    pushImgTest()


