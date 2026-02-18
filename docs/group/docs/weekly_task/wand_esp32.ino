#include <Arduino.h>
#include <Wire.h>

static const int PIN_BTN     = 18;
static const int PIN_SWITCH  = 19;
static const int PIN_IR_LED  = 23;

static const int PIN_I2C_SDA = 21;
static const int PIN_I2C_SCL = 22;

static const int PIN_UART_TX = 17;
static const int PIN_UART_RX = 16;
static const uint32_t UART_BAUD = 115200;

static const uint8_t MPU_ADDR = 0x68;
static const uint8_t REG_PWR_MGMT_1 = 0x6B;
static const uint8_t REG_ACCEL_XOUT_H = 0x3B;

struct ImuRaw {
  int16_t ax, ay, az;
  int16_t gx, gy, gz;
};

static bool i2cWrite8(uint8_t addr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  Wire.write(val);
  return (Wire.endTransmission() == 0);
}

static bool i2cRead(uint8_t addr, uint8_t reg, uint8_t* out, size_t len) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  size_t got = Wire.requestFrom((int)addr, (int)len);
  if (got != len) return false;
  for (size_t i = 0; i < len; i++) out[i] = Wire.read();
  return true;
}

static bool mpuInit() {
  return i2cWrite8(MPU_ADDR, REG_PWR_MGMT_1, 0x00);
}

static bool mpuRead(ImuRaw &v) {
  uint8_t buf[14];
  if (!i2cRead(MPU_ADDR, REG_ACCEL_XOUT_H, buf, sizeof(buf))) return false;
  v.ax = (int16_t)((buf[0] << 8) | buf[1]);
  v.ay = (int16_t)((buf[2] << 8) | buf[3]);
  v.az = (int16_t)((buf[4] << 8) | buf[5]);
  v.gx = (int16_t)((buf[8] << 8) | buf[9]);
  v.gy = (int16_t)((buf[10] << 8) | buf[11]);
  v.gz = (int16_t)((buf[12] << 8) | buf[13]);
  return true;
}

static bool lastBtnStable = false;
static bool lastBtnRaw = false;
static uint32_t lastBtnChangeMs = 0;

static bool readButtonPressedEdge(uint32_t nowMs) {
  bool rawPressed = (digitalRead(PIN_BTN) == LOW);
  if (rawPressed != lastBtnRaw) {
    lastBtnRaw = rawPressed;
    lastBtnChangeMs = nowMs;
  }
  const uint32_t DEBOUNCE_MS = 25;
  if ((nowMs - lastBtnChangeMs) >= DEBOUNCE_MS) {
    bool edge = (!lastBtnStable && lastBtnRaw);
    lastBtnStable = lastBtnRaw;
    return edge;
  }
  return false;
}

static bool isArmed() {
  return (digitalRead(PIN_SWITCH) == LOW);
}

static bool recording = false;
static const uint32_t SAMPLE_PERIOD_MS = 10;
static uint32_t lastSampleMs = 0;

void setup() {
  pinMode(PIN_BTN, INPUT_PULLUP);
  pinMode(PIN_SWITCH, INPUT_PULLUP);
  pinMode(PIN_IR_LED, OUTPUT);
  digitalWrite(PIN_IR_LED, LOW);

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(400000);

  Serial2.begin(UART_BAUD, SERIAL_8N1, PIN_UART_RX, PIN_UART_TX);

  (void)mpuInit();

  Serial2.println("<BOOT>");
}

static void sendStartMarker() {
  Serial2.println("<START>");
}

static void sendEndMarker() {
  Serial2.println("<END>");
}

static void sendSampleLine(uint32_t tMs, const ImuRaw& imu) {
  Serial2.print("DATA,");
  Serial2.print(tMs);
  Serial2.print(",");
  Serial2.print(imu.ax); Serial2.print(",");
  Serial2.print(imu.ay); Serial2.print(",");
  Serial2.print(imu.az); Serial2.print(",");
  Serial2.print(imu.gx); Serial2.print(",");
  Serial2.print(imu.gy); Serial2.print(",");
  Serial2.println(imu.gz);
}

void loop() {
  const uint32_t now = millis();

  const bool armed = isArmed();
  if (!armed) {
    if (recording) {
      recording = false;
      sendEndMarker();
    }
    digitalWrite(PIN_IR_LED, LOW);
    delay(5);
    return;
  }

  digitalWrite(PIN_IR_LED, HIGH);

  if (readButtonPressedEdge(now)) {
    recording = !recording;
    if (recording) sendStartMarker();
    else sendEndMarker();
  }

  if (recording && (now - lastSampleMs >= SAMPLE_PERIOD_MS)) {
    lastSampleMs = now;
    ImuRaw imu{};
    if (!mpuRead(imu)) {
      imu = ImuRaw{0,0,0,0,0,0};
    }
    sendSampleLine(now, imu);
  }
}
