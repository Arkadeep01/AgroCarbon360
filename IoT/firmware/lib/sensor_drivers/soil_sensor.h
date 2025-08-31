#pragma once
#include <Arduino.h>

class SoilSensor {
public:
    // Constructor: pin, dry raw value, wet raw value
    explicit SoilSensor(uint8_t pin, uint16_t dryRaw = 3200, uint16_t wetRaw = 1200)
        : _pin(pin), _dryRaw(dryRaw), _wetRaw(wetRaw) {}

    // Initialize sensor pin
    void begin() {
        pinMode(_pin, INPUT);
    }

    // Read raw ADC value
    uint16_t readRaw() const {
        return analogRead(_pin);
    }

    // Get soil moisture percentage (0–100%)
    uint8_t readMoisture() const {
        uint16_t raw = readRaw();
        if (raw > _dryRaw) raw = _dryRaw;     // clamp to dry
        if (raw < _wetRaw) raw = _wetRaw;     // clamp to wet

        // Map to 0–100%
        return map(raw, _dryRaw, _wetRaw, 0, 100);
    }

private:
    uint8_t _pin;
    uint16_t _dryRaw;
    uint16_t _wetRaw;
};
