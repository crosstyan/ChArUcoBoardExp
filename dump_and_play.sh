#!/bin/bash

if [ -z $1 ]; then
    echo "Usage: $0 <port>"
    exit 1
else
    echo "dumping video from port $1"
fi

TARGET_PORT=$1;

if ! [[ $TARGET_PORT =~ ^[0-9]+$ ]] ; then
    echo "error: expect a number, got $TARGET_PORT" >&2
    exit 1
fi

# See also majestic.yaml
# Get the current date and time in the format YYYYMMDD-HHMMSS
DATE=$(date +"%Y%m%d-%H%M%S")

# use mts as MPEG transport stream
FILENAME="output/video-${DATE}-${TARGET_PORT}.mts"
# SINK="autovideosink"
SINK="glimagesink"


# Run the GStreamer pipeline with the dynamic filename
# gst-launch-1.0 -e udpsrc port=$TARGET_PORT \
# ! 'application/x-rtp,encoding-name=H265,payload=96' \
# ! rtph265depay \
# ! h265parse \
# ! tee name=t \
# t. ! queue ! $DECODER ! videoconvert ! $SINK \
# t. ! queue ! mp4mux ! filesink location=$FILENAME


# DECODER="nvh265dec"
# DECODER="vulkanh265dec"
# DECODER="avdec_h265"
DECODER="vtdec_hw"
# DECODER="vtdec"
# gst-launch-1.0 -e udpsrc port=$TARGET_PORT auto-multicast=true multicast-group=224.0.0.123 \
# ! 'application/x-rtp,encoding-name=H265,payload=96' \
# ! rtph265depay \
# ! tee name=t \
# ! h265parse \
# t. ! queue ! $DECODER ! videoconvert ! $SINK \
# t. ! queue ! mpegtsmux ! filesink location=$FILENAME

# hvc1
# hev1
gst-launch-1.0 -e udpsrc port=$TARGET_PORT auto-multicast=true multicast-group=224.0.0.123 \
! 'application/x-rtp,encoding-name=H265,payload=96' \
! rtph265depay \
! tee name=t \
t. ! queue ! h265parse ! "video/x-h265,stream-format=hvc1" ! $DECODER ! videoconvert ! $SINK \
t. ! queue ! h265parse ! mpegtsmux ! filesink location=$FILENAME

