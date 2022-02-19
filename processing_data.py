#IMPORTING LIBRARY
import cv2

# MEMBERI TANDA BERUPA KOTAK WARNA PINK SEBAGAI OBEJEK TRACKING DAN MEMBERI NILAI POSISI TARGET
def drawBox(img, bbox, xx, yy):
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    wSet = w//2
    hSet = h//2
    xc = x+wSet
    yc = y+hSet
    cv2.rectangle(img, (x, y), ((x+w), (y+h)), (255, 0, 255), 3, 1)
    cv2.circle(img, (xc, yc), 5, (255, 0, 255), -1)
    
    cv2.line(img, (xx-wSet, yy),
             (xx+wSet, yy), (255, 255, 255), 2)

    cv2.line(img, (xx, yy-hSet),
             (xx, yy+hSet), (255, 255, 255), 2)
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

    cv2.putText(img, f'DATA: {num}', (10, 40),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    return num
