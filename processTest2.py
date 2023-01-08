from multiprocessing import Process
import os

# 子进程要执行的代码
def run_proc(Pinput="", Pport=1000,g='nvinfer'):
    print('Pinput=%s, Pport=%d,g=%s'% (inputURL, out_port,g))
    print()

if __name__=='__main__':
    inputURL="http://www.qq.com"
    out_port=9600
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_proc, args=(pro,out_port,111))
    print('Child process will start.')
    p.start()
    # p.join()
    print('Child process end.')