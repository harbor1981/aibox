# aibox

Prequisites:
- DeepStreamSDK 6.1.1
- Python 3.8
- Gst-python
- GstRtspServer
### Installing modules for deepstream-sdk

/opt/nvidia/deepstream/deepstream/user_additional_install.sh

### Installing GstRtspServer and instrospection typelib

apt update
apt-get install libgstrtspserver-1.0-0 gstreamer1.0-rtsp
apt-get install libgirepository1.0-dev
apt-get install gobject-introspection gir1.2-gst-rtsp-server-1.0
### Installing modules for service 
pip3 install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install flask  -i https://pypi.tuna.tsinghua.edu.cn/simple
sudo docker run --gpus all -it  --net=host --privileged -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/aibox/aibox:/opt/nvidia/deepstream/deepstream-6.1/sources/aibox -e DISPLAY=$DISPLAY -w /opt/nvidia/deepstream/deepstream-6.1/sources/aibox --name aibox  nvcr.io/nvidia/deepstream:6.1.1-devel