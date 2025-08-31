// serial_reader.ino
#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  if (!isnan(temp) && !isnan(hum)) {
    Serial.print("{\"temperature\":");
    Serial.print(temp);
    Serial.print(",\"humidity\":");
    Serial.print(hum);
    Serial.println("}");
  }
  delay(5000);
}
