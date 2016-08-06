#include <Servo.h>
#include <SoftwareSerial.h>
#include <TinyGPS.h>
#include <aJSON.h>

#define MOTOR_L_PIN 10  // LEFT MOTOR control pin
#define MOTOR_R_PIN 9   // RIGHT MOTOR control pin
#define SERVO_L_PIN 6   // LEFT SERVO control pin
#define SERVO_R_PIN 5   // RIGHT SERVO control pin
#define GPS_RX_PIN  11  // GPS RX pin
#define GPS_TX_PIN  3   // GPS TX pin
#define MIN_MOTOR_SPD 700     // Minimum motor speed
#define MAX_MOTOR_SPD 2200    // Maximum motor speed
#define MIN_SERVO_POS 700     // Minimum servo angle
#define MAX_SERVO_POS 2200    // Maximum servo angle

Servo myservoL; // Left servo object
Servo myservoR; // Right servo object
Servo mymotorL; // Left motor object
Servo mymotorR; // Right motor object

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
const int sentenceSize = 200; // Max control sequence size


SoftwareSerial gpsSerial(GPS_RX_PIN,GPS_TX_PIN); // RX, TX (TX not used)
TinyGPS gps; // create gps object

int valSerL = 10;
int valSerR = 10;
int valEngL = 10;
int valEngR = 10;
long latS = -1;
long longW = -1;



void setup() {
  // Attach pins to motors -- servos should NOT be attached here
  mymotorR.attach(MOTOR_R_PIN); // attach pin to right motor
  mymotorL.attach(MOTOR_L_PIN); // attach pin to left motor
   
  // initialize serial:
  Serial.begin(9600);
  gpsSerial.begin(9600);
 
  // reserve sentenceSize bytes for the inputString:
  inputString.reserve(sentenceSize);
}


void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
    Serial.println(inputString);
    displayParams();
    
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
  
  
  if(gpsSerial.available()){ // check for gps data
    if(gps.encode(gpsSerial.read())){ // encode gps data
        gps.get_position(&latS,&longW); // get latitude and longitude
    }
  }
}


void displayParams()
{
  
  char* value;
  char jsonString[sentenceSize];
  inputString.toCharArray(jsonString,sentenceSize);
    
  aJsonObject* root = aJson.parse(jsonString);
  aJsonObject* MR = aJson.getObjectItem(root, "MR");  
  aJsonObject* ML = aJson.getObjectItem(root, "ML");
  aJsonObject* SR = aJson.getObjectItem(root, "SR"); 
  aJsonObject* SL = aJson.getObjectItem(root, "SL"); 
 
  // Connect to servos/motors
  myservoR.attach(SERVO_R_PIN); // attach right servo
  myservoL.attach(SERVO_L_PIN); // attach left servo
  
  //Leftservo position   
      valSerL = constrain( atoi(SL->valuestring), -100, 100 );
      myservoL.writeMicroseconds( map(valSerL, -100, 100, MIN_SERVO_POS, MAX_SERVO_POS ) );
      
      //Right servo position
      valSerR = constrain( atoi(SR->valuestring), -100, 100 );
      myservoR.writeMicroseconds( map(valSerR, -100, 100, MIN_SERVO_POS, MAX_SERVO_POS ) );

      //Left motor position
      valEngL = constrain( atoi(ML->valuestring), 0, 100 );
      mymotorL.writeMicroseconds( map(valEngL, 0, 100, MIN_MOTOR_SPD, MAX_MOTOR_SPD ) );

      //Right motor position
      valEngR = constrain( atoi(MR->valuestring), 0, 100 );
      mymotorR.writeMicroseconds( map(valEngR, 0, 100, MIN_MOTOR_SPD, MAX_MOTOR_SPD ) );


      // Avoid noise on servos for trying to hold position
      // Motors should NOT be dettached though...
      delay(100); // wait for servo to get there
      myservoL.detach();
      myservoR.detach();
 
  Serial.print(" Lat: ");
  Serial.print(latS);
  Serial.print(" Long: ");
  Serial.print(longW);
  Serial.print(" RServo: ");
  Serial.print(valSerR);
  Serial.print(" LServo: ");
  Serial.print(valSerL);
  Serial.print(" RMotor: ");
  Serial.print(valEngR);
  Serial.print(" LMotor: ");
  Serial.print(valEngL);
  Serial.print("\n");
  
  Serial.flush(); // Wait till outgoing tx is done
  
  
}




/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
