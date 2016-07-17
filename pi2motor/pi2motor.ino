#include <Servo.h>
#include <SoftwareSerial.h>
// Servo/Motor control tool + GPS display
// Created by Lucas Malta on 19 July 2015 based on Dr. Monk GPS read
// 
// Control relies on passing along a sequence:
//   Usage1: $ENGINE,POS_SERVO_LFT,POS_SERVO_RHT,SPD_MOTOR_LFT,SPD_MOTOR_RHT\n
//   Usage2: $RESET\n (set all values to zero)
//
// Ranges:
//   Servo position: -100 to 100
//   Motor speed: 0 to 100
//   --Note: values outside range will be capped
//
// Ex. in Python: ser.write('$ENGINE,-70, 70, 20, 100\n')
//
// GPS is diplayed from Pin 11
//

#define MOTOR_L_PIN 10  // LEFT MOTOR control pin
#define MOTOR_R_PIN 9   // RIGHT MOTOR control pin
#define SERVO_L_PIN 6   // LEFT SERVO control pin
#define SERVO_R_PIN 5   // RIGHT SERVO control pin
#define MIN_MOTOR_SPD 700     // Minimum motor speed
#define MAX_MOTOR_SPD 2200    // Maximum motor speed
#define MIN_SERVO_POS 700     // Minimum servo angle
#define MAX_SERVO_POS 2200    // Maximum servo angle

Servo myservoL; // Left servo object
Servo myservoR; // Right servo object
Servo mymotorL; // Left motor object
Servo mymotorR; // Right motor object

const int sentenceSize = 80; // Max control sequence size
char sentence[sentenceSize]; // Control sentence
SoftwareSerial gpsSerial(11,10); // RX, TX (TX not used)

int valSerL = 10;
int valSerR = 10;
int valEngL = 10;
int valEngR = 10;
float latS = -1;
float longW = -1;

void setup()
{
  // Attach pins to motors -- servos should NOT be attached here
  mymotorR.attach(MOTOR_R_PIN); // attach pin to right motor
  mymotorL.attach(MOTOR_L_PIN); // attach pin to left motor
  
  Serial.begin(9600);
  gpsSerial.begin(9600);
  Serial.println("Ready"); 
}


void loop()
{
  static int i = 0;

  // Get USB serial data
  if (Serial.available())
  {
    //Serial.println("Available");
    // Read sentence until \n
    char ch = Serial.read();    
    if (ch != '\n' && i < sentenceSize)
    {
      sentence[i] = ch;
      i++;
    }
    
    else
    {
      sentence[i] = '\0';
      i = 0;      
      displayParams();
    }
  }
  
  else
  {
    //Serial.println("ERROR: USB Serial unavailable.");
  }

  // Get GPS data
  if (gpsSerial.available())
  {
    char ch = gpsSerial.read(); // Read NMEA sentence
    if (ch != '\n' && i < sentenceSize)
    {
      sentence[i] = ch;
      i++;
    }
   
    else
    {
      //Serial.println(sentence);
      sentence[i] = '\0';
      i = 0;
      displayParams();
    }
  }
  
  else
  {
   //Serial.println("GPS Serial not available. GPS disconnected?");
  }
  
}


void displayParams()
{
  
  char field[sentenceSize]; // fields are values between commmas
  getField(field, 0); // field 0 = sentence type

   // $RESET - Reset speed/position
  if (strcmp(field, "$RESET") == 0)
  {
    Serial.println("Reseting...");
    myservoR.attach(SERVO_R_PIN); // attach right servo
    myservoL.attach(SERVO_L_PIN); // attach left servo

    // Set servo to mid position
    myservoR.writeMicroseconds( map(0, -100, 100, MIN_SERVO_POS, MAX_SERVO_POS ) );
    myservoL.writeMicroseconds( map(0, -100, 100, MIN_SERVO_POS, MAX_SERVO_POS ) );

    // Set motors to zero speed
    mymotorR.writeMicroseconds( map(0, 0, 100, MIN_MOTOR_SPD, MAX_MOTOR_SPD ) );
    mymotorL.writeMicroseconds( map(0, 0, 100, MIN_MOTOR_SPD, MAX_MOTOR_SPD ) );
    
    delay(100);
    myservoR.detach();
    myservoL.detach();
  }


   // $ENGINE - Change motor/servo params
  else if (strcmp(field, "$ENGINE") == 0) 
  {
      // Connect to servos/motors
      myservoR.attach(SERVO_R_PIN); // attach right servo
      myservoL.attach(SERVO_L_PIN); // attach left servo
  
      //Leftservo position
      getField(field, 1);   
      valSerL = constrain( atoi(field), -100, 100 );
      myservoL.writeMicroseconds( map(valSerL, -100, 100, MIN_SERVO_POS, MAX_SERVO_POS ) );
      
      //Right servo position
      getField(field, 2); 
      valSerR = constrain( atoi(field), -100, 100 );
      myservoR.writeMicroseconds( map(valSerR, -100, 100, MIN_SERVO_POS, MAX_SERVO_POS ) );

      //Left motor position
      getField(field, 3);   
      valEngL = constrain( atoi(field), 0, 100 );
      mymotorL.writeMicroseconds( map(valEngL, 0, 100, MIN_MOTOR_SPD, MAX_MOTOR_SPD ) );

      //Right motor position
      getField(field, 4);   
      valEngR = constrain( atoi(field), 0, 100 );
      mymotorR.writeMicroseconds( map(valEngR, 0, 100, MIN_MOTOR_SPD, MAX_MOTOR_SPD ) );


      // Avoid noise on servos for trying to hold position
      // Motors should NOT be dettached though...
      delay(100); // wait for servo to get there
      myservoL.detach();
      myservoR.detach();
  }
  

   // $GPRMC - Recommended minimum specific GPS/Transit data
  else if (strcmp(field, "$GPRMC") == 0) 
  {
      //Lat
      getField(field, 3);  // current lat 
      latS = atof(field);
      //getField(field, 4); // N/S

      
      //Long
       getField(field, 5);  // current long
       longW = atof(field);
      //getField(field, 6);  // E/W
  }

      
  else
  {
    //Serial.print("ERROR: No command found.");
  }

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
  
  
}


// Parser function: get field info from within a sentence
void getField(char* buffer, int index)
{
  
  int sentencePos = 0;
  int fieldPos = 0;
  int commaCount = 0;
  while (sentencePos < sentenceSize)
  {
    if (sentence[sentencePos] == ',')
    {
      commaCount ++;
      sentencePos ++;
    }
    if (commaCount == index)
    {
      buffer[fieldPos] = sentence[sentencePos];
      fieldPos ++;
    }
    sentencePos ++;
  }

  buffer[fieldPos] = '\0';
} 
