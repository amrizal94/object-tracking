import cv2
import numpy as np
import background_box as ps
from win32 import win32api
import win32.lib.win32con as win32con
import time
import serial
import serial.tools.list_ports
import base64
from logo_jpg_byte import byteform

vcW = 640
vcH = 480

leftClickOnDown = False
image_coordinates = [0, 0, 0, 0]
arduinoPort = []
arduino = None
bbox = None

logo_jpeg = base64.b64decode(byteform)
jpeg_as_np = np.frombuffer(logo_jpeg, dtype=np.uint8)
logo = cv2.imdecode(jpeg_as_np, flags=1)


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
    cv2.putText(img, f'DATA: {num}', (10, 40),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    return num


def mouse_evt_SSC(event, x, y, flags, param):
    global runCam, runApp, cap, tracker, arduino
    if boxSS[0] < x and x < boxSS[2] and boxSS[1] < y and y < boxSS[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            cap = cv2.VideoCapture(0)
            tracker = cv2.legacy.TrackerCSRT_create()
            runCam = not runCam

    elif boxClose[0] < x and x < boxClose[2] and boxClose[1] < y and y < boxClose[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runApp = not runApp

    elif 0 < x and x < 640 and 100 < y and y < 580:
        if event == cv2.EVENT_LBUTTONUP and bbox:
            cap = cv2.VideoCapture(0)
            tracker = cv2.legacy.TrackerCSRT_create()
            runCam = not runCam

    if len(arduinoPort) != 0:
        if boxConnection[0] < x and x < boxConnection[2] and boxConnection[1] < y and y < boxConnection[3]:
            win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
            if event == cv2.EVENT_LBUTTONDOWN:
                if arduino:
                    arduino.close()
                    arduino = None
                else:
                    arduino = serial.Serial(arduinoPort[0], baudrate=9600)


def mouse_evt(event, x, y, flags, param):
    global runCam, runApp, flip, image_coordinates, leftClickOnDown, arduino, bbox
    if boxSS[0] < x and x < boxSS[2] and boxSS[1] < y and y < boxSS[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runCam = not runCam

    elif boxClose[0] < x and x < boxClose[2] and boxClose[1] < y and y < boxClose[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runCam = not runCam
            runApp = not runApp

    elif boxFlip[0] < x and x < boxFlip[2] and boxFlip[1] < y and y < boxFlip[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            flip = not flip

    elif 0 < x and x < 640 and 100 < y and y < 580:
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
            bbox = (image_coordinates[0], image_coordinates[1], image_coordinates[2] -
                    image_coordinates[0], image_coordinates[3]-image_coordinates[1])
            tracker.init(img, bbox)
            image_coordinates = [0, 0, 0, 0]
        if leftClickOnDown:
            image_coordinates[2], image_coordinates[3] = x, y

    if len(arduinoPort) != 0:
        if boxConnection[0] < x and x < boxConnection[2] and boxConnection[1] < y and y < boxConnection[3]:
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
            arduinoPort.append(
                p[0]) if p[0] not in arduinoPort else arduinoPort

    if len(arduinoPort) == 0:
        cv2.putText(img, 'COM: Not Available', (10, 60),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    else:
        if arduino:
            cv2.putText(img, f"COM: Connect To {arduinoPort[0]}", (
                10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        else:
            listToStr = 'and'.join([str(elem) for elem in arduinoPort])
            cv2.putText(img, f"COM: {listToStr} {'is available' if len(arduinoPort) < 2 else 'are availables'} ", (
                10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        img, boxConnection = ps.putBText(img, 'Disconnect' if arduino else 'Connect', text_offset_x=20,
                                         text_offset_y=blank_image.shape[0]-85, vspace=10, hspace=10, font_scale=1.0, background_RGB=(252, 3, 211), text_RGB=(255, 250, 250))


runApp = True
runCam = False
flip = False
while runApp:
    blank_image = np.zeros((vcH+200, vcW, 3), np.uint8)
    blank_image[0:100, 530:632] = logo

    connection(blank_image)
    blank_image, boxSS = ps.putBText(blank_image, 'Stop' if runCam else 'Start', text_offset_x=blank_image.shape[
                                     1]-100, text_offset_y=blank_image.shape[0]-85, vspace=10, hspace=10, font_scale=1.0, background_RGB=(20, 210, 4), text_RGB=(255, 250, 250))
    blank_image, boxClose = ps.putBText(
        blank_image, 'Close', text_offset_x=blank_image.shape[1]-100, text_offset_y=blank_image.shape[0]-35, vspace=10, hspace=10, font_scale=1.0, background_RGB=(242, 66, 53), text_RGB=(255, 250, 250))
    pTime = 0
    while runCam:
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        success, img = cap.read()
        if flip:
            img = cv2.flip(img, 1)

        success, bbox = tracker.update(img)

        blank_image = np.zeros((vcH+200, vcW, 3), np.uint8)
        blank_image[0:100, 530:632] = logo
        blank_image[100:580, 0:640] = img

        connection(blank_image)

        if image_coordinates != [0, 0, 0, 0, ]:
            pt1, pt2 = (image_coordinates[0], image_coordinates[1]
                        ), (image_coordinates[2], image_coordinates[3])
            cv2.rectangle(blank_image, pt1, pt2, (255, 0, 255), 3, 1)

        blank_image, boxFlip = ps.putBText(blank_image, 'Flip', text_offset_x=20, text_offset_y=blank_image.shape[
                                           0]-35, vspace=10, hspace=10, font_scale=1.0, background_RGB=(90, 128, 242), text_RGB=(255, 250, 250))
        blank_image, boxSS = ps.putBText(blank_image, 'Stop' if runCam else 'Start', text_offset_x=blank_image.shape[
                                         1]-100, text_offset_y=blank_image.shape[0]-85, vspace=10, hspace=10, font_scale=1.0, background_RGB=(20, 210, 4), text_RGB=(255, 250, 250))
        blank_image, boxClose = ps.putBText(
            blank_image, 'Close', text_offset_x=blank_image.shape[1]-100, text_offset_y=blank_image.shape[0]-35, vspace=10, hspace=10, font_scale=1.0, background_RGB=(242, 66, 53), text_RGB=(255, 250, 250))

        if success:
            data = drawBox(blank_image, bbox)
            try:
                arduino.write(str.encode(data))
            except:
                arduino = None

        else:
            cv2.putText(blank_image, 'Status: Lost', (10, 40),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

        cv2.putText(blank_image, f'FPS: {int(fps)}', (10, 20),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
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
