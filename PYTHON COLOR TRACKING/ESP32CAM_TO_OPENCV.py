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
dead_zone = 40
pan_angle = 40.0  # Start looking straight ahead
Kp_pan = 1.2     # Proportional Gain

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
            
            # 1. Calculate Error (Frame is 480 wide, so center is 240)
            error_x = center_x - 240
            
            # 3. The Proportional Logic
            if abs(error_x) <= dead_zone:
                # Ball is centered. Drive straight.
                command = "F:150"  # We will format this so Arduino can read it
                print(f"Target Locked. Driving Forward. (Error: {error_x})")
                
            else:
                # Ball is outside dead zone. Calculate turn speed.
                # Use abs() because we only want a positive speed value (0 to 255)
                adjustment_speed = int(abs(error_x) * Kp_pan)
                
                # Clamp speed between 80 (to overcome motor friction) and 255 (max speed)
                pwm_val = max(80, min(255, adjustment_speed))
                
                if error_x > 0:
                    # Ball is on the right, so we need to turn Right
                    command = f"L:{pwm_val}"
                    print(f"Tracking Left. PWM: {pwm_val} (Error: {error_x})")
                else:
                    # Ball is on the left, so we need to turn Left
                    command = f"R:{pwm_val}"
                    print(f"Tracking Right. PWM: {pwm_val} (Error: {error_x})")
            
            # 4. Send the command to Arduino (assuming you have a serial object named 'ser')
            
            # --- Serial Transmission to Arduino ---
            if ser is not None:
                data_string = f"{command}\n"
                ser.write(data_string.encode('utf-8'))
            
            # Draw visuals
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Cmd: {command}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            # print(frame.shape)

    # Show results
    cv2.imshow("Red Ball Tracking", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('p'):
        print("Color Tracking Ended")
        break

cap.release()
if ser is not None:
    ser.close()
cv2.destroyAllWindows()