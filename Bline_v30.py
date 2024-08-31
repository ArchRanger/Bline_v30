import cv2
import time
import serial  # UART için seri kütüphanesi
import paho.mqtt.client as mqtt

# MQTT ayarları
broker_address = "broker.emqx.io"
port = 1883
topic = "rotayon"

client = mqtt.Client("AGV")
client.connect(broker_address, port)

# UART ayarları
uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)  # Raspberry Pi'de UART kullanımı

cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

matrisler = [0, 0, 0, 0, 0]
situations = [
    [0,0,0,0,0],[0,0,0,0,1],[0,0,0,1,0],[0,0,0,1,1],[0,0,1,0,0],[0,0,1,0,1],[0,0,1,1,0],[0,0,1,1,1],[0,1,0,0,0],[0,1,0,0,1],[0,1,0,1,0],[0,1,0,1,1],[0,1,1,0,0],[0,1,1,0,1],[0,1,1,1,0],[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,1],[1,0,0,1,0],[1,0,0,1,1],[1,0,1,0,0],[1,0,1,0,1],[1,0,1,1,0],[1,0,1,1,1],[1,1,0,0,0],[1,1,0,0,1],[1,1,0,1,0],[1,1,0,1,1],[1,1,1,0,0],[1,1,1,0,1],[1,1,1,1,0],[1,1,1,1,1]
]

def siyah(alan, alan_no):
    start_time = time.time()

    gray = cv2.cvtColor(alan, cv2.COLOR_BGR2GRAY)

    lower_black = 0
    upper_black = 30

    mask = cv2.inRange(gray, lower_black, upper_black)
    black_pixels = cv2.bitwise_and(alan, alan, mask=mask)

    gray = cv2.cvtColor(black_pixels, cv2.COLOR_BGR2GRAY)  # Yoğunluk
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)  # B&W

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # matris değişkenini fonksiyonun başında tanımla
    matris = [0, 0, 0, 0, 0]

    # Yalnızca en büyük konturu seç
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area > 60:  # Alanın belirli bir değerin üzerinde olmasını sağla
            cv2.drawContours(alan, [largest_contour], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(largest_contour)

            center_x = x + w // 2  # Sınırlayıcı kutunun merkezi
            center_y = y + h // 2

            section_height = alan.shape[0] // 3  # Yükseklik
            section_width = alan.shape[1] // 3  # Genişlik

            matris[alan_no] = 1

            print(f"Koordinatlar: {center_x}, {center_y}")

            cv2.circle(alan, (center_x, center_y), 5, (0, 0, 255), -1)

    global matrisler
    matrisler[alan_no] = matris[alan_no]

    stop_time = time.time()
    print("Süre: ", stop_time - start_time)


def durum_gonder(matris):
    durum = None
    if matris == [1,0,1,0,1]:
        durum = "düz"
    elif matris == [0,0,1,1,1]:
        durum = "sağ"
    elif matris == [0,1,1,0,1]:
        durum = "sol"
    elif matris == [0,1,1,1,1]:
        durum = "T"
    elif matris == [1,1,1,1,1]:
        durum = "dörtyol"
    elif matris == [0,1,1,1,0]:
        durum = "çiftyol"
    
    if durum:
        print(f"Durum: {durum}")
        client.publish(topic, durum)


def uart_veri_isle(veri):
    # Gelen veriyi kontrol et ve işle
    if veri in ['1', '2', '3', '4', '5']:
        # Diğer Arduino'ya gönder
        uart.write(veri.encode())
        print(f"Veri gönderildi: {veri}")
        
        # Aynı zamanda MQTT'ye de gönder
        client.publish(topic, f"Veri: {veri}")

while True:
    ret, photo = cap.read()
    if not ret:
        break

    # UART verisini oku
    if uart.in_waiting > 0:
        gelen_veri = uart.read().decode().strip()
        uart_veri_isle(gelen_veri)

    photo = cv2.flip(photo, 1)  # Mirror
    kernel_size = (5, 5)
    photo = cv2.GaussianBlur(photo, kernel_size, 0)

    cv2.rectangle(photo, (140, 50), (180, 100), (0, 255, 0), 2)  # Dikey dikdörtgen
    cv2.rectangle(photo, (100, 100), (140, 140), (0, 255, 0), 2)  # Yatay dikdörtgen
    cv2.rectangle(photo, (140, 100), (180, 140), (0, 255, 0), 2)  # Orta dikdörtgen
    cv2.rectangle(photo, (180, 100), (220, 140), (0, 255, 0), 2)  # Yatay dikdörtgen
    cv2.rectangle(photo, (140, 140), (180, 190), (0, 255, 0), 2)  # Dikey dikdörtgen

    alan0 = photo[50:100, 140:180]
    alan1 = photo[100:140, 100:140]
    alan2 = photo[100:140, 140:180]
    alan3 = photo[100:140, 180:220]
    alan4 = photo[140:190, 140:180]

    alanlist = [alan0, alan1, alan2, alan3, alan4]
    count = 0

    for alan in alanlist:
        siyah(alan, count)
        count = count + 1

    print(matrisler)
    durum_gonder(matrisler)

    cv2.imshow("AGV_1.", photo)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
