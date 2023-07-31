import time
import cv2

def alibaba(name):
    result=0
    for i in range(1000):
        result += i
        print('hello,%s,%d' % (name, i))
        time.sleep(5)


def split(path):
    print(path.split("|"))
def getRtspInfo(url):

    # 加载视频
    video = cv2.VideoCapture(url)
    while True:
        # 读取视频帧
        ret, frame = video.read()
        if not ret:
            break
        # 显示视频帧
        cv2.imshow("Video", frame)
        cv2.waitKey(1)
    video.release()
    cv2.destroyAllWindows()
import cv2


#######################################################3
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

def on_pad_added(element, pad):
    caps = pad.query_caps(None)
    structure = caps.get_structure(0)
    width = structure.get_int("width")
    height = structure.get_int("height")
    print("分辨率：", f"{width}x{height}")

def get_rtsp_info_ds(rtsp_url):
    pipeline_str = f'''
        uridecodebin uri={rtsp_url} name=source !
        videoconvert ! video/x-raw,format=BGR !
        fakesink
    '''

    pipeline = Gst.parse_launch(pipeline_str)
    source = pipeline.get_by_name('source')
    source.connect('pad-added', on_pad_added)

    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()

    while True:
        message = bus.timed_pop_filtered(
            Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

        if message.type == Gst.MessageType.ERROR:
            error, debug_info = message.parse_error()
            print(f"错误：{error.message}, {debug_info}")
            break

    pipeline.set_state(Gst.State.NULL)



if __name__ == '__main__':
    # alibaba('quejinlong')
    # import gi
    #
    # gi.require_version("Gtk", "3.0")
    # from gi.repository import Gtk
    #
    # window = Gtk.Window(title="Hello World")
    # window.show()
    # window.connect("destroy", Gtk.main_quit)
    # Gtk.main()
    # path = "rtsp://172.18.20.30/live/1"
    # split(path)
    # getRtspInfo("../../samples/streams/sample_720p.h264")
    get_rtsp_info("rtsp://199.19.110.7:7402/live/park")
