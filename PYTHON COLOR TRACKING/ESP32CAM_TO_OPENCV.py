import cv2
import numpy as np
import serial
import time

# Initialize webcam
url = "http://192.168.43.66:81/stream"
cap = cv2.VideoCapture(url)

# Initialize Serial to Arduino (COM5)
try:
    ser = serial.Serial('COM5', 115200, timeout=1)
    time.sleep(2) # Give Arduino 2 seconds to reboot after connection
    print("Serial connection established.")
except serial.SerialException:
    print("Warning: Could not open COM5. Check connection.")
    ser = None

# --- NEW: Servo Tracking Variables ---
pan_angle = 90.0  # Start looking straight ahead
Kp_pan = 0.05     # Proportional Gain

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't find camera.")
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (480, 320))
    
    # 1. Preprocess: Blur and convert to HSV
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 2. Define Red Color Ranges 
    lower_red1 = np.array([0, 80, 30])
    upper_red1 = np.array([10, 255, 255])
    
    lower_red2 = np.array([170, 80, 50])
    upper_red2 = np.array([180, 255, 255])

    # 3. Create and clean mask
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # 4. Find contours 
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # ONLY track the single largest contour
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(c) > 1500: # Filter small noise
            x, y, w, h = cv2.boundingRect(c)
            center_x = x + (w // 2)
            
            # --- Proportional Controller Math ---
            error_x = center_x - 240
            adjustment = error_x * Kp_pan
            pan_angle = pan_angle - adjustment
            
            # Clamp the angle to protect the physical servo (0 to 180 degrees)
            pan_angle = max(0, min(180, pan_angle))
            
            # --- Serial Transmission to Arduino ---
            if ser is not None:
                data_string = f"{int(pan_angle)}\n"
                ser.write(data_string.encode('utf-8'))
            
            # Draw visuals
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Angle: {int(pan_angle)}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show results
    cv2.imshow("Red Ball Tracking", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('p'):
        print("Color Tracking Ended")
        break

cap.release()
if ser is not None:
    ser.close()
cv2.destroyAllWindows()