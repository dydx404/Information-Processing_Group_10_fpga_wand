const int irPin = 25;

void setup() {
  Serial.begin(115200);
  pinMode(irPin, OUTPUT);
  digitalWrite(irPin, LOW);
  Serial.println("IR LED test starting");
}

void loop() {
  Serial.println("IR LED ON");
  digitalWrite(irPin, HIGH);
  delay(2000);

  Serial.println("IR LED OFF");
  digitalWrite(irPin, LOW);
  delay(2000);
}
