#pragma once
#include <Arduino.h>

class TempHumidity {
public:
  void begin();
  bool read(float& tempC, float& rh);
};
