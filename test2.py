import time


def alibaba(name):
    result=0
    for i in range(1000):
        result += i
        print('hello,%s,%d' % (name, i))
        time.sleep(5)


if __name__ == '__main__':
    alibaba('quejinlong')