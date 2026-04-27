struct LEFTMOTORS {
  //front left motors
  int directionPins[4] = { 2, 3, 4, 5 };  // inputs 1 - 4 of left side of both l293d
  int enablePin = 6;                      // enable pin of left motors
};

struct RIGHTMOTORS {
  //front right motors
  int directionPins[4] = { A0, A1, A2, A3 };  // inputs 1 - 4 of right side of both l293d
  int enablePin = 9;                          // enable pin of right motors
};

// object created from both structures
LEFTMOTORS leftDrive;
RIGHTMOTORS rightDrive;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);  //initializing serial comm

  // looping through all the left motors pins and setting them as OUTPUT
  for (int pin = 0; pin < sizeof(leftDrive.directionPins) / sizeof(leftDrive.directionPins[0]); pin++) {
    pinMode(leftDrive.directionPins[pin], OUTPUT);
  }

  // looping through all the right motors pins and setting them as OUTPUT
  for (int pin = 0; pin < sizeof(rightDrive.directionPins) / sizeof(rightDrive.directionPins[0]); pin++) {
    pinMode(rightDrive.directionPins[pin], OUTPUT);
  }

  // setting the enable pins as OUTPUT
  pinMode(leftDrive.enablePin, OUTPUT);
  pinMode(rightDrive.enablePin, OUTPUT);

  stopRobot();  // deactivating the motors
}

void loop() {
  // put your main code here, to run repeatedly:
}

void stopRobot() {
  analogWrite(leftDrive.enablePin, 0);
  analogWrite(rightDrive.enablePin, 0);
}

void moveForward() {
  analogWrite(leftDrive.enablePin, 255);
  analogWrite(rightDrive.enablePin, 255);
}
