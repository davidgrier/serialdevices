
/*
 * Sketch to control stepper motors via serial interface
 *
 * Commands implemented with examples:
 * - V:500 : Set motor speed to 500 steps/second
 * - G:-1000:50 : Move motor 1 to position -1000 and motor 2 to 50
 * - S : Stop (release) motors
 * - Q : Query software ID
 * - P : Query position of motors
 * - R : Query whether motors are running
 */

#include <stdio.h>
/* Adafruit Motor Shield v. 2.3 */
#include <AccelStepper.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
#include <MultiStepper.h>

Adafruit_MotorShield AFMS(0x60);
Adafruit_StepperMotor *motor1 = AFMS.getStepper(200, 1);
Adafruit_StepperMotor *motor2 = AFMS.getStepper(200, 2);

/* String I/O */
const int bufsize = 32;
char cmd[bufsize];    // command string
int len = 0;

/* flags */
boolean command_ready = false; // command string received
boolean is_running = false;    // true if steppers are running

/* motor positions (steps) */
long n1 = 0;
long n2 = 0;

/* Motor configuration */
void forwardstep1() {
  motor1->onestep(FORWARD, DOUBLE);
}

void backwardstep1() {
  motor1->onestep(BACKWARD, DOUBLE);
}

void forwardstep2() {
  motor2->onestep(FORWARD, DOUBLE);
}

void backwardstep2() {
  motor2->onestep(BACKWARD, DOUBLE);
}

AccelStepper stepper1(forwardstep1, backwardstep1);
AccelStepper stepper2(forwardstep2, backwardstep2);
MultiStepper steppers;

void set_target() {
  long target[2];
  
  sscanf(cmd, "G:%ld:%ld", &n1, &n2);
  target[0] = n1;
  target[1] = n2;
  steppers.moveTo(target);
  Serial.println('G');
}

void getset_speed() {
  float v;
  
  if (len == 1) {
    v = stepper1.maxSpeed();
    Serial.print('V');
    Serial.print(':');
    Serial.println(v);
  }
  else {
    v = atof(&cmd[2]);
    stepper1.setMaxSpeed(v);
    stepper2.setMaxSpeed(v);
    Serial.println('V');
  }
}

void release_motors() {
  motor1->release();
  motor2->release();
  Serial.println('S');
}

void query_identity() {
  Serial.println("acam2");
}

void getset_position() {
  if (len == 1) {
    n1 = stepper1.currentPosition();
    n2 = stepper2.currentPosition();
    Serial.print('P');
    Serial.print(':');
    Serial.print(n1);
    Serial.print(':');
    Serial.println(n2);
  }
  else {
    sscanf(cmd, "P:%ld:%ld", &n1, &n2);
    stepper1.setCurrentPosition(n1);
    stepper2.setCurrentPosition(n2);
    Serial.println('P');
  }
}

void query_isrunning() {
  Serial.print('R');
  Serial.print(':');
  Serial.println(is_running);
}

/* Dispatch commands */
void parse_command() {
  switch (cmd[0]) {
    case 'P':
      getset_position();
      break;
    case 'G':
      set_target();
      break;
    case 'R':
      query_isrunning();
      break;
    case 'V':
      getset_speed();
      break;
    case 'S':
      release_motors();
      break;
    case 'Q':
      query_identity();
      break;
    default:
      Serial.println(cmd);
      break;
  }
  len = 0;
  command_ready = false;
}

void debug_command() {
  Serial.print("debug: ");
  Serial.println(cmd);
}

void setup() {
    Serial.begin(9600, SERIAL_8N1); // Serial Port at 9600 baud
    while (!Serial) {
      ;                     // Wait for serial port to connect
    }
    Serial.setTimeout(100);
    
    AFMS.begin();           // AccelStepper setup
    TWBR = ((F_CPU / 800000l) - 16) / 2; // i2C clock 800kHz
    stepper1.setMaxSpeed(500.0);
    stepper2.setMaxSpeed(500.0);
    stepper1.setCurrentPosition(0);	
    stepper2.setCurrentPosition(0);
    steppers.addStepper(stepper1);
    steppers.addStepper(stepper2);
}

void loop() {
    if (command_ready) {
      parse_command();
    }
    is_running = steppers.run();
}

void serialEvent() {
  char c;

  if (Serial.available() > 0 && command_ready == false) {
    c = Serial.read();
    if (c == '\n') {
      cmd[len] = '\0';
      command_ready = true;
    } else {
      cmd[len++] = c;
      if (len >= bufsize) {
        len = bufsize - 1;
      }
    }
  }
}
