import requests


def post_result(Vehicle_count=0,Person_count=0,post_url='http://199.19.110.7:7104/api/Callback'):
    global data
    # post_url = 'http://199.19.110.7:7104/api/Callback'
    # 创建包含要发送的参数的字典
    data = {
        'Vehicle_count': Vehicle_count,
        'Person_count': Person_count
    }
    # 发送POST请求
    response = requests.post(post_url, data=data)
    # 检查响应状态码
    if response.status_code == 200:
        print('请求已成功发送')
    else:
        print('请求失败')

if __name__ == '__main__':
    post_result(1,1)
