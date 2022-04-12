#include <Arduino.h>

// You can import the full Pico SDK. Its installation is handled by PlatformIO :)
#include <pico.h>
#include "uwu.h"

const int pin_uwu = PIN_LED;

__attribute__((unused)) void setup() {
    Serial.begin(115200);
    pinMode(pin_uwu, OUTPUT);
}

__attribute__((unused)) void loop() {
    Serial.println("uwu");
    // Toggle LED every 200ms
    uwu(pin_uwu);
}
