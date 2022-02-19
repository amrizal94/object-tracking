import random
from tkinter import Tk, ttk, messagebox, Label, Entry, Button, DoubleVar
import cv2
import numpy as np
import base64
import time
import serial
import serial.tools.list_ports
from processing_data import drawBox
from logo_jpg_byte import byteform as logo # Memanggil bytes yang berupa gambar logo
from cameranotfound import byteform as camNotFound # Memanggil bytes yang berupa gambar camera not found, mencegah error jika camera lost connect
root = Tk()
root.title('Object tracking')
root.minsize(260, 100)
note_book = ttk.Notebook(root)
tabWifi = ttk.Frame(note_book)
tabUsb = ttk.Frame(note_book)
note_book.add(tabWifi, text = "WiFi")
note_book.add(tabUsb, text = "USB")
note_book.grid(row=0, column=0, columnspan = 3)
    
Label(tabWifi, text="Connect over WiFi (LAN)").grid(row=1, columnspan = 3, pady=10)
Label(tabWifi, text="Device IP", width=10, anchor='w').grid(row=2)
Label(tabWifi, text="Device Port", width=10, anchor='w').grid(row=3)

# Using readlines()
try:
  file1 = open('settings.txt', 'r')
  Lines = file1.readlines()
except OSError:
  open('settings.txt', 'w')

if len(Lines)-1 >= 2:
  if Lines[0] != '':
    v = DoubleVar()
    eW1 = Entry(tabWifi, textvariable=v)
    v.set(str(Lines[0]).strip())
  else:
    eW1 = Entry(tabWifi)
else:
  eW1 = Entry(tabWifi)
if len(Lines)-1 >= 2:
  if Lines[1] != '':
    v = DoubleVar()
    eW2 = Entry(tabWifi, textvariable=v)
    v.set(str(Lines[1]).strip())
  else:
    eW2 = Entry(tabWifi)
else:
  eW2 = Entry(tabWifi)
eW1.grid(row=2, column=1, columnspan = 2)
eW2.grid(row=3, column=1, columnspan = 2)

Label(tabUsb, text="Connect over USB").grid(row=1, columnspan = 3, pady=10)
Label(tabUsb, text="Source (0...n)", width=10, anchor='w').grid(row=2)
if len(Lines)-1 >= 2:
  if Lines[2] !='':
    v = DoubleVar()
    eU1 = Entry(tabUsb, textvariable=v)
    v.set(int(str(Lines[2]).strip()))
  else:
    eU1 = Entry(tabUsb)
else:
  eU1 = Entry(tabUsb)
eU1.grid(row=2, column=1, columnspan = 2)    

def mouse_evt(event, x, y, flags, param):
  global leftClickOnDown, bbox, image_coordinates, tracker, runCam, arduino
  # FUNGSI MERESET TARGET OBJEK
  if 0 < x and x < 640 and 100 < y and y < 580:
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
    cv2.putText(img, 'COM: Not Available', (10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
  else:
    if arduino:
        cv2.putText(img, f"COM: Connect To {arduinoPort[0]}", (
            10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    else:
        listToStr = 'and'.join([str(elem) for elem in arduinoPort])
        cv2.putText(img, f"COM: {listToStr} {'is available' if len(arduinoPort) < 2 else 'are availables'} ", (
            10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

def cam_flip():
  global flip
  flip = not flip
    
def cam_run():
  global source, runCam
  if bSS['text'] == 'Start':
    if note_book.select()=='.!notebook.!frame':
      if (eW1.get() =='' or eW2.get() ==''):
        messagebox.showerror("No Cam", "Please input ip and port")
        return
      source = f'http://{eW1.get()}:{eW2.get()}/video'
    elif note_book.select()=='.!notebook.!frame2':
      if eU1.get() =='':
        messagebox.showerror("No Cam", "Please input source com camera 0 ... n")
        return
      if not str.isdigit(eU1.get()):
        messagebox.showwarning("showwarning", "Source must be number")
        return
      source = int(eU1.get())
    runCam = True
    bSS['text'] = 'Stop'
    bSS['bg'] = 'red'
    bSS['fg'] = 'white'
    eW1['state']="disabled"
    eW2['state']="disabled"
    eU1['state']="disabled"
    with open('settings.txt', 'w') as f:
      line1 = ' ' if eW1.get() =='' else eW1.get()
      f.write(f'{line1}\n')
      line2 = ' ' if eW2.get() =='' else eW2.get()
      f.write(f'{line2}\n')
      line3 = ' ' if eU1.get() =='' else eU1.get()
      f.write(f'{line3}')
      f.close()
        
  else:
    bSS['text'] = 'Start'
    bSS['bg'] = bgBSS
    bSS['fg'] = 'black'
    eW1['state']="normal"
    eW2['state']="normal"
    eU1['state']="normal"
    runCam = False
  
def app_run():
  global runApp, runCam
  result = messagebox.askquestion("Quit", "Are You Sure?", icon='warning')
  if result == 'yes':
      runCam = not runCam if runCam else runCam
      runApp = not runApp
  
  
class MyButton(Button):
  def __init__(self, *args, **kwargs):
    Button.__init__(self, *args, **kwargs)
    # keep a record of the original background colour
    self._bg = self['bg']
    self['width']=5
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    self['activebackground'] = random.choice(colors)
    
# Button Flip
bF = MyButton(root, text='Flip', command = cam_flip)
bF.grid(row=4,column=0,pady=4)

# Button Start and Stop
bgBSS = '#72db99'
bSS = MyButton(root, text='Start', command=cam_run, bg=bgBSS)
bSS.grid(row=4,column=1, pady=4)

# Button Quit
bQ = MyButton(root, text='Quit', command=app_run)
bQ.grid(row=4,column=2,pady=4)

# SETTING RESOLUSI GAMBAR KAMERA
vcW = 640
vcH = 480

# INITIAL BEBERAPA VARIABLE GLOBAL
leftClickOnDown = False
image_coordinates = [0, 0, 0, 0]
arduinoPort = []
arduino = None
bbox = None

# VARIABLE PROCESSING
xx = vcW//2
yy = (vcH+200)//2
# Logo
logo_jpeg = base64.b64decode(logo)
jpeg_as_np = np.frombuffer(logo_jpeg, dtype=np.uint8)
logo = cv2.imdecode(jpeg_as_np, flags=1)

# camNotFound
camNotFound_jpeg = base64.b64decode(camNotFound)
jpeg_as_np = np.frombuffer(camNotFound_jpeg, dtype=np.uint8)
camNotFound = cv2.imdecode(jpeg_as_np, flags=1)

runApp = True
runCam = False
flip = False
pTime = 0
tracker = cv2.legacy.TrackerCSRT_create()
while runApp:
  blank_image = np.zeros((vcH+200, vcW, 3), np.uint8) # MENAMBAHKAN BACKGROUND HITAM DIATAS DAN DIBAWAH GAMBAR KAMERA
  blank_image[0:100, 530:632] = logo # MELETAKKAN POSISI LOGO
  cv2.imshow("Object Tracking", blank_image)
  root.update()
  
  if runCam:
    cap = cv2.VideoCapture(source)
  while runCam:
    # FUNGSI FPS
    cTime = time.time()
    try:
      fps = 1 / (cTime - pTime)
    except ZeroDivisionError:
      fps = 0
    
    success, img = cap.read()
    
    # FUNGSI MEMBALIKKAN GAMBAR
    if flip:
      img = cv2.flip(img, 1)
      
    success, bbox = tracker.update(img)
      
    # MENAMPILAKAN GAMBAR CAM
    blank_image = np.zeros((vcH+200, vcW, 3), np.uint8) # GAMBAR BACKGROUND HITAM
    blank_image[0:100, 530:632] = logo # MELETAKKAN GAMBAR LOGO PADA BACKGROUND HITAM
    
    # MENGATASI JIKA KAMERA TERPUTUS
    try:
        blank_image[100:580, 0:640] = img # MELETAKKAN GAMBAR KAMERA
    except:
        blank_image[100:580, 0:640] = camNotFound # MELETAKKAN GAMBAR KAMERA NOT FOUND
        
    connection(blank_image)
    
    # MENKALIBRASI DENGAN MENAMPILKAN KOTAK NO FIIL REALTIME
    if image_coordinates != [0, 0, 0, 0, ]:
        pt1, pt2 = (image_coordinates[0], image_coordinates[1]
                    ), (image_coordinates[2], image_coordinates[3])
        cv2.rectangle(blank_image, pt1, pt2, (255, 0, 255), 3, 1)
        
    if success:
      data = drawBox(blank_image, bbox, xx, yy)
      
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
    pTime = cTime
    root.update()