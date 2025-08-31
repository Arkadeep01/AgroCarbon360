#pragma once
#include <Arduino.h>

class PHSensor {
public:
  explicit PHSensor(uint8_t pin, float vRef=3.3f, uint16_t adcMax=4095)
  : _pin(pin), _vRef(vRef), _adcMax(adcMax) {}

  void begin() {}

  // Simple linear calibration: pH = slope * voltage + offset
  void setCalibration(float slope, float offset) { _slope = slope; _offset = offset; }

  float readPH(uint16_t samples=10) {
    uint32_t acc=0;
    for (uint16_t i=0;i<samples;++i){ acc+=analogRead(_pin); delay(5); }
    uint16_t raw = acc / samples;
    float voltage = (raw * _vRef) / _adcMax;
    return _slope * voltage + _offset;
  }

  uint16_t readRaw(uint16_t samples=10) {
    uint32_t acc=0;
    for (uint16_t i=0;i<samples;++i){ acc+=analogRead(_pin); delay(5); }
    return acc / samples;
  }

private:
  uint8_t _pin;
  float _vRef;
  uint16_t _adcMax;
  float _slope = -5.70f; // Example slope (change per calibration)
  float _offset = 21.34f; // Example offset (change per calibration)
};
