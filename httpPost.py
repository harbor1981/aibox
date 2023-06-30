import requests
import json

def post_count_result(Vehicle_count=0, Person_count=0, callback_url='http://199.19.110.7:7104/api/Callback', interface="count", rtsp_src="", task_id=""):
    # post_url = 'http://199.19.110.7:7104/api/Callback'
    # 创建包含要发送的参数的字典
    print("post_result go....")
    message = {
        'interface': interface,
        'params':{
            'rtsp_src': rtsp_src,
            'Vehicle_count': Vehicle_count,
            'Person_count': Person_count,
            'task_id': task_id
        }
    }
    # message=json.dumps(message)
    response = requests.post(callback_url, json=message, headers={'content-type': 'application/json;charset=UTF-8'})
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    # response = requests.request("post",post_url, json=message, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        print('请求已成功发送')
    else:
        print('请求失败')
    print(response.text)
def callAiboxService(countAPI_url, rtsp_url, callback_url,task_id):
    message = {
        'rtsp_url': rtsp_url,
        'callback_url': callback_url,
        'task_id': task_id
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

if __name__ == '__main__':
    # post_count_result(Vehicle_count=0, Person_count=0, callback_url='http://199.19.110.7:7104/api/Callback', interface="count", rtsp_src="rtsp://199.19.110.7:7103/live/park", task_id="task20230630001")

    callAiboxService(countAPI_url='http://192.168.200.197:5002/count',rtsp_url= "rtsp://199.19.110.7:7103/live/park", callback_url="http://199.19.110.7:7104/api/Callback",task_id="task_20230630001")


