#include <Arduino.h>
#include "config.h"

#if ENABLE_LORA
  #include <SPI.h>
  #include <LoRa.h>
#endif

bool lora_init() {
#if ENABLE_LORA
  SPI.begin();
  LoRa.setPins(LORA_SS_PIN, LORA_RST_PIN, LORA_DIO0_PIN);
  if (!LoRa.begin((long)LORA_BAND)) {
    return false;
  }
  return true;
#else
  return false;
#endif
}

bool lora_send(const String& payload) {
#if ENABLE_LORA
  LoRa.beginPacket();
  LoRa.print(payload);
  int r = LoRa.endPacket(); // returns 1 on success
  return r == 1;
#else
  (void)payload;
  return false;
#endif
}
