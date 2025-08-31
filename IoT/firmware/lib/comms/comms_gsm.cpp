#include <Arduino.h>
#include "config.h"

#if ENABLE_GSM
  #define TINY_GSM_MODEM_SIM800
  #include <TinyGsmClient.h>
  #include <HTTPClient.h> // For ESP32 HTTPS over TinyGSM? Typically use TinyGsmClient + custom HTTP
  HardwareSerial SerialGSM(1);
  TinyGsm modem(SerialGSM);
  TinyGsmClient gsmClient(modem);
#endif

bool gsm_init() {
#if ENABLE_GSM
  SerialGSM.begin(GSM_SERIAL_BAUD, SERIAL_8N1, GSM_MODEM_RX, GSM_MODEM_TX);
  delay(600);
  if (!modem.restart()) return false;
  if (!modem.gprsConnect(GSM_APN, GSM_USER, GSM_PASS)) return false;
  return true;
#else
  return false;
#endif
}

bool gsm_send_http(const String& payload) {
#if ENABLE_GSM
  // Minimal HTTP POST via TinyGsmClient
  if (!modem.isGprsConnected()) return false;

  // Build raw HTTP request
  String host;
  String path = "/";
  if (String(GSM_HTTP_ENDPOINT).startsWith("http://")) {
    host = String(GSM_HTTP_ENDPOINT).substring(7);
  } else if (String(GSM_HTTP_ENDPOINT).startsWith("https://")) {
    // For true HTTPS you need SSL client (TinyGSM SSL or BearSSL). Keep it simple here:
    host = String(GSM_HTTP_ENDPOINT).substring(8);
  } else host = GSM_HTTP_ENDPOINT;

  int slash = host.indexOf('/');
  if (slash > 0) { path = host.substring(slash); host = host.substring(0, slash); }

  if (!gsmClient.connect(host.c_str(), 80)) return false;

  String req =
    String("POST ") + path + " HTTP/1.1\r\n" +
    "Host: " + host + "\r\n" +
    "Content-Type: application/json\r\n" +
    "Connection: close\r\n" +
    "Content-Length: " + String(payload.length()) + "\r\n\r\n" +
    payload;

  gsmClient.print(req);

  // rudimentary response check
  uint32_t start = millis();
  while (millis() - start < 10000 && !gsmClient.available()) { delay(10); }
  if (!gsmClient.available()) { gsmClient.stop(); return false; }

  // Read status line
  String status = gsmClient.readStringUntil('\n');
  gsmClient.stop();
  return status.indexOf("200") > 0 || status.indexOf("201") > 0 || status.indexOf("202") > 0;
#else
  (void)payload;
  return false;
#endif
}
