#include <Arduino.h>
#include "config.h"

#if ENABLE_WIFI
  #include <WiFi.h>
  #if SEND_OVER_MQTT
    #include <PubSubClient.h>
    static WiFiClient wifiClient;
    static PubSubClient mqttClient(wifiClient);
  #endif
  #if SEND_OVER_HTTP
    #include <HTTPClient.h>
  #endif
#endif

bool wifi_init() {
#if ENABLE_WIFI
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint8_t attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    attempts++;
  }
  if (WiFi.status() != WL_CONNECTED) return false;

  #if SEND_OVER_MQTT
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    uint8_t tries=0;
    while(!mqttClient.connected() && tries<3){
      if(mqttClient.connect(DEVICE_ID)) break;
      delay(1000); tries++;
    }
    if(!mqttClient.connected()) return false;
  #endif
  return true;
#else
  return false;
#endif
}

bool wifi_send_http(const String& payload) {
#if ENABLE_WIFI && SEND_OVER_HTTP
  if (WiFi.status() != WL_CONNECTED) return false;
  HTTPClient http;
  http.begin(HTTP_ENDPOINT);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(payload);
  http.end();
  return code >= 200 && code < 300;
#else
  (void)payload;
  return false;
#endif
}

bool wifi_send_mqtt(const String& topic, const String& payload) {
#if ENABLE_WIFI && SEND_OVER_MQTT
  if (!WiFi.isConnected()) return false;
  if (!mqttClient.connected()) return false;
  return mqttClient.publish(topic.c_str(), payload.c_str(), true);
#else
  (void)topic; (void)payload;
  return false;
#endif
}
