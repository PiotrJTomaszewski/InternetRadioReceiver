
#define F_CPU 8000000UL
#include <Arduino.h>
#define DEBOUNCE_TIME 50
#define NORMAL_BUTTONS 4
// Number of buttons including those 3 of the rotary encoder
#define ALL_BUTTONS 7

enum BUTTONS {BTN_0, BTN_1, BTN_2, BTN_3, ENC_A, ENC_B, ENC_BTN};


// Bit 0-3 buttons states (1 if a button is pressed)
// Bit 4 - 1 if the encoder is turning right
// Bit 5 - 1 if the encoder is turning left
// Bit 6 - encoder button (1 if it's pressed)
int message;

// For how long each button was pressed (counting down)
unsigned long last_pressed_time[NORMAL_BUTTONS];
unsigned long last_time_encoder_btn;
unsigned long last_time_encoder_a;
uint8_t last_register_state;

void setup() {
  message = 0x00;
  last_register_state = 0xff;
  last_pressed_time[0] = 0x00;
  last_pressed_time[1] = 0x00;
  last_pressed_time[2] = 0x00;
  last_pressed_time[3] = 0x00;
  last_time_encoder_btn = 0x00;
  last_time_encoder_a = 0x00;
  // Setup port B as an input
  DDRB = 0x00;
  // Disable pull-ups on port B
  PORTB = 0x00;
  delay(10);

  Serial.begin(9600);
}

void loop() {
  uint8_t register_state = PINB;
  for(int8_t i=NORMAL_BUTTONS-1; i>=0; --i) {
    if (((register_state & _BV(i)) == 0) && ((last_register_state & _BV(i)) != 0)) {
      if (millis() - last_pressed_time[i] > DEBOUNCE_TIME) {
        message |= _BV(i);
//        Serial.println(i);
        last_pressed_time[i] = millis();
      }
    } 
  }

  // Rotary encoder button
  if (((register_state & _BV(ENC_BTN)) == 0) && ((last_register_state & _BV(ENC_BTN)) != 0)) {
    if (millis() - last_time_encoder_btn > DEBOUNCE_TIME) {
      message |= _BV(ENC_BTN);
      last_time_encoder_btn = millis();
    }
  }

  // Rotary encoder
  if (((register_state & _BV(ENC_A)) == 0) && ((last_register_state & _BV(ENC_A)) != 0)) {
    if ((register_state & _BV(ENC_B)) == 0)
      message |= 0x10;
    else
      message |= 0x20;
  }

 if (message != 0x00) {
   Serial.write(message);
   message = 0x00;
 }

  last_register_state = register_state;
}