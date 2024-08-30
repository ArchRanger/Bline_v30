import cv2
import time

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

    section_height = alan.shape[0] // 3  # Yükseklik
    section_width = alan.shape[1] // 3  # Genişlik
    matris = [0, 0, 0, 0, 0]

    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 60:
            cv2.drawContours(alan, [contour], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(contour)

            center_x = x + w // 2  # Sınırlayıcı kutunun merkezi
            center_y = y + h // 2

            section_indexH = center_y // section_height
            section_indexW = center_x // section_width

            
            matris[alan_no] = 1

            print(f"Koordinatlar: {center_x}, {center_y}")

            cv2.circle(alan, (center_x, center_y), 5, (0, 0, 255), -1)

    global matrisler

    matrisler[alan_no] = matris[alan_no]

    stop_time = time.time()
    print("Süre: ", stop_time - start_time)


while True:
    ret, photo = cap.read()
    if not ret:
        break

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

    cv2.imshow("AGV_1.", photo)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
