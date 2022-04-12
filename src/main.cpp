#include <Arduino.h>
#include <Wire.h>
#include <PCA9685.h>
// You can import the full Pico SDK. Its installation is handled by PlatformIO :)
#include <pico.h>
#include "uwu.h"

const int pin_uwu = PIN_LED;

void setup() {
    Serial.begin(115200);
    pinMode(pin_uwu, OUTPUT);
}

void loop() {
    Serial.println("uwu");
    // Toggle LED every 200ms
    uwu(pin_uwu);
}
