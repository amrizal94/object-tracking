#IMPORTING LIBRARY
import cv2
import numpy as np
import background_box as ps
from win32 import win32api
import win32.lib.win32con as win32con
import time
import serial
import serial.tools.list_ports
import base64
from logo_jpg_byte import byteform as logo # Memanggil bytes yang berupa gambar logo
from cameranotfound import byteform as camNotFound # Memanggil bytes yang berupa gambar camera not found, mencegah error jika camera lost connect

# SETTING RESOLUSI GAMBAR KAMERA
vcW = 640
vcH = 480

# INITIAL BEBERAPA LIBRARY GLOBAL
leftClickOnDown = False
image_coordinates = [0, 0, 0, 0]
arduinoPort = []
arduino = None
bbox = None

logo_jpeg = base64.b64decode(logo)
jpeg_as_np = np.frombuffer(logo_jpeg, dtype=np.uint8)
logo = cv2.imdecode(jpeg_as_np, flags=1)

camNotFound_jpeg = base64.b64decode(camNotFound)
jpeg_as_np = np.frombuffer(camNotFound_jpeg, dtype=np.uint8)
camNotFound = cv2.imdecode(jpeg_as_np, flags=1)

tracker = cv2.legacy.TrackerCSRT_create()

source = 0

cap = cv2.VideoCapture(source)

# TEST DEVICE CAMERA, UNTUK MENGETAHUI KAMERA YANG TERKONEKSI DAN BISA DIGUNAKAN
def testDevice(source):
    cap = cv2.VideoCapture(source)
    success, img = cap.read()
    return type(img).__module__ == np.__name__


# MEMBERI TANDA BERUPA KOTAK WARNA PINK SEBAGAI OBEJEK TRACKING DAN MEMBERI NILAI POSISI TARGET
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
        num = "H" # JIKA POSISI ON TARGET
    else:
        # JIKA POSISI TARGET ADA DI ATAS / DIBAWAH
        if yc < yy - jari2:
            num += "A" # TARGET ADA DIATAS (NAIK)
        elif yc > yy + jari2:
            num += "B" # TARGET ADA DIBAWAH (TURUN)
            
        # JIKA POSISI TARGET ADA DI KANAN / KIRI
        if xc < xx - jari2:
            num += "C" # TARGET ADA DISEBALAH KANAN 

        elif xc > xx + jari2:
            num += "D" # TARGET ADA DISEBALAH KIRI 

    # drawInfo(img, "DATA", 3, num, True)
    cv2.putText(img, f'DATA: {num}', (10, 40),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    return num

# MEMBUAT FUNGSI KETIKA MOUSE MENGEKLIK GAMBAR TOMBOL START, STOP DAN CLOSE DALAM POSISI KAMERA SUDAH MENGAMBIL GAMBAR
def mouse_evt(event, x, y, flags, param):
    global runCam, runApp, flip, image_coordinates, leftClickOnDown, arduino, bbox, source, cap, tracker
    
    if runCam:
        # FUNGSI TOMBOL MEMBALIK GAMBAR KAMERA
        if boxFlip[0] < x and x < boxFlip[2] and boxFlip[1] < y and y < boxFlip[3]:
            win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
            if event == cv2.EVENT_LBUTTONDOWN:
                flip = not flip
                
        # FUNGSI MENGGANTI KAMERA DEVICE YANG TERHUBUNG
        elif boxCC[0] < x and x < boxCC[2] and boxCC[1] < y and y < boxCC[3]:
            win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
            if event == cv2.EVENT_LBUTTONDOWN:
                source += 1
                while testDevice(source) is False:
                    source += 1
                    if source == 10:
                        source = 0
                cap = cv2.VideoCapture(source)
    
    # FUNGSI TOMBOL START DAN STOP
    if boxSS[0] < x and x < boxSS[2] and boxSS[1] < y and y < boxSS[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runCam = not runCam
    # FUNGSI CLOSE
    elif boxClose[0] < x and x < boxClose[2] and boxClose[1] < y and y < boxClose[3]:
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
        if event == cv2.EVENT_LBUTTONDOWN:
            runCam = not runCam if runCam else runCam
            runApp = not runApp
            
    # FUNGSI MERESET TARGET OBJEK
    elif 0 < x and x < 640 and 100 < y and y < 580:
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            if bbox != (0.0, 0.0, 0.0, 0.0):
                runCam = not runCam
            if runCam == False:
                tracker = cv2.legacy.TrackerCSRT_create()
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
            
    # FUNGSI MENAMPILKAN TOMBOL KONEK KE ARDUINO JIKA TERDAPAT DEVIDE TERHUBUNG
    if len(arduinoPort) != 0:
        if boxConnection[0] < x and x < boxConnection[2] and boxConnection[1] < y and y < boxConnection[3]:
            win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))
            if event == cv2.EVENT_LBUTTONDOWN:
                if arduino:
                    arduino.close()
                    arduino = None
                else:
                    arduino = serial.Serial(arduinoPort[0], baudrate=9600)

# MENAMPILKAN PORT ARDUINO YANG TERSEDIA DAN TERKONEKSI
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
                                         text_offset_y=blank_image.shape[0]-35, vspace=10, hspace=10, font_scale=1.0, background_RGB=(252, 3, 211), text_RGB=(255, 250, 250))


runApp = True
runCam = False
flip = False

# LOOP APLIKASI
while runApp:
    blank_image = np.zeros((vcH+200, vcW, 3), np.uint8) # MENAMBAHKAN BACKGROUND HITAM DIATAS DAN DIBAWAH GAMBAR KAMERA
    blank_image[0:100, 530:632] = logo # MELETAKKAN POSISI LOGO

    connection(blank_image)
    # MENAMPILKAN GAMBAR TOMBOL START DAN TOMBOL STOP
    blank_image, boxSS = ps.putBText(blank_image, 'Stop' if runCam else 'Start', text_offset_x=blank_image.shape[
                                     1]-100, text_offset_y=blank_image.shape[0]-85, vspace=10, hspace=10, font_scale=1.0, background_RGB=(20, 210, 4), text_RGB=(255, 250, 250))
    
    # MENAMPILKAN GAMBAR TOMBOL CLOSE
    blank_image, boxClose = ps.putBText(
        blank_image, 'Close', text_offset_x=blank_image.shape[1]-100, text_offset_y=blank_image.shape[0]-35, vspace=10, hspace=10, font_scale=1.0, background_RGB=(242, 66, 53), text_RGB=(255, 250, 250))
    pTime = 0
    
    # LOOP PENGAMBILAN GAMBAR KAMERA
    while runCam:
        # FUNGSI FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        success, img = cap.read()
        
        # FUNGSI MEMBALIKKAN GAMBAR
        if flip:
            img = cv2.flip(img, 1)

        success, bbox = tracker.update(img)

        blank_image = np.zeros((vcH+200, vcW, 3), np.uint8) # GAMBAR BACKGROUND HITAM
        blank_image[0:100, 530:632] = logo # MELETAKKAN GAMBAR LOGO PADA BACKGROUND HITAM
        
        # MENGATASI JIKA KAMERA TERPUTUS
        try:
            blank_image[100:580, 0:640] = img # MELETAKKAN GAMBAR KAMERA
        except:
            blank_image[100:580, 0:640] = camNotFound # MELETAKKAN GAMBAR KAMERA NOT FOUND

        connection(blank_image)

        # MEMBERI TANDA KOTAK PINK JIKA MASIH MENTRACKING
        if image_coordinates != [0, 0, 0, 0, ]:
            pt1, pt2 = (image_coordinates[0], image_coordinates[1]
                        ), (image_coordinates[2], image_coordinates[3])
            cv2.rectangle(blank_image, pt1, pt2, (255, 0, 255), 3, 1)

        # MENAMPILKAN GAMBAR TOMBOL FILP 
        blank_image, boxFlip = ps.putBText(blank_image, 'Flip', text_offset_x=320, text_offset_y=blank_image.shape[
                                           0]-85, vspace=10, hspace=10, font_scale=1.0, background_RGB=(90, 128, 242), text_RGB=(255, 250, 250))
        
        # MENAMPILKAN GAMBAR TOMBOL CHANGE CAMERA
        blank_image, boxCC = ps.putBText(blank_image, 'Change Camera', text_offset_x=20, text_offset_y=blank_image.shape[
                                         0]-85, vspace=10, hspace=10, font_scale=1.0, background_RGB=(20, 10, 204), text_RGB=(255, 250, 250))
        
        # MENAMPILKAN GAMBAR TOMBOL STOP DAN START
        blank_image, boxSS = ps.putBText(blank_image, 'Stop' if runCam else 'Start', text_offset_x=blank_image.shape[
                                         1]-100, text_offset_y=blank_image.shape[0]-85, vspace=10, hspace=10, font_scale=1.0, background_RGB=(20, 210, 4), text_RGB=(255, 250, 250))
        
        # MENAMPILKAN GAMBAR TOMBOL CLOSE
        blank_image, boxClose = ps.putBText(
            blank_image, 'Close', text_offset_x=blank_image.shape[1]-100, text_offset_y=blank_image.shape[0]-35, vspace=10, hspace=10, font_scale=1.0, background_RGB=(242, 66, 53), text_RGB=(255, 250, 250))

        
        if success:
            data = drawBox(blank_image, bbox)
            
            # MENCEGAH ERROR KETIKA ARDUINO DISCONNECT
            try:
                arduino.write(str.encode(data)) # MENGIRIM DATA 
            except:
                arduino = None

        else:
            # MENAMPILKAN GAMBAR TULISAN STATUS
            cv2.putText(blank_image, 'Status: Lost', (10, 40),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

        # MENAMPILKAN GAMBAR TULISAN FPS
        cv2.putText(blank_image, f'FPS: {int(fps)}', (10, 20),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        
        # MENAMPILKAN GAMBAR TULISAN COM CAMERA
        cv2.putText(blank_image, f'COM CAMERA: {source}', (10, 80),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.imshow("Object Tracking", blank_image)
        cv2.setMouseCallback("Object Tracking", mouse_evt)
        
        # FUNGSI SHORTCUT TOMBOL KEYBOARD
        k = cv2.waitKey(1)
        # TEKAN 'Q' untuk LOOP KAMERA ATAU TIDAK
        if k == ord("q"): 
            runCam = not runCam
            break
        # TEKAN 'F' untuk MEMBALIKKAN GAMBAR
        elif k == ord("f"):
            flip = not flip
        pTime = cTime
    cv2.imshow("Object Tracking", blank_image)
    cv2.setMouseCallback("Object Tracking", mouse_evt)
    k = cv2.waitKey(1)
    # TEKAN 'Q' untuk CLOSE APP
    if k == ord("q"):
        runApp = not runApp
        break
