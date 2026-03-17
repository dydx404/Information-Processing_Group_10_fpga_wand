#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

const int irPin = 25;        
const int hapticPin = 26;     

const int gyroThreshold = 9000;    
const int pulseTime = 180;        
const int cooldownTime = 300;       

unsigned long pulseEndTime = 0;
unsigned long nextAllowedTrigger = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);   // SDA, SCL

  pinMode(irPin, OUTPUT);
  pinMode(hapticPin, OUTPUT);

  digitalWrite(irPin, LOW);
  digitalWrite(hapticPin, LOW);

  mpu.initialize();

  Serial.println("ESP32 wand ready");
}

void loop() {
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  int gyroMotion = abs(gx) + abs(gy) + abs(gz);

  Serial.print("G: ");
  Serial.print(gx); Serial.print(" ");
  Serial.print(gy); Serial.print(" ");
  Serial.print(gz); Serial.print(" | Gyro motion: ");
  Serial.println(gyroMotion);

  unsigned long now = millis();

  if (gyroMotion > gyroThreshold && now > nextAllowedTrigger) {
    digitalWrite(irPin, HIGH);
    digitalWrite(hapticPin, HIGH);

    pulseEndTime = now + pulseTime;
    nextAllowedTrigger = now + cooldownTime;

    Serial.println("FLICK DETECTED");
  }

  if (now > pulseEndTime) {
    digitalWrite(irPin, LOW);
    digitalWrite(hapticPin, LOW);
  }

  delay(15);
}
