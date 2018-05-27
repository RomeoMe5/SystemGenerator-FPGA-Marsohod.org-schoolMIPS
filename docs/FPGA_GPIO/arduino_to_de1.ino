int pin_a1 = 10;
int pin_a2 = 11;
int pin_a3 = 12;

int data1 = 0;
int data2 = 0;
int data3 = 0;
int incomingByte = 0;
int counter = 1;

void setup() {
  pinMode(pin_a1, OUTPUT);
  pinMode(pin_a2, OUTPUT);
  pinMode(pin_a3, OUTPUT);

  Serial.begin(9600);

  Serial.println("number of set");
}

void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();

    if (incomingByte == 48) /* 0 */ {
      switch (counter) {
        case 1:
          data1 = 0;
          counter++;

          Serial.print("set data1   ");
          Serial.println(data1);
          break;
        case 2:
          data2 = 0;
          counter++;

          Serial.print("set data2   ");
          Serial.println(data2);
          break;
        case 3:
          data3 = 0;
          counter = 1;

          Serial.print("set data3   ");
          Serial.println(data3);

          digitalWrite(pin_a1, data1);
          digitalWrite(pin_a2, data2);
          digitalWrite(pin_a3, data3);

          Serial.print("set   ");
          Serial.print(data1);
          Serial.print("   ");
          Serial.print(data2);
          Serial.print("   ");
          Serial.print(data3);
          Serial.println("");
          break;
      }
    }
    if (incomingByte == 49) /* 1 */ {
      switch (counter) {
        case 1:
          data1 = 1;
          counter++;

          Serial.print("set data1   ");
          Serial.println(data1);
          break;
        case 2:
          data2 = 1;
          counter++;

          Serial.print("set data2   ");
          Serial.println(data2);
          break;
        case 3:
          data3 = 1;
          counter=1;

          Serial.print("set data3   ");
          Serial.println(data3);

          digitalWrite(pin_a1, data1);
          digitalWrite(pin_a2, data2);
          digitalWrite(pin_a3, data3);

          Serial.print("set   ");
          Serial.print(data1);
          Serial.print("   ");
          Serial.print(data2);
          Serial.print("   ");
          Serial.print(data3);
          Serial.println("");
          break;
      }
    }
  }
}
