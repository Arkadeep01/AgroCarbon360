#pragma once

/************** BUILD FLAGS **************/
#define ENABLE_WIFI      1   // ESP32 WiFi (MQTT/HTTP)
#define ENABLE_LORA      0   // LoRa/LoRaWAN (set pins below)
#define ENABLE_GSM       0   // GSM/4G via TinyGSM

#define ENABLE_DHT       0   // Use DHT22 sensor for temp/humidity
#define ENABLE_SHT31     0   // Use SHT31 via I2C
#define ENABLE_SOIL_ADC  1   // Soil moisture analog input
#define ENABLE_PH_ADC    1   // pH analog input with calibration
#define ENABLE_GPS       0   // GPS via TinyGPS++/UART

#define SEND_OVER_HTTP   1
#define SEND_OVER_MQTT   0

#define USE_DEEP_SLEEP   1
#define SLEEP_SECONDS    300 // 5 minutes

/************** WIFI **************/
#if ENABLE_WIFI
  #define WIFI_SSID        "RANSOMEWARE"
  #define WIFI_PASS        "Thunder_Bird "
  #define HTTP_ENDPOINT    "https://api.example.com/iot/ingest"
  #define MQTT_BROKER      "broker.example.com"
  #define MQTT_PORT        1883
  #define MQTT_TOPIC       "agrocarbon360/field"
#endif

/************** LORA (SX127x) **************/
#if ENABLE_LORA
  #define LORA_SS_PIN      18
  #define LORA_RST_PIN     14
  #define LORA_DIO0_PIN    26
  #define LORA_BAND        865E6 // India MHz band (865–867 MHz)
#endif

/************** GSM **************/
#if ENABLE_GSM
  #define GSM_APN          "your.apn"
  #define GSM_USER         ""
  #define GSM_PASS         ""
  #define GSM_HTTP_ENDPOINT "https://api.example.com/iot/ingest"
  #define GSM_SERIAL_BAUD  115200
  #define GSM_MODEM_TX     27
  #define GSM_MODEM_RX     26
#endif

/************** PINS: SENSORS **************/
#define PIN_SOIL_ADC       34   // ESP32 ADC1 channel
#define PIN_PH_ADC         35
#define DHT_PIN            4
#define DHT_TYPE           22   // DHT22

/************** GPS UART **************/
#define GPS_RX_PIN         16
#define GPS_TX_PIN         17
#define GPS_BAUD           9600

/************** DEVICE META **************/
#define DEVICE_ID          "FIELD-ESP32-001"
#define FW_VERSION         "0.1.0"








/************** SAFE DEFAULTS **************/
// #ifndef ARDUINO
//   #error "This firmware targets Arduino/ESP32."
// #endif


/******* Hardware Implementations that will be required to activate the Arduino model *******/
// 1. Hardware Requirements
// ESP32 Development Board (e.g., ESP32 DevKitC, NodeMCU-32S)
// Micro USB Cable (for programming and power)
// Soil Moisture Sensor (analog output)
// pH Sensor (analog output)
// Jumper Wires
// Breadboard (optional, for prototyping)
// Power Source (USB or battery, if deploying in the field)
// (Optional: DHT22, SHT31, LoRa, GSM, GPS modules if you enable those features in config.h)
// 2. Wiring Diagram
// Soil Moisture Sensor

// VCC → 3.3V (ESP32)
// GND → GND (ESP32)
// Signal → GPIO 34 (ESP32, as per PIN_SOIL_ADC)
// pH Sensor

// VCC → 3.3V (ESP32)
// GND → GND (ESP32)
// Signal → GPIO 35 (ESP32, as per PIN_PH_ADC)
// (If using other sensors, connect according to their respective pins in config.h.)