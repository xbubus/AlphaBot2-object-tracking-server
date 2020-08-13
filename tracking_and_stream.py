from flask import Flask, render_template, Response
from camera import Camera
import cv2

app=Flask(__name__)
cam=Camera()
cap=cam.start()

@app.route('/')
def index():
    return render_template('index.html')
    
def gen_frame():
    while cap:
        frame = cap.read()[0]
        convert = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n') 
def gen_mask():
    while cap:
        mask = cap.read()[1]
        convert = cv2.imencode('.jpg', mask)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n') 


@app.route('/video')
def video():
    return Response(gen_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video2')
def video2():
    return Response(gen_mask(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
