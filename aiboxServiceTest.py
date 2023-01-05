# This is a sample Python script.\
# rtsp://417u0941d0.wicp.vip:8554/live/2
# -*- coding: utf-8 -*-
import requests
url = 'http://192.168.1.5:5000/push?url=rtsp://417u0941d0.wicp.vip:8554/live/2'
cookies = {'Cookie':'xxxxx'}
r = requests.get(url, cookies = cookies)
#print(r.text)
print(r.content)

