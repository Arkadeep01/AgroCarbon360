#pragma once
#include <Arduino.h>

struct GpsFix {
  bool valid = false;
  double lat = 0.0;
  double lon = 0.0;
  float  hdop = 0.0f;
};

class GPSModule {
public:
  void begin(long baud, int8_t rxPin, int8_t txPin);
  GpsFix readFix(uint32_t timeoutMs=1000);
};
