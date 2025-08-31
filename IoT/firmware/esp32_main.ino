#include <Arduino.h>
#include "config.h"
#include "sensor_drivers/soil_sensor.h"
#include "sensor_drivers/temp_humidity.h"
#include "sensor_drivers/ph_sensor.h"
#include "sensor_drivers/gps_module.h"

// Extern comms functions (implemented in .cpp files)
extern bool wifi_init();
extern bool wifi_send_http(const String& payload);
extern bool wifi_send_mqtt(const String& topic, const String& payload);

extern bool lora_init();
extern bool lora_send(const String& payload);

extern bool gsm_init();
extern bool gsm_send_http(const String& payload);

// Sensors
SoilSensor   soil(PIN_SOIL_ADC);
PHSensor     ph(PIN_PH_ADC);
TempHumidity th;
GPSModule    gps;

static String makePayload(float tempC, float rh, float soilPct, float phVal, const GpsFix& fix) {
  // Small manual JSON to avoid extra deps
  String json = "{";
  json += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  json += "\"fw\":\"" + String(FW_VERSION) + "\",";
  json += "\"ts\":" + String((uint32_t) (millis()/1000)) + ",";
  json += "\"sensors\":{";
  json += "\"temp_c\":" + String(tempC, 2) + ",";
  json += "\"humidity\":" + String(rh, 1) + ",";
  json += "\"soil_pct\":" + String(soilPct, 1) + ",";
  json += "\"ph\":" + String(phVal, 2);
  json += "},";
  json += "\"loc\":{";
  if (fix.valid) {
    json += "\"lat\":" + String(fix.lat, 6) + ",";
    json += "\"lon\":" + String(fix.lon, 6) + ",";
    json += "\"hdop\":" + String(fix.hdop, 1);
  }
  json += "}}";
  return json;
}

static void goToSleep() {
#if USE_DEEP_SLEEP
  esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_SECONDS * 1000000ULL);
  esp_deep_sleep_start();
#endif
}

void setup() {
  Serial.begin(115200);
  delay(400);

  // Init sensors
  soil.begin();
  ph.begin();
  th.begin();
#if ENABLE_GPS
  gps.begin(GPS_BAUD, GPS_RX_PIN, GPS_TX_PIN);
#endif

  // Init comms (best effort)
#if ENABLE_WIFI
  if (wifi_init()) Serial.println("[OK] WiFi ready");
  else Serial.println("[WARN] WiFi init failed");
#endif
#if ENABLE_LORA
  if (lora_init()) Serial.println("[OK] LoRa ready");
  else Serial.println("[WARN] LoRa init failed");
#endif
#if ENABLE_GSM
  if (gsm_init()) Serial.println("[OK] GSM ready");
  else Serial.println("[WARN] GSM init failed");
#endif
}

void loop() {
  float tempC=0, rh=0, soilPct=0, phVal=7.0;
  th.read(tempC, rh);
#if ENABLE_SOIL_ADC
  soilPct = soil.readPercent(15);
#endif
#if ENABLE_PH_ADC
  phVal = ph.readPH(20);
#endif

  GpsFix fix;
#if ENABLE_GPS
  fix = gps.readFix(1200);
#endif

  String payload = makePayload(tempC, rh, soilPct, phVal, fix);
  Serial.println("[PAYLOAD] " + payload);

  bool sent = false;

#if ENABLE_WIFI
  #if SEND_OVER_HTTP
    if (!sent) sent = wifi_send_http(payload);
  #endif
  #if SEND_OVER_MQTT
    if (!sent) sent = wifi_send_mqtt(MQTT_TOPIC, payload);
  #endif
#endif

#if ENABLE_LORA
  if (!sent) sent = lora_send(payload);
#endif

#if ENABLE_GSM
  if (!sent) sent = gsm_send_http(payload);
#endif

  Serial.println(sent ? "[TX] Success" : "[TX] Failed (no link)");
  delay(200);

  goToSleep(); // if deep sleep disabled, loop continues
  delay(1000); // fallback delay
}
