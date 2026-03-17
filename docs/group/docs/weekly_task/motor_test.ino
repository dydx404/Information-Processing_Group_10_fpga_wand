const int hapticPin = 26;

void setup() {
  Serial.begin(115200);
  pinMode(hapticPin, OUTPUT);
  digitalWrite(hapticPin, LOW);
  Serial.println("Motor test starting");
}

void loop() {
  Serial.println("MOTOR ON");
  digitalWrite(hapticPin, HIGH);
  delay(1000);

  Serial.println("MOTOR OFF");
  digitalWrite(hapticPin, LOW);
  delay(2000);
}
