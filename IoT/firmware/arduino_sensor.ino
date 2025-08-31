#include <Arduino.h>
#include "sensor_drivers/soil_sensor.h"
#include "sensor_drivers/temp_humidity.h"
#include "sensor_drivers/ph_sensor.h"

#define SOIL_PIN A0

SoilSensor soil(SOIL_PIN);
TempHumidity th;
PHSensor ph(A1);

void setup(){
  Serial.begin(9600);
  soil.begin();
  th.begin();
  ph.begin();
  // Example calibration — replace with your field calibration
  ph.setCalibration(-5.70f, 21.34f);
}

void loop(){
  float t=0, h=0;
  th.read(t,h);
  float soilPct = soil.readPercent(10);
  float phVal   = ph.readPH(10);

  Serial.print("TempC: "); Serial.print(t,1);
  Serial.print("  RH%: "); Serial.print(h,1);
  Serial.print("  Soil%: "); Serial.print(soilPct,1);
  Serial.print("  pH: "); Serial.println(phVal,2);

  delay(2000);
}
