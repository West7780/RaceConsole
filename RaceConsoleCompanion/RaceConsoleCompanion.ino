#define LANE1PIN A0
#define LANE2PIN A1
#define LANE3PIN A2
#define LANE4PIN A3

#define AMBIENT A4
#define POTENTIOMETER A5

#define LANE1INDICATOR 3
#define LANE2INDICATOR 5
#define LANE3INDICATOR 6
#define LANE4INDICATOR 9

#define REMOTE_INDICATOR 13

#define CUTOFF_DIAL_MAX 25

int wait = 1000;

int pin[] = {LANE1PIN, LANE2PIN, LANE3PIN, LANE4PIN};
int indicator[] = {LANE1INDICATOR, LANE2INDICATOR, LANE3INDICATOR, LANE4INDICATOR};
int raw[4] = {0, 0, 0, 0};
bool broken[4] = {false, false, false, false};
int count[4] = {0, 0, 0, 0};
int time_broken_last[4] = {0, 0, 0, 0};
int time_broken_second_to_last[4] = {0, 0, 0, 0};

int ambiantVal;
int potVal;

int cutOff;

bool broken_temp;
int raw_temp;

int brightness = 128;

int now_wait = 0;

String message = "";
String message_buffer = "";

void setup() {
  
  Serial.begin(9600);
  for (int i = 0; i < 4; i++) {
    pinMode(indicator[i], OUTPUT);
  }
  pinMode(REMOTE_INDICATOR, OUTPUT);
  
}

void loop() {
    
    ambiantVal = analogRead(AMBIENT);
    potVal = analogRead(POTENTIOMETER);
    cutOff = map(potVal, 0, 1023, 0, CUTOFF_DIAL_MAX);
    
    now_wait = millis() + wait;
    
    for (int i = 0; i < 4; ++i) {
      
      raw_temp = analogRead(pin[i]);
      broken_temp = raw_temp > cutOff;

      if (broken_temp && not broken[i]) {
          if (time_broken_last[i] > now_wait) {
            time_broken_second_to_last[i] = time_broken_last[i];
            ++count[i];
          }
          digitalWrite(indicator[i], HIGH);
      } else if (not broken[i] && broken_temp) {
          digitalWrite(indicator[i], LOW);
      }

      broken[i] = broken_temp;
      raw[i] = raw_temp;
    
    }
    
    if ( Serial.available() > 0 ) {

      while (Serial.available() > 0) {
        message_buffer += (char)Serial.read();
        if (message_buffer.substring(message_buffer.length() - 1, message_buffer.length()) == "\n") {
          message = message_buffer;
          message_buffer = "";
          case (message) {
            case String("indicator on"):
              digitalWrite(SOFTWARE_INDICATOR, HIGH);
              break;
            case String("indicator off"):
              digitalWrite(SOFTWARE_INDICATOR, LOW);
              break;
            default:
              break;
          }
          break;
        }
      }
      
      Serial.println(
        String("{ ")+
        "lane_counts : [ "+
        String(count[0])+", "+
        String(count[1])+", "+
        String(count[2])+", "+
        String(count[3])+
        "]"+
        ", "+
        "lanes_broken: [ "+
        String(broken[0])+", "+
        String(broken[1])+", "+
        String(broken[2])+", "+
        String(broken[3])+
        "]"+
        ", "+
        "lanes_raw: [ "+
        String(raw[0])+", "+
        String(raw[1])+", "+
        String(raw[2])+", "+
        String(raw[3])+
        "]"+
        ", "+
        "time_broken_last: [ "+
        String(time_broken_last[0])+", "+
        String(time_broken_last[1])+", "+
        String(time_broken_last[2])+", "+
        String(time_broken_last[3])+
        "]"+
        ", "+
        "time_broken_second_to_last: [ "+
        String(time_broken_second_to_last[0])+", "+
        String(time_broken_second_to_last[1])+", "+
        String(time_broken_second_to_last[2])+", "+
        String(time_broken_second_to_last[3])+
        "]"+
        ", "+
        "ambiant_value: "+String(ambiantVal)+
        +", "+
        "potentiometer_value: "+String(potVal)+
        "}"
      );

    }
  
}
