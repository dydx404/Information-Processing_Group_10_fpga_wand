#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ===== Keep your working IMU pins =====
static const uint8_t SDA_PIN = 32;
static const uint8_t SCL_PIN = 33;
static const uint8_t MPU_ADDR = 0x68;
static const uint8_t LED_PIN = 25;

// ===== WiFi/UDP config (EDIT SSID/PASS ONLY) =====
const char* WIFI_SSID = "temp";
const char* WIFI_PASS = "50405049";

IPAddress PYNQ_IP(172, 27, 155, 164);   // <-- your PYNQ wlan0 IP
const uint16_t UDP_PORT = 5005;

WiFiUDP udp;

// MPU6050 registers
static const uint8_t REG_PWR_MGMT_1   = 0x6B;
static const uint8_t REG_ACCEL_XOUT_H = 0x3B;

bool writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

bool readBytes(uint8_t reg, uint8_t *buf, size_t n) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MPU_ADDR, (int)n) != (int)n) return false;
  for (size_t i = 0; i < n; i++) buf[i] = Wire.read();
  return true;
}

static inline int16_t toInt16(uint8_t hi, uint8_t lo) {
  return (int16_t)((hi << 8) | lo);
}

static void wifiConnect() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.print("WiFi connecting");
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 20000) {
    delay(300);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi OK, ESP32 IP = ");
    Serial.println(WiFi.localIP());
    Serial.print("UDP target PYNQ = ");
    Serial.print(PYNQ_IP);
    Serial.print(":");
    Serial.println(UDP_PORT);

    // optional but fine
    udp.begin(UDP_PORT);

    // one-time test packet
    udp.beginPacket(PYNQ_IP, UDP_PORT);
    udp.print("HELLO_FROM_ESP32");
    udp.endPacket();
  } else {
    Serial.println("WiFi NOT connected. (IMU still runs; UDP disabled)");
  }
}

static void udpSend(const String& msg) {
  if (WiFi.status() != WL_CONNECTED) return;

  if (!udp.beginPacket(PYNQ_IP, UDP_PORT)) {
    Serial.println("UDP beginPacket failed");
    return;
  }
  udp.print(msg);
  if (!udp.endPacket()) {
    Serial.println("UDP endPacket failed");
  }
}

void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);

  if (!writeReg(REG_PWR_MGMT_1, 0x00)) {
    Serial.println("ERROR: Cannot wake MPU6050");
    while (true) delay(1000);
  }
  delay(50);

  wifiConnect();

  Serial.println("Gesture-friendly motion gate running...");
  Serial.println("score_f state");
}

void loop() {
  // ---- read IMU ----
  uint8_t data[14];
  if (!readBytes(REG_ACCEL_XOUT_H, data, sizeof(data))) {
    Serial.println("Read error");
    delay(200);
    return;
  }

  int16_t gx = toInt16(data[8],  data[9]);
  int16_t gy = toInt16(data[10], data[11]);
  int16_t gz = toInt16(data[12], data[13]);

  // ---- motion metric ----
  uint32_t score = (uint32_t)abs(gx) + (uint32_t)abs(gy) + (uint32_t)abs(gz);

  static float score_f = 0.0f;
  const float alpha = 0.12f;
  score_f = (1.0f - alpha) * score_f + alpha * (float)score;

  const float START_TH    = 14000.0f;
  const float CONTINUE_TH = 5000.0f;
  const uint32_t STILL_MS_TO_STOP = 250;
  const uint8_t START_COUNT = 2;

  enum State { IDLE, MOVING };
  static State state = IDLE;

  static uint8_t start_hits = 0;
  static uint32_t still_since_ms = 0;

  static State last_state = IDLE;
  static uint32_t last_update_ms = 0;

  const uint32_t now = millis();

  if (state == IDLE) {
    if (score_f > START_TH) {
      if (++start_hits >= START_COUNT) {
        state = MOVING;
        start_hits = 0;
        still_since_ms = 0;
      }
    } else {
      start_hits = 0;
    }
  } else {
    if (score_f > CONTINUE_TH) {
      still_since_ms = 0;
    } else {
      if (still_since_ms == 0) still_since_ms = now;
      if (now - still_since_ms >= STILL_MS_TO_STOP) {
        state = IDLE;
        still_since_ms = 0;
      }
    }
  }

  digitalWrite(LED_PIN, state == MOVING ? HIGH : LOW);
  Serial.printf("%.0f %s\n", score_f, state == MOVING ? "MOVING" : "IDLE");

  // ---- UDP messages ----
  if (state != last_state) {
    if (state == MOVING) {
      udpSend("GESTURE_START t=" + String(now) + " score=" + String((int)score_f));
    } else {
      udpSend("GESTURE_END t=" + String(now) + " score=" + String((int)score_f));
    }
    last_state = state;
  }

  if (state == MOVING && (now - last_update_ms) >= 100) { // 10 Hz
    udpSend("GESTURE_UPDATE t=" + String(now) + " score=" + String((int)score_f));
    last_update_ms = now;
  }

  delay(20);
}
