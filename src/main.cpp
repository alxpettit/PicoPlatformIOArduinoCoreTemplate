#include <Arduino.h>
// You can import the full Pico SDK. Its installation is handled by PlatformIO :)
#include <pico.h>

void setup() {
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    // Toggle LED every 200ms
    digitalWrite(PIN_LED, HIGH);
    delay(200);
    digitalWrite(PIN_LED, LOW);
    delay(200);
}
