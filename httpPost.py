import requests
import json

def post_count_result(vehicleCount=0, personCount=0, callbackUrl='', method="count", rtspSrc="", taskId=""):
    # post_url = 'http://199.19.110.7:7104/api/Callback'
    # 创建包含要发送的参数的字典
    print("post_result go....")
    message = {
        'method': method,
        'taskId': taskId,
        'params':{
            'rtspSrc': rtspSrc,
            'vehicleCount': vehicleCount,
            'personCount': personCount
        }
    }
    # message=json.dumps(message)
    response = requests.post(callbackUrl, json=message, headers={'content-type': 'application/json;charset=UTF-8'})
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    # response = requests.request("post",post_url, json=message, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        print(f'请求已成功发送,callbackUrl={callbackUrl}')
    else:
        print(f'请求失败',callbackUrl={callbackUrl})
    print(response.text)

def post_gate_result(carIn=0, carOut=0, personIn=0, personOut=0, callbackUrl='http://199.19.110.7:7104/api/Callback', method="countEntryExit", rtspSrc="", taskId=""):
    # post_url = 'http://199.19.110.7:7104/api/Callback'
    # 创建包含要发送的参数的字典
    print("post_result go....")
    message = {
        'method': method,
        'taskId': taskId,
        'params':{
            'rtspSrc': rtspSrc,
            'carIn': carIn,
            'carOut': carOut,
            'personIn': personIn,
            'personOut': personOut
        }
    }
    # message=json.dumps(message)
    response = requests.post(callbackUrl, json=message, headers={'content-type': 'application/json;charset=UTF-8'})
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    # response = requests.request("post",post_url, json=message, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        print('请求已成功发送')
    else:
        print('请求失败')
    print(response.text)


def callCount(countAPI_url, rtspSrc, callbackUrl, taskId):
    message = {
        'rtspSrc': rtspSrc,
        'callbackUrl': callbackUrl,
        'taskId': taskId
    }
    response = requests.post(countAPI_url, json=message, headers={'content-type': 'application/json;charset=UTF-8'})
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    # response = requests.request("post",post_url, json=message, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        print('请求已成功发送')
    else:
        print('请求失败')
    print(response.text)

def callGate(gateAPI_url, rtspSrc, callbackUrl, lineCrossingCarIn,lineCrossingCarOut,lineCrossingPersonIn,lineCrossingPersonOut,taskId):
    message = {
        'rtspSrc': rtspSrc,
        'callbackUrl': callbackUrl,
        'lineCrossingCarIn':lineCrossingCarIn,
        'lineCrossingCarOut':lineCrossingCarOut,
        'lineCrossingPersonIn':lineCrossingPersonIn,
        'lineCrossingPersonOut':lineCrossingPersonOut,
        'taskId': taskId
    }
    response = requests.post(gateAPI_url, json=message, headers={'content-type': 'application/json;charset=UTF-8'})
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    # response = requests.request("post",post_url, json=message, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        print('请求已成功发送')
    else:
        print('请求失败')
    print(response.text)
def callStopAIboxService(portNO):
    url = "http://192.168.200.197:5002/stop"
    params = {"port": portNO}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print('请求已成功发送')
    else:
        print('请求失败')
    print(response.text)

if __name__ == '__main__':
    ##github key:qQeV0h/YthXN6GT/I95tBc1hyOtbeaf43bohL+Tw7ww
    ##rtsp://118.89.76.229:554/live/park
    ##rtsp://199.19.110.7:7103/live/park"
    ##rtsp://199.19.110.7:7402/live/park"
    ##line-crossing-car_in=400;500;400;1058;50;500;800;500;
    ##line-crossing-person_in=1300;500;1300;1058;1200;400;1800;400;
    ##line-crossing-person_out=1400;1058;1400;500;1200;500;1600;500;

    # post_count_result(Vehicle_count=0, Person_count=0, callbackUrl='http://199.19.110.7:7104/api/Callback', method="count", rtspSrc="rtsp://199.19.110.7:7103/live/park", taskId="task20230630001")

    callCount(countAPI_url='http://192.168.100.45:5002/count', rtspSrc="rtsp://106.14.163.86:8554/live/test", callbackUrl="http://119.89.76.229:7403/api/Callback", taskId="count_20230630001")
    # callGate(gateAPI_url='http://192.168.100.197:5002/countEntryExit',
    #          rtspSrc="rtsp://199.19.110.7:7402/live/park",
    #          callbackUrl="http://199.19.110.7:7403/api/Callback",
    #          taskId="count_20230630001",
    #          lineCrossingCarIn="400;500;400;1058;50;500;800;500;",
    #          lineCrossingCarOut="400;500;400;1058;50;500;800;500;",
    #          lineCrossingPersonIn="1300;500;1300;1058;1200;400;1800;400;",
    #          lineCrossingPersonOut="1400;1058;1400;500;1200;500;1600;500;"
    # )

    # callStopAIboxService(9601)
    # post_gate_result(callbackUrl='http://199.19.110.7:7403/api/Callback')






