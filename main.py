import cv2
import numpy as np
import pyshine as ps
from win32 import win32api
import win32.lib.win32con as win32con
import time
import serial
import serial.tools.list_ports
import base64

vcW = 640
vcH = 480

leftClickOnDown = False
image_coordinates = [0,0,0,0]
arduinoPort = []
arduino = None
bbox = None
byteform = b'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'
logo_jpeg = base64.b64decode(byteform)
jpeg_as_np = np.frombuffer(logo_jpeg, dtype=np.uint8)
logo = cv2.imdecode(jpeg_as_np, flags = 1)
def drawBox(img, bbox):
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    xc = x+w//2
    yc = y+h//2
    cv2.rectangle(img, (x, y), ((x+w), (y+h)), (255, 0, 255), 3, 1)
    cv2.circle(img, (xc, yc), 5, (255, 0, 255), -1)
    # drawInfo(img, "Status", 1, "Tracking", True)
    height = img.shape[0]
    width = img.shape[1]
    yy = height//2
    xx = width//2
    cv2.line(img, (xx-w//2, yy),
             (xx+w//2, yy), (255, 255, 255), 2)

    cv2.line(img, (xx, yy-h//2),
             (xx, yy+h//2), (255, 255, 255), 2)
    jari2 = 10/100 * w
    cv2.circle(img, (xx, yy), int(jari2), (255, 255, 255), 2)
    num = ""
    if yc > yy - jari2 and yc < yy + jari2 and xc > xx - jari2 and xc < xx + jari2:
        num = "H"
    else:
        if yc < yy - jari2:
            num += "A"
        elif yc > yy + jari2:
            num += "B"

        if xc < xx - jari2:
            num += "C"

        elif xc > xx + jari2:
            num += "D"
        

    # drawInfo(img, "DATA", 3, num, True)
    cv2.putText(img, f'DATA: {num}', (10, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    return num

def mouse_evt_SSC(event, x, y, flags, param):
    global runCam, runApp, cap, tracker, arduino
    if boxSS[0] < x  and x < boxSS[2] and boxSS[1] < y and y < boxSS[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            cap = cv2.VideoCapture(0)
            tracker = cv2.legacy.TrackerCSRT_create()
            runCam = not runCam
            
    elif boxClose[0] < x  and x < boxClose[2] and boxClose[1] < y and y < boxClose[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runApp = not runApp
            
    elif 0 < x  and x < 640 and 100 < y and y < 580:
        if event == cv2.EVENT_LBUTTONUP and bbox:
            cap = cv2.VideoCapture(0)
            tracker = cv2.legacy.TrackerCSRT_create()
            runCam = not runCam
    
    if len(arduinoPort)!= 0:
        if boxConnection[0] < x  and x < boxConnection[2] and boxConnection[1] < y and y < boxConnection[3]:
            win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
            if event == cv2.EVENT_LBUTTONDOWN:
                if arduino:
                    arduino.close()
                    arduino = None
                else:
                    arduino = serial.Serial(arduinoPort[0], baudrate=9600)
            
def mouse_evt(event, x, y, flags, param):
    global runCam, runApp, flip, image_coordinates, leftClickOnDown, arduino, bbox
    if boxSS[0] < x  and x < boxSS[2] and boxSS[1] < y and y < boxSS[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runCam = not runCam
            
    elif boxClose[0] < x  and x < boxClose[2] and boxClose[1] < y and y < boxClose[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runCam = not runCam
            runApp = not runApp
            
    elif boxFlip[0] < x  and x < boxFlip[2] and boxFlip[1] < y and y < boxFlip[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            flip = not flip
            
    elif 0 < x  and x < 640 and 100 < y and y < 580:
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            if bbox != (0.0, 0.0, 0.0, 0.0):
                runCam = not runCam
            else:
                image_coordinates[0], image_coordinates[1] = x, y
                leftClickOnDown = True
        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            leftClickOnDown = False
            bbox = (image_coordinates[0],image_coordinates[1],image_coordinates[2]-image_coordinates[0],image_coordinates[3]-image_coordinates[1])
            tracker.init(img, bbox)
            image_coordinates = [0,0,0,0]
        if leftClickOnDown:
            image_coordinates[2], image_coordinates[3] = x, y
    
    if len(arduinoPort)!= 0:
        if boxConnection[0] < x  and x < boxConnection[2] and boxConnection[1] < y and y < boxConnection[3]:
            win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
            if event == cv2.EVENT_LBUTTONDOWN:
                if arduino:
                    arduino.close()
                    arduino = None
                else:
                    arduino = serial.Serial(arduinoPort[0], baudrate=9600)


def connection(img):
    global boxConnection
    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    for p in myports:
        if "CH340" in p[1] or "Arduino" in p[1]:
            arduinoPort.append(p[0]) if p[0] not in arduinoPort else arduinoPort
    
    if len(arduinoPort)== 0:
        cv2.putText(img, 'COM: Not Available', (10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    else:
        if arduino:
            cv2.putText(img, f"COM: Connect To {arduinoPort[0]}", (10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        else:
            listToStr = 'and'.join([str(elem) for elem in arduinoPort])
            cv2.putText(img, f"COM: {listToStr} {'is available' if len(arduinoPort) < 2 else 'are availables'} ", (10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        img, boxConnection =  ps.putBText(img,'Disconnect' if arduino else 'Connect',text_offset_x=20,text_offset_y=blank_image.shape[0]-85,vspace=10,hspace=10, font_scale=1.0,background_RGB=(252, 3, 211),text_RGB=(255,250,250))
    

runApp = True
runCam = False
flip = False
while runApp:
    blank_image = np.zeros((vcH+200,vcW,3), np.uint8)
    blank_image[0:100, 530:632] = logo
    
    connection(blank_image)
    blank_image, boxSS =  ps.putBText(blank_image,'Stop' if runCam else 'Start',text_offset_x=blank_image.shape[1]-100,text_offset_y=blank_image.shape[0]-85,vspace=10,hspace=10, font_scale=1.0,background_RGB=(20,210,4),text_RGB=(255,250,250))
    blank_image, boxClose =  ps.putBText(blank_image,'Close',text_offset_x=blank_image.shape[1]-100,text_offset_y=blank_image.shape[0]-35,vspace=10,hspace=10, font_scale=1.0,background_RGB=(242, 66, 53),text_RGB=(255,250,250))
    pTime = 0
    while runCam:            
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        success, img = cap.read()
        if flip:
            img = cv2.flip(img, 1)
            
        success, bbox = tracker.update(img)
            
        blank_image = np.zeros((vcH+200,vcW,3), np.uint8)
        blank_image[0:100, 530:632] = logo
        blank_image[100:580, 0:640] = img
        
        connection(blank_image)
        
        if image_coordinates != [0,0,0,0,]:
            pt1, pt2 = (image_coordinates[0], image_coordinates[1]), (image_coordinates[2], image_coordinates[3])
            cv2.rectangle(blank_image, pt1, pt2, (255, 0, 255), 3, 1)
       
        blank_image, boxFlip =  ps.putBText(blank_image,'Flip',text_offset_x=20,text_offset_y=blank_image.shape[0]-35,vspace=10,hspace=10, font_scale=1.0,background_RGB=(90, 128, 242),text_RGB=(255,250,250))
        blank_image, boxSS =  ps.putBText(blank_image,'Stop' if runCam else 'Start',text_offset_x=blank_image.shape[1]-100,text_offset_y=blank_image.shape[0]-85,vspace=10,hspace=10, font_scale=1.0,background_RGB=(20,210,4),text_RGB=(255,250,250))
        blank_image, boxClose =  ps.putBText(blank_image,'Close',text_offset_x=blank_image.shape[1]-100,text_offset_y=blank_image.shape[0]-35,vspace=10,hspace=10, font_scale=1.0,background_RGB=(242, 66, 53),text_RGB=(255,250,250))
        
        if success:
            data = drawBox(blank_image, bbox)
            try:
                arduino.write(str.encode(data))
            except:
                arduino = None
                
        else:
            cv2.putText(blank_image, 'Status: Lost', (10, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
            
        
        cv2.putText(blank_image, f'FPS: {int(fps)}', (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.imshow("Object Tracking", blank_image)
        cv2.setMouseCallback("Object Tracking", mouse_evt)
        k = cv2.waitKey(1)
        if k == ord("q"):
            runCam = not runCam
            break
        elif k == ord("f"):
            flip = not flip
        pTime = cTime
    cv2.imshow("Object Tracking", blank_image)
    cv2.setMouseCallback("Object Tracking", mouse_evt_SSC)
    k = cv2.waitKey(1)
    if k == ord("q"):
        runApp = not runApp
        break
    