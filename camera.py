from threading import Thread, Lock
import cv2
import paho.mqtt.client as mqtt
import numpy as np
import json
topic='rpi/object_tracking'
port='1883'
WIDTH=640
HEIGHT=480
CENTER_X=WIDTH/2
CENTER_Y=HEIGHT/2

class Camera(object):
    def __init__(self):
        self.cap=cv2.VideoCapture('udpsrc port=4001 caps = "application/x-rtp,media=(string)video, clock-rate=(int)90000,encoding-name=(string)JPEG,a-framerate=(string)40.000000,a-framesize=(string)640-480,payload=(int)26" ! rtpjpegdepay ! decodebin !videoconvert ! appsink', cv2.CAP_GSTREAMER)
        self.frame_counter=0
        self.init_mqtt()
        self.started=False
        self.read_lock = Lock()
        self.frame_counter=0
    def start(self):
        if self.started:
            return None
        self.started=True
        self.thread=Thread(target=self.update)
        self.thread.start()
        return self
    def read(self):
        with self.read_lock:
            img=self.frame.copy()
            mask=self.mask.copy()
        return img,mask
    
    def update(self):
        
        while self.started:
            ret_val, frame = self.cap.read()
            with self.read_lock:
                self.output=self.process_frame(frame)
            if self.radius>0:
                print("radius:",self.radius)
            if self.output[1]>15:
                self.frame_counter=0
                xoff=int(self.output[0][0]-CENTER_X)
                yoff=int(self.output[0][1]-CENTER_Y)
                data = json.dumps({"xoff": xoff,"radius":self.output[1],"yoff":yoff})
                self.client.publish(topic,data)
            if self.frame_counter>10:
                data = json.dumps({"xoff": 0,"radius":0,"yoff":0})
                self.client.publish(topic,data)
            self.frame_counter+=1
    
    def init_mqtt(self):
        self.client =mqtt.Client("mec_publisher")
        self.client.connect('localhost',keepalive=3600)
        print("connected to mqtt broker")
        
    def find_ball(self,frame):
        frame = cv2.GaussianBlur(frame,(9,9),0)
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        lower_tenis_ball=np.array([32,86,75]) #32,86,75
        upper_tenis_ball=np.array([78,255,255])#65,255,255  dobre
        mask = cv2.inRange(hsv, lower_tenis_ball, upper_tenis_ball)
        kernel1 = np.ones((9, 9), np.uint8)
        kernel2 = np.ones((5, 5), np.uint8)
        mask = cv2.erode  (mask, kernel1, iterations=2)
        self.mask = cv2.dilate (mask, kernel2, iterations=3)
        contour_image = np.copy(mask)
        contours, _ = cv2.findContours(contour_image, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        circles = [cv2.minEnclosingCircle(cnt) for cnt in contours]
        largest = (0, 0), 0
        for (x, y), radius in circles:
            if radius > largest[1] and radius >15:
                largest = (int(x), int(y)), int(radius)
        return largest[0], largest[1],mask
        
    def process_frame(self,frame):
        self.coordinates, self.radius,masked= self.find_ball(frame)
        self.processed = cv2.cvtColor(masked, cv2.COLOR_GRAY2BGR)
        cv2.circle(frame, self.coordinates, self.radius, [255, 0, 0])
        self.frame=frame
        return self.coordinates, self.radius
        
    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()
