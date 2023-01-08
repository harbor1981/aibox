import base64
def hello(name):
   print("hello,%s"%(name))

def getURL():
   url="rtsp://192.168.1.5:8554/ds-test"
   return url

def getBaseCode(url):
    string = url.encode("utf-8")  # encode()不填时默认为utf-8
    base16 = base64.b16encode(string)
    print(base16)

if __name__ == '__main__':
    getURL()
    getBaseCode("rtsp://192.168.1.5:8554/ds-test")


