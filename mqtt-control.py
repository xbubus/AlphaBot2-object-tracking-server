import readchar
import sys
import paho.mqtt.client as mqtt
topic_motors='rpi/motors'
topic_camera='rpi/camera'
client =mqtt.Client("rpi_motor/camera")
print("Trying to connect to mqtt broker")
client.connect('localhost',keepalive=3600)
print("connected")
#publishes varius messeges on diffrent topics depending of key pressed
while True:
    val=repr(readchar.readchar())
    val=val[1:2]
    print(val)
    #motor movement
    if val=='w':
        client.publish(topic_motors,'forward')
    elif val=='a':
        client.publish(topic_motors,'left')
    elif val=='d':
        client.publish(topic_motors,'right')
    elif val=='s':
        client.publish(topic_motors,'backward')
    elif val=='q':
        client.publish(topic_motors,'stop')
    #camera movement
    elif val=='i':
        client.publish(topic_camera,'up')
    elif val=='k':
        client.publish(topic_camera,'down')
    elif val=='j':
        client.publish(topic_camera,'left')
    elif val=='l':
        client.publish(topic_camera,'right')
    elif val=='x':
        client.publish(topic_motors,'stop')
        client.publish(topic_camera,'stop')
        sys.exit()
    else:
        client.publish(topic_motors,'stop')
        client.publish(topic_camera,'stop')
