import numpy as np
import cv2
import socket
import json
import time
import copy
## raspbery init:
#raspivid -t 0 -cd MJPEG -w 640 -h 480 -fps 40 -b 8000000 -o - | gst-launch-1.0 fdsrc ! "image/jpeg,framerate=40/1" ! jpegparse ! rtpjpegpay ! udpsink host=192.168.41.3 port=4001
import paho.mqtt.client as mqtt
import argparse
HOST = '10.9.111.129'
PORT = 8083



topic='rpi/object_tracking'
ip='10.9.111.128'
port='1883'
client =mqtt.Client("rpi_publisher")
client.connect('localhost',keepalive=3600)
print("connected to mqtt broker")
WIDTH=640
HEIGHT=480
CENTER_X=WIDTH/2
CENTER_Y=HEIGHT/2

def find_lemon(frame):
    frame = cv2.GaussianBlur(frame,(9,9),0)
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #lower_yellow = np.array([25,120,100])
    #upper_yellow = np.array([40,255,255])
   #lower_tenis_ball=np.array([0.09*256,0.6*256,0.2*256])
   # upper_tenis_ball=np.array([0.14*256,256,256])
    lower_tenis_ball=np.array([32,86,75]) #32,86,75
    upper_tenis_ball=np.array([78,255,255])#65,255,255  dobre
    mask = cv2.inRange(hsv, lower_tenis_ball, upper_tenis_ball)
  
    kernel1 = np.ones((9, 9), np.uint8)
    kernel2 = np.ones((5, 5), np.uint8)
    mask_before_erdi=mask
    mask = cv2.erode  (mask, kernel1, iterations=2)
    mask = cv2.dilate (mask, kernel2, iterations=3)
    
  
    
    contour_image = np.copy(mask)
    contours, _ = cv2.findContours(contour_image, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    circles = [cv2.minEnclosingCircle(cnt) for cnt in contours]
    largest = (0, 0), 0
    for (x, y), radius in circles:
        if radius > largest[1] and radius >15:
            largest = (int(x), int(y)), int(radius)
    return mask, largest[0], largest[1],mask_before_erdi,hsv

def process_frame(frame):
    masked, coordinates, radius,mask_before_erdi,hsv = find_lemon(frame)
    processed = cv2.cvtColor(masked, cv2.COLOR_GRAY2BGR)
    cv2.circle(frame, coordinates, radius, [255, 0, 0])
    return coordinates, radius, masked,frame,mask_before_erdi,hsv




cap = cv2.VideoCapture('udpsrc port=4001 caps = "application/x-rtp,media=(string)video, clock-rate=(int)90000,encoding-name=(string)JPEG,a-framerate=(string)40.000000,a-framesize=(string)640-480,payload=(int)26" ! rtpjpegdepay ! decodebin !videoconvert ! appsink', cv2.CAP_GSTREAMER)
frame_counter=0
while True:
    ret_val, frame = cap.read()
    if not ret_val:
        print('VidepCapture.read() failed. Exiting...')
        break
    org_frame=copy.copy(frame)
   # cv2.imshow("picamera", frame)
    mask=process_frame(frame)
    #print(mask[0],mask[1])
   # cv2.imshow("original frame",org_frame)
   # cv2.imshow("hsv image",mask[5])
   # cv2.imshow("mask before denoising",mask[4])
   # cv2.imshow("mask",mask[2])
   # cv2.imshow("final frame",mask[3])
   # cv2.imwrite("original_frame.jpg",org_frame)
   # cv2.imwrite("hsv image.jpg",mask[5])
   # cv2.imwrite("mask_before_denoising.jpg",mask[4])
   # cv2.imwrite("mask.jpg",mask[2])
   # cv2.imwrite("final_frame.jpg",mask[3])
    frame_counter+=1
    if mask[1]>0:
        if mask[1]>15:
            frame_counter=0
            xoff=int(mask[0][0]-CENTER_X)
            yoff=int(mask[0][1]-CENTER_Y)
            data = json.dumps({"xoff": mask[0][0]-CENTER_X,"radius":mask[1],"yoff":yoff})
            client.publish(topic,data)
            print(topic,data)
    if frame_counter>5:
        data = json.dumps({"xoff": 0,"radius":0,"yoff":0})
        client.publish(topic,data)
        frame_counter=0
 #   if cv2.waitKey(1) == 27:
#        break
cv2.destroyAllWindows()
cap.release()


