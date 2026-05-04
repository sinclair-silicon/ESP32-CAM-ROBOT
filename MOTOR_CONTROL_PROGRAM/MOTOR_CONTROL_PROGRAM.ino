struct LEFTMOTORS {
  int directionPins[4] = { 2, 3, 4, 5 };
  int enablePin = 6;
};

struct RIGHTMOTORS {
  int directionPins[4] = { A0, A1, A2, A3 };
  int enablePin = 9;
};

LEFTMOTORS leftDrive;
RIGHTMOTORS rightDrive;

// New global variable to hold incoming serial data
String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(115200);

  for (int pin = 0; pin < 4; pin++) {
    pinMode(leftDrive.directionPins[pin], OUTPUT);
    pinMode(rightDrive.directionPins[pin], OUTPUT);
  }

  pinMode(leftDrive.enablePin, OUTPUT);
  pinMode(rightDrive.enablePin, OUTPUT);

  // Reserve 50 bytes for the input string to prevent memory fragmentation
  inputString.reserve(50);

  stopRobot();
}

void loop() {
  // 1. Check if we received a complete command string
  if (stringComplete) {

    // 2. Parse the string (Expected format: "R:200" or "F:150")
    int colonIndex = inputString.indexOf(':');

    if (colonIndex != -1) {
      // Extract the direction character ('R', 'L', 'F')
      String directionStr = inputString.substring(0, colonIndex);
      // Extract the speed number and convert it to an integer
      int speed = inputString.substring(colonIndex + 1).toInt();

      // Ensure speed is within safe bounds
      speed = constrain(speed, 0, 255);

      // 3. Execute the command
      if (directionStr == "F") {
        moveForward(speed);
      } else if (directionStr == "L") {
        turnLeft(speed);
      } else if (directionStr == "R") {
        turnRight(speed);
      }
    }

    // 4. Clear the string for the next command
    inputString = "";
    stringComplete = false;
  }
}

// Built-in Arduino function that automatically grabs incoming serial characters
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    // If the incoming character is a newline, set a flag so the main loop can process it
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

// --- MOVEMENT FUNCTIONS ---

void stopRobot() {
  analogWrite(leftDrive.enablePin, 0);
  analogWrite(rightDrive.enablePin, 0);
}

void moveForward(int speed) {
  analogWrite(leftDrive.enablePin, speed);
  analogWrite(rightDrive.enablePin, speed);

  for (int i = 0; i < 4; i += 2) {
    digitalWrite(leftDrive.directionPins[i], HIGH);
    digitalWrite(leftDrive.directionPins[i + 1], LOW);
    digitalWrite(rightDrive.directionPins[i], LOW);
    digitalWrite(rightDrive.directionPins[i + 1], HIGH);
  }
}

void turnLeft(int speed) {
  // Skid steer: Left side backwards, Right side forwards
  analogWrite(leftDrive.enablePin, speed);
  analogWrite(rightDrive.enablePin, speed);

  for (int i = 0; i < 4; i += 2) {
    digitalWrite(leftDrive.directionPins[i], LOW);
    digitalWrite(leftDrive.directionPins[i + 1], HIGH);

    digitalWrite(rightDrive.directionPins[i], LOW);
    digitalWrite(rightDrive.directionPins[i + 1], HIGH);
  }
}

void turnRight(int speed) {
  // Skid steer: Left side forwards, Right side backwards
  analogWrite(leftDrive.enablePin, speed);
  analogWrite(rightDrive.enablePin, speed);

  for (int i = 0; i < 4; i += 2) {
    digitalWrite(leftDrive.directionPins[i], HIGH);
    digitalWrite(leftDrive.directionPins[i + 1], LOW);

    digitalWrite(rightDrive.directionPins[i], HIGH);
    digitalWrite(rightDrive.directionPins[i + 1], LOW);
  }
}
