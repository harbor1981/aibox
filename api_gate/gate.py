#!/usr/bin/env python3

################################################################################
# SPDX-FileCopyrightText: Copyright (c) 2020-2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import sys

import utils

sys.path.append('../')
import gi
import configparser
gi.require_version('Gst', '1.0')
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GLib, Gst,GstRtspServer
import sys
import math
import platform
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call
from common.FPS import PERF_DATA
import httpPost

import pyds
perf_data = None

MAX_DISPLAY_LEN=64
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH=1920
MUXER_OUTPUT_HEIGHT=1080
MUXER_BATCH_TIMEOUT_USEC=4000000
TILED_OUTPUT_WIDTH=1280
TILED_OUTPUT_HEIGHT=720
GST_CAPS_FEATURES_NVMM="memory:NVMM"
OSD_PROCESS_MODE= 0
OSD_DISPLAY_TEXT= 1
pgie_classes_str= ["Vehicle", "TwoWheeler", "Person","RoadSign"]

# nvanlytics_src_pad_buffer_probe  will extract metadata received on nvtiler sink pad
# and update params for drawing rectangle, object information etc.
def nvanalytics_src_pad_buffer_probe(pad,info,u_data):
    frame_number=0
    num_rects=0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list

    while l_frame:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number=frame_meta.frame_num

        if(frame_number%50==0):
            l_obj = frame_meta.obj_meta_list
            num_rects = frame_meta.num_obj_meta
            obj_counter = {
                PGIE_CLASS_ID_VEHICLE: 0,
                PGIE_CLASS_ID_PERSON: 0,
                PGIE_CLASS_ID_BICYCLE: 0,
                PGIE_CLASS_ID_ROADSIGN: 0
            }
            print("#" * 50)
            while l_obj:
                try:
                    # Note that l_obj.data needs a cast to pyds.NvDsObjectMeta
                    # The casting is done by pyds.NvDsObjectMeta.cast()
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break
                obj_counter[obj_meta.class_id] += 1
                l_user_meta = obj_meta.obj_user_meta_list
                # Extract object level meta data from NvDsAnalyticsObjInfo
                while l_user_meta:
                    try:
                        user_meta = pyds.NvDsUserMeta.cast(l_user_meta.data)
                        if user_meta.base_meta.meta_type == pyds.nvds_get_user_meta_type(
                                "NVIDIA.DSANALYTICSOBJ.USER_META"):
                            user_meta_data = pyds.NvDsAnalyticsObjInfo.cast(user_meta.user_meta_data)
                            if user_meta_data.dirStatus: print(
                                "Object {0} moving in direction: {1}".format(obj_meta.object_id,
                                                                             user_meta_data.dirStatus))
                            if user_meta_data.lcStatus: print(
                                "Object {0} line crossing status: {1}".format(obj_meta.object_id,
                                                                              user_meta_data.lcStatus))
                            if user_meta_data.ocStatus: print(
                                "Object {0} overcrowding status: {1}".format(obj_meta.object_id,
                                                                             user_meta_data.ocStatus))
                            if user_meta_data.roiStatus: print(
                                "Object {0} roi status: {1}".format(obj_meta.object_id, user_meta_data.roiStatus))
                    except StopIteration:
                        break

                    try:
                        l_user_meta = l_user_meta.next
                    except StopIteration:
                        break
                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break

            # Get meta data from NvDsAnalyticsFrameMeta
            l_user = frame_meta.frame_user_meta_list
            while l_user:
                try:
                    user_meta = pyds.NvDsUserMeta.cast(l_user.data)
                    if user_meta.base_meta.meta_type == pyds.nvds_get_user_meta_type(
                            "NVIDIA.DSANALYTICSFRAME.USER_META"):
                        user_meta_data = pyds.NvDsAnalyticsFrameMeta.cast(user_meta.user_meta_data)
                        if user_meta_data.objInROIcnt: print("Objs in ROI: {0}".format(user_meta_data.objInROIcnt))
                        if user_meta_data.objLCCumCnt: print(
                            "Linecrossing Cumulative: {0}".format(user_meta_data.objLCCumCnt))
                        if user_meta_data.objLCCurrCnt: print(
                            "Linecrossing Current Frame: {0}".format(user_meta_data.objLCCurrCnt))
                        if user_meta_data.ocStatus: print("Overcrowding status: {0}".format(user_meta_data.ocStatus))
                        ################################
                        # print("####################################{0}".format(user_meta_data.objLCCumCnt['car_in']))
                        car_in = user_meta_data.objLCCumCnt['car_in']
                        car_out = 0
                        person_in = user_meta_data.objLCCumCnt['person_in']
                        person_out = user_meta_data.objLCCumCnt['person_out']

                        httpPost.post_gate_result(car_in, car_out, person_in, person_out, callback_url, method,
                                                  rtsp_src, task_id)

                        ################################

                except StopIteration:
                    break
                try:
                    l_user = l_user.next
                except StopIteration:
                    break

            print("Frame Number=", frame_number, "stream id=", frame_meta.pad_index, "Number of Objects=", num_rects,
                  "Vehicle_count=", obj_counter[PGIE_CLASS_ID_VEHICLE], "Person_count=",
                  obj_counter[PGIE_CLASS_ID_PERSON])
            # Update frame rate through this probe
            stream_index = "stream{0}".format(frame_meta.pad_index)
            global perf_data
            perf_data.update_fps(stream_index)
            print("#" * 50)
        try:
            l_frame=l_frame.next
        except StopIteration:
            break


    return Gst.PadProbeReturn.OK



def cb_newpad(decodebin, decoder_src_pad,data):
    print("In cb_newpad\n")
    caps=decoder_src_pad.get_current_caps()
    gststruct=caps.get_structure(0)
    gstname=gststruct.get_name()
    source_bin=data
    features=caps.get_features(0)

    # Need to check if the pad created by the decodebin is for video and not
    # audio.
    print("gstname=",gstname)
    if(gstname.find("video")!=-1):
        # Link the decodebin pad only if decodebin has picked nvidia
        # decoder plugin nvdec_*. We do this by checking if the pad caps contain
        # NVMM memory features.
        print("features=",features)
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad=source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write("Failed to link decoder src pad to source bin ghost pad\n")
        else:
            sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")

def decodebin_child_added(child_proxy,Object,name,user_data):
    print("Decodebin child added:", name, "\n")
    if(name.find("decodebin") != -1):
        Object.connect("child-added",decodebin_child_added,user_data)

def create_source_bin(index,uri):
    print("Creating source bin")

    # Create a source GstBin to abstract this bin's content from the rest of the
    # pipeline
    bin_name="source-bin-%02d" %index
    print(bin_name)
    nbin=Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write(" Unable to create source bin \n")

    # Source element for reading from the uri.
    # We will use decodebin and let it figure out the container format of the
    # stream and the codec and plug the appropriate demux and decode plugins.
    uri_decode_bin=Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        sys.stderr.write(" Unable to create uri decode bin \n")
    # We set the input uri to the source element
    uri_decode_bin.set_property("uri",uri)
    # Connect to the "pad-added" signal of the decodebin which generates a
    # callback once a new pad for raw data has beed created by the decodebin
    uri_decode_bin.connect("pad-added",cb_newpad,nbin)
    uri_decode_bin.connect("child-added",decodebin_child_added,nbin)

    # We need to create a ghost pad for the source bin which will act as a proxy
    # for the video decoder src pad. The ghost pad will not have a target right
    # now. Once the decode bin creates the video decoder and generates the
    # cb_newpad callback, we will set the ghost pad target to the video decoder
    # src pad.
    Gst.Bin.add(nbin,uri_decode_bin)
    bin_pad=nbin.add_pad(Gst.GhostPad.new_no_target("src",Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write(" Failed to add ghost pad in source bin \n")
        return None
    return nbin

def main(args):
    # Check input arguments,暂时改为1
    if len(args) < 1:
        sys.stderr.write("usage: %s <uri1> [uri2] ... [uriN]\n" % args[0])
        sys.exit(1)

    global perf_data
    perf_data = PERF_DATA(len(args))
    number_sources=len(args)

    # Standard GStreamer initialization
    Gst.init(None)

    # Create gstreamer elements */
    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    is_live = False

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")
    print("Creating streamux \n ")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")

    pipeline.add(streammux)
    for i in range(number_sources):
        print("Creating source_bin ",i," \n ")
        uri_name=args[i]
        if uri_name.find("rtsp://") == 0 :
            is_live = True
        ## todo create_source_bin
        source_bin=create_source_bin(i, uri_name)
        if not source_bin:
            sys.stderr.write("Unable to create source bin \n")
        pipeline.add(source_bin)
        padname="sink_%u" %i
        ## todo get_request_pad
        sinkpad= streammux.get_request_pad(padname) 
        if not sinkpad:
            sys.stderr.write("Unable to create sink pad bin \n")
        srcpad=source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("Unable to create src pad bin \n")
        srcpad.link(sinkpad)
    queue1=Gst.ElementFactory.make("queue","queue1")
    queue2=Gst.ElementFactory.make("queue","queue2")
    queue3=Gst.ElementFactory.make("queue","queue3")
    queue4=Gst.ElementFactory.make("queue","queue4")
    queue5=Gst.ElementFactory.make("queue","queue5")
    queue6=Gst.ElementFactory.make("queue","queue6")
    queue7=Gst.ElementFactory.make("queue","queue7")
    pipeline.add(queue1)
    pipeline.add(queue2)
    pipeline.add(queue3)
    pipeline.add(queue4)
    pipeline.add(queue5)
    pipeline.add(queue6)
    pipeline.add(queue7)

    print("Creating Pgie \n ")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")

    print("Creating nvtracker \n ")
    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    if not tracker:
        sys.stderr.write(" Unable to create tracker \n")

    print("Creating nvdsanalytics \n ")
    nvanalytics = Gst.ElementFactory.make("nvdsanalytics", "analytics")
    if not nvanalytics:
        sys.stderr.write(" Unable to create nvanalytics \n")
    nvanalytics.set_property("config-file", "./api_gate/config_nvdsanalytics.txt")

    print("Creating tiler \n ")
    tiler=Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write(" Unable to create tiler \n")

    print("Creating nvvidconv \n ")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")

    print("Creating nvosd \n ")
    ##todo onscreendisplay，process-mode，display-text
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")
    nvosd.set_property('process-mode',OSD_PROCESS_MODE)
    nvosd.set_property('display-text',OSD_DISPLAY_TEXT)

    if(is_aarch64()):
        print("Creating transform \n ")
        transform=Gst.ElementFactory.make("nvegltransform", "nvegl-transform")
        if not transform:
            sys.stderr.write(" Unable to create transform \n")
####################################################################################################

    nvvidconv_postosd = Gst.ElementFactory.make(
        "nvvideoconvert", "convertor_postosd")
    if not nvvidconv_postosd:
        sys.stderr.write(" Unable to create nvvidconv_postosd \n")

    # Create a caps filter
    caps = Gst.ElementFactory.make("capsfilter", "filter")
    caps.set_property(
        "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
    )
    # codec="H264"
    # bitrate=4000000
    # Make the encoder
    if codec == "H264":
        encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
        print("Creating H264 Encoder")
    elif codec == "H265":
        encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
        print("Creating H265 Encoder")
    if not encoder:
        sys.stderr.write(" Unable to create encoder")
    encoder.set_property("bitrate", bitrate)
    if is_aarch64():
        encoder.set_property("preset-level", 1)
        encoder.set_property("insert-sps-pps", 1)
        #encoder.set_property("bufapi-version", 1)

    # Make the payload-encode video into RTP packets
    if codec == "H264":
        rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
        print("Creating H264 rtppay")
    elif codec == "H265":
        rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
        print("Creating H265 rtppay")
    if not rtppay:
        sys.stderr.write(" Unable to create rtppay")

    # Make the UDP sink
    updsink_port_num = 5400
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    if not sink:
        sys.stderr.write(" Unable to create udpsink")

    sink.set_property("host", "224.224.255.255")
    sink.set_property("port", updsink_port_num)
    sink.set_property("async", False)
    sink.set_property("sync", 1)
    #######################################################################################
    # print("Creating EGLSink \n")
    # sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    # # sink = Gst.ElementFactory.make("fakesink", "nvvideo-renderer")
    # if not sink:
    #     sys.stderr.write(" Unable to create egl sink \n")

    if is_live:
        print("At least one of the sources is live")
        streammux.set_property('live-source', 1)
    streammux.set_property('width', 1920)
    streammux.set_property('height', 1080)
    streammux.set_property('batch-size', number_sources)
    streammux.set_property('batched-push-timeout', 4000000)
    ###
    pgie.set_property('config-file-path', "./api_gate/dsnvanalytics_pgie_config.txt")
    pgie_batch_size=pgie.get_property("batch-size")
    if(pgie_batch_size != number_sources):
        print("WARNING: Overriding infer-config batch-size",pgie_batch_size," with number of sources ", number_sources," \n")
        pgie.set_property("batch-size",number_sources)
    ###
    tiler_rows=int(math.sqrt(number_sources))
    tiler_columns=int(math.ceil((1.0*number_sources)/tiler_rows))
    tiler.set_property("rows",tiler_rows)
    tiler.set_property("columns",tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    sink.set_property("qos",0)
    #Set properties of tracker
    config = configparser.ConfigParser()
    config.read('./api_gate/dsnvanalytics_tracker_config.txt')
    config.sections()

    for key in config['tracker']:
        if key == 'tracker-width' :
            tracker_width = config.getint('tracker', key)
            tracker.set_property('tracker-width', tracker_width)
        if key == 'tracker-height' :
            tracker_height = config.getint('tracker', key)
            tracker.set_property('tracker-height', tracker_height)
        if key == 'gpu-id' :
            tracker_gpu_id = config.getint('tracker', key)
            tracker.set_property('gpu_id', tracker_gpu_id)
        if key == 'll-lib-file' :
            tracker_ll_lib_file = config.get('tracker', key)
            tracker.set_property('ll-lib-file', tracker_ll_lib_file)
        if key == 'll-config-file' :
            tracker_ll_config_file = config.get('tracker', key)
            tracker.set_property('ll-config-file', tracker_ll_config_file)
        if key == 'enable-batch-process' :
            tracker_enable_batch_process = config.getint('tracker', key)
            tracker.set_property('enable_batch_process', tracker_enable_batch_process)
        if key == 'enable-past-frame' :
            tracker_enable_past_frame = config.getint('tracker', key)
            tracker.set_property('enable_past_frame', tracker_enable_past_frame)

    print("Adding elements to Pipeline \n")
    pipeline.add(pgie)
    pipeline.add(tracker)
    pipeline.add(nvanalytics)
    pipeline.add(tiler)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    ###################
    pipeline.add(nvvidconv_postosd)
    pipeline.add(caps)
    pipeline.add(encoder)
    pipeline.add(rtppay)
    pipeline.add(sink)
    #######################

    # if is_aarch64():
    #     pipeline.add(transform)
    # pipeline.add(sink)

    # We link elements in the following order:
    # sourcebin -> streammux -> nvinfer -> nvtracker -> nvdsanalytics ->
    # nvtiler -> nvvideoconvert -> nvdsosd -> sink
    print("Linking elements in the Pipeline \n")
    # streammux.link(queue1)
    # queue1.link(pgie)
    # pgie.link(queue2)
    # queue2.link(tracker)
    # tracker.link(queue3)
    # queue3.link(nvanalytics)
    # nvanalytics.link(queue4)
    # queue4.link(tiler)
    # tiler.link(queue5)
    # queue5.link(nvvidconv)
    # nvvidconv.link(queue6)
    # queue6.link(nvosd)
    # if is_aarch64():
    #     nvosd.link(queue7)
    #     queue7.link(transform)
    #     transform.link(sink)
    # else:
    #     nvosd.link(queue7)
    #     queue7.link(sink)

    streammux.link(pgie)
    pgie.link(tracker)
    tracker.link(nvanalytics)
    # nvanalytics.link(tiler)
    # tiler.link(nvvidconv)
    nvanalytics.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(nvvidconv_postosd)
    nvvidconv_postosd.link(caps)
    caps.link(encoder)
    encoder.link(rtppay)
    rtppay.link(sink)

    # create an event loop and feed gstreamer bus mesages to it
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)
    # nvanalytics_src_pad=nvanalytics.get_static_pad("src")
    # if not nvanalytics_src_pad:
    #     sys.stderr.write(" Unable to get src pad \n")
    # else:
    #     nvanalytics_src_pad.add_probe(Gst.PadProbeType.BUFFER, nvanalytics_src_pad_buffer_probe, 0)
    #     # perf callback function to print fps every 5 sec
    #     GLib.timeout_add(5000, perf_data.perf_print_callback)
    osdsinkpad = nvosd.get_static_pad("sink")
    if not osdsinkpad:
        sys.stderr.write(" Unable to get sink pad of nvosd \n")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, nvanalytics_src_pad_buffer_probe, 0)
    GLib.timeout_add(5000, perf_data.perf_print_callback)
    ##############################################################
    # Start streaming
    # rtsp_port_num = 9600

    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % rtsp_port_num
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
        % (updsink_port_num, codec)
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory("/%s"%(method), factory)
    host_ip = utils.get_host_ip()

    print(
        "\n *** DeepStream: Launched RTSP Streaming at rtsp://%s:%d/%s ***\n\n"
        % (host_ip, rtsp_port_num,method)
    )
    ###################################################################

    # List the sources
    print("Now playing...")
    for i, source in enumerate(args):
        if (i != 0):
            print(i, ": ", source)

    print("Starting pipeline \n")
    # start play back and listed to events		
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # cleanup
    print("Exiting app\n")
    pipeline.set_state(Gst.State.NULL)

def invokeGate(Pcodec='H264', Pbitrate=4000000, Pinput='', Pgie='nvinfer', Pport=9600, Pcallback_url="", Pmethod="gate", Ptask_id=""):
    global codec
    global bitrate
    global stream_path
    global gie
    global rtsp_port_num
    global callback_url
    global method
    global rtsp_src
    global task_id
    codec = Pcodec
    bitrate = Pbitrate
    # stream_path = []
    # stream_path.append(Pinput)
    stream_path=Pinput.split("|")
    gie = Pgie
    rtsp_port_num = Pport
    callback_url = Pcallback_url
    method = Pmethod
    rtsp_src = stream_path
    task_id = Ptask_id
    sys.exit(main(stream_path))
    return stream_path

if __name__ == '__main__':
    # sys.exit(main(sys.argv))

    invokeGate(Pinput='rtsp://199.19.110.7:7103/live/park', Pport=9600)