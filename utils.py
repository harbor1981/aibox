import socket
import os
import signal
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

def killOneProcess(port):
    '''root authority is required'''
    command="kill -9 $(netstat -nlp | grep :"+str(port)+" | awk '{print $7}' | awk -F'/' '{{ print $1 }}')"
    os.system(command)

if __name__ == '__main__':
    killOneProcess(5000)
    # out_port=5000
    # ps_ports = [out_port]
    # killProcesses(*get_pid(*ps_ports))
