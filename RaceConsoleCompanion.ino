#define LANE1 A0
#define LANE2 A1

#define POT A5
#define AMBIANT A4

#define REDPIN 3
#define BLUEPIN 5
#define GREENPIN 4

#define INDICATOR 13

int lane1count = 0;
int lane2count = 0;

int lane1val = 0;
int lane2val = 0;

int lane1last = 0;
int lane2last = 0;

int potVal = 0;
int ambiantVal = 0;

int cutoff = 15;

void setup() {
  
  Serial.begin(9600);
  pinMode(REDPIN, OUTPUT); 
  pinMode(BLUEPIN, OUTPUT); 
  pinMode(GREENPIN, OUTPUT);
  
  pinMode(INDICATOR, OUTPUT);

  delay(1000);

  digitalWrite(REDPIN, HIGH);

  delay(333);

  digitalWrite(GREENPIN, HIGH);

  delay(333);

  digitalWrite(REDPIN, LOW);

  delay(333);

  digitalWrite(GREENPIN, LOW);

  delay(666);

  digitalWrite(BLUEPIN, HIGH);

  delay(75);

  digitalWrite(BLUEPIN, LOW);

  delay(75);

  digitalWrite(BLUEPIN, HIGH);

  delay(75);

  digitalWrite(BLUEPIN, LOW);

  delay(75);

  digitalWrite(BLUEPIN, HIGH);

  delay(75);

  digitalWrite(BLUEPIN, LOW);

  delay(75);
  
}

String pad(String x, int width) {
  
  String result = "";

  for (int i = 0; i <= (width-x.length()); i++) {
    result += " ";
  }

  result +=x;

  return result;
  
}

void loop() {
    
    lane1val = analogRead(LANE1);
    lane2val = analogRead(LANE2);

    ambiantVal = analogRead(AMBIANT);
    potVal = analogRead(POT);

    cutoff = map(potVal, 0, 1023, 0, 25);

    if ( Serial.available() > 0 ) {

      char c = (char)Serial.read();
      
      Serial.println(
        String(lane1count)+" "+
        String(lane2count)+" "+
        String(cutoff)+" "+
        String(ambiantVal)+" "+
        String(lane1val)+" "+
        String(lane2val)+" "+c+" "
      );
      
      if (c = 'B') {
        digitalWrite(INDICATOR, HIGH);
      } else if (c = 'R') {
        lane1count = 0;
        lane2count = 0;
        
        lane1val = 0;
        lane2val = 0;
        
        lane1last = 0;
        lane2last = 0;
      } else {
        digitalWrite(INDICATOR, LOW);
      }
      
    }

    if (lane1val > cutoff && lane1last <= cutoff) {
        ++lane1count;
        digitalWrite(REDPIN, HIGH);
        digitalWrite(GREENPIN, HIGH);
    } else if (lane1val <= cutoff && lane1last > cutoff) {
        digitalWrite(REDPIN, LOW);
        digitalWrite(GREENPIN, LOW);
    }

    if (lane2val > cutoff && lane2last <= cutoff) {
        ++lane2count;
        digitalWrite(BLUEPIN, HIGH);
    } else if (lane2val <= cutoff && lane2last > cutoff) {
        digitalWrite(BLUEPIN, LOW);
    }

    lane1last = lane1val;
    lane2last = lane2val;
  
}
