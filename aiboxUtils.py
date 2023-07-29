import socket
import os
import signal
import string
import random

import numpy as np
import psutil as psutil


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
def killProcesses(*pids):
  for pid in pids:
    a = os.kill(pid, signal.SIGKILL)
    print('已杀死pid为%s的进程,　返回值是:%s' % (pid, a))

def get_pid(*ports):
	#其中\"为转义"
  pids = []
  for port in ports:
    pid = os.popen("netstat -nlp | grep :%s | awk '{print $7}' | awk -F\" / \" '{ print $1 }'" % (port)).read().split('/')[0]
    if pid:
      pids.append(int(pid))
  return pids
def killProcessByName(processName):
    pids = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        # get process name according to pid
        process_name = p.name()
        if process_name.find(processName)!=-1:
            print("Process name is: %s, pid is: %s" % (process_name, pid))
            os.kill(pid, signal.SIGKILL)  

def killProcessByPort(port):
    code='200'
    msg='success'
    data='data'
    if port==0:
        print("111111111111111111111111111111111")
        for i in range(30):
            command="kill -9 $(netstat -nlp | grep :"+str(9600+i)+" | awk '{print $7}' | awk -F'/' '{{ print $1 }}')"
            print(command)
            os.system(command)
        msg="all processes have been killed"
        return code,msg,data
    elif 9600<=port and port<9630:
        '''root authority is required'''
        command="kill -9 $(netstat -nlp | grep :"+str(port)+" | awk '{print $7}' | awk -F'/' '{{ print $1 }}')"
        os.system(command)
        msg='%s has been killed'%(port)
        return code,msg,data
    else:
        code='-1'
        msg='error!port must in (9600,9630)'
        return code,msg,data

def generateFiles(nums):
    a = 1
    while (a <= nums):
        fwrite = str(a) + "git submodule update --init的使用方式git submodule update --init的使用方式 \n"
        file = open("/home/quejl/files/" + str(a) + ".txt", "a")
        f = 0
        while (f <= 100):
            f += 1
            file.write(fwrite)
        file.close()
        a += 1
def generateBigFile():
    n = 1024 ** 2  # 1 Mb of text
    letters = np.array(list(chr(ord('a') + i) for i in range(26)))
    chars = np.random.choice(np.fromstring(letters, dtype='<U1'), n)
    with open('/home/quejl/textfile111.txt', 'w+') as f:
        f.write(''.join(chars))
def generateBigFiles(nums,filePath):
    a = 1
    letters = np.array(list(chr(ord('a') + i) for i in range(26)))
    while (a <= nums):
        n = 100 ** 2*random.randint(1,500)  # 0.1Mb-5Mb of text
        chars = np.random.choice(np.fromstring(letters, dtype='<U1'), n)
        with open(filePath + str(a) + ".txt", 'w+') as f:
            f.write(''.join(chars))
        a += 1

def update_gate_config(config_file, lineCrossingCarIn,lineCrossingCarOut,lineCrossingPersonIn,lineCrossingPersonOut):
    new_values = {
        "line-crossing-car_in": lineCrossingCarIn,
        "line-crossing-car_out": lineCrossingCarOut,
        "line-crossing-person_in": lineCrossingPersonIn,
        "line-crossing-person_out": lineCrossingPersonOut,
    }
    with open(config_file, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        key_value = line.strip().split('=')
        if key_value[0].strip() in new_values:
            new_value = new_values[key_value[0].strip()]
            updated_line = f"{key_value[0].strip()} = {new_value}\n"
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    with open(config_file, 'w') as f:
        f.writelines(updated_lines)
        print("update_gate_config done!")


if __name__ == '__main__':
    # code,msg,data=killProcessByPort(9600)
    # print("code=%s,msg=%s,data=%s"%(code,msg,data))
    # killProcessByName("alibaba")
    # generateBigFiles(100,"/home/quejl/files2/")
    # generateBigFile()
    # killOneProcess(5000)
    # out_port=5000
    # ps_ports = [out_port]
    # killProcesses(*get_pid(*ps_ports))
    config_file = "api_gate/config_nvdsanalytics.txt"
    lineCrossingCarIn="100;500;400;1058;50;500;800;500;"
    lineCrossingCarOut="100;500;400;1058;50;500;800;500;"
    lineCrossingPersonIn="100;500;1300;1058;1200;400;1800;400;"
    lineCrossingPersonOut="100;1058;1400;500;1200;500;1600;500;"
    update_gate_config("api_gate/config_nvdsanalytics.txt",lineCrossingCarIn,lineCrossingCarOut,lineCrossingPersonIn,lineCrossingPersonOut)

