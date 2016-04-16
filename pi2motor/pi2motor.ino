#include <Servo.h>
// Serial communication protocol
// Created by Lucas Malta on 19 July 2015 based on Dr. Monk GPS read
// Sentence: $ENGINE,POS_SERVO_E,POS_SERVO_D,SPD_MOTOR_E,SPD_MOTOR_D\n
// Sentence: $RESET\n
//
// Ex. in python: ser.write('$ENGINE,2000,1000,2000,2000\n')

#define MOTOR1_PIN 10  // MOTOR1 control pin
#define MOTOR2_PIN 9 // MOTOR2 control pin
#define MIN_SPD 700  // Minimum motor speed
#define MAX_SPD 2200  // Maximum mototr speed

Servo myservo1; // servo1 object
Servo myservo2; // servo2 object
const int sentenceSize = 80;
char sentence[sentenceSize]; // control sentence


void setup()
{
  // Attach pins to motors -- servos should NOT be attached here
  //myservo1.attach(MOTOR1_PIN); // attach pin to servo1
  //myservo2.attach(MOTOR2_PIN); // attach pin to motor1
  Serial.begin(9600);
  Serial.println("Ready"); 
}


void loop()
{
  static int i = 0;
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
    //Serial.println("Serial disconnected?");
  }
}


void displayParams()
{
  
  char field[sentenceSize];
  getField(field, 0); // Field 0 = sentence type

   // $RESET - Reset speed/position
  if (strcmp(field, "$RESET") == 0)
  {
    Serial.println("Reseting...");
    myservo1.attach(MOTOR1_PIN); // attach pin to servo1
    myservo1.writeMicroseconds(MIN_SPD);
    myservo2.writeMicroseconds(MIN_SPD);
    delay(150);
    myservo1.detach();
    //myservo2.detach();
  }


   // $ENGINE - Change motor/servo params
  else if (strcmp(field, "$ENGINE") == 0) 
  {
      // Connect to servos/motors
      myservo1.attach(MOTOR1_PIN); // attach pin to servo1
      myservo2.attach(MOTOR2_PIN); // attach pin to servo2
  
      Serial.print("Left servo position: ");
      getField(field, 1);   
      int valEng1 = constrain( atoi(field), -100, 100 );
      Serial.println( valEng1 );
      myservo1.writeMicroseconds( map(valEng1, -100, 100, MIN_SPD, MAX_SPD ) );
      delay(150); // wait for servo to get there

      
      Serial.print("Right servo position: ");
      getField(field, 2); 
      int valEng2 = constrain( atoi(field), -100, 100 );
      Serial.println( valEng2 );
      myservo2.writeMicroseconds( map(valEng2, -100, 100, MIN_SPD, MAX_SPD ) );
      delay(150); // wait for servo to get there

      // Avoid noise on servos for trying to hold position
      // Motors should NOT be dettached though...
      myservo1.detach();
      myservo2.detach();
    /*

      Serial.print("Pos servo1: ");
      getField(field, 3);  
      Serial.println(field);

      Serial.print("Pos servo2: ");
      getField(field, 4);  
      Serial.println(field);
      */
  }
      
  else
  {
    //  Do nothing.  
  }
  
  
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
