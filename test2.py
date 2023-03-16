import time


def alibaba(name):
    result=0
    for i in range(1000):
        result += i
        print('hello,%s,%d' % (name, i))
        time.sleep(5)


def split(path):
    print(path.split("|"))

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
    path = "rtsp://172.18.20.30/live/1"
    split(path)
