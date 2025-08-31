#include "temp_humidity.h"
#include "../config.h"

#if ENABLE_DHT
  #include <DHT.h>
  static DHT dht(DHT_PIN, DHT_TYPE);
#elif ENABLE_SHT31
  #include <Wire.h>
  #include <Adafruit_SHT31.h>
  static Adafruit_SHT31 sht31 = Adafruit_SHT31();
#endif

void TempHumidity::begin() {
#if ENABLE_DHT
  dht.begin();
#elif ENABLE_SHT31
  Wire.begin();
  sht31.begin(0x44);
#endif
}

bool TempHumidity::read(float& tempC, float& rh) {
#if ENABLE_DHT
  tempC = dht.readTemperature();
  rh    = dht.readHumidity();
  if (isnan(tempC) || isnan(rh)) return false;
  return true;
#elif ENABLE_SHT31
  tempC = sht31.readTemperature();
  rh    = sht31.readHumidity();
  if (isnan(tempC) || isnan(rh)) return false;
  return true;
#else
  // Fallback stub for testing without hardware
  tempC = 28.5;
  rh = 62.0;
  return true;
#endif
}
