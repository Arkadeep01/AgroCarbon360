#include <Arduino.h>
#include "config.h"
#include "soil_sensor.h"
#include "ph_sensor.h"
#include "temp_humidity.h"

SoilSensor sensor(34);
phSensor ph(41);
tempHumidity th;

void setup() {
  Serial.begin(115200);
  soil.begin("ESP32 Sensor Firmware Starting...");
}

void loop() {
    Serial.printf("Soil: %d | pH: %.2f | Temp/Humidity: %s\n",
                  soil.read(),
                  ph.read(),
                  th.read().c_str());

    delay(2000);
}