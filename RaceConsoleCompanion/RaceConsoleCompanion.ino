#include <LiquidCrystal.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(2, 3, 4, 5, 6, 7, 8, 9, 10, 11);

#define GREENBTN 13
#define REDBTN 12

#define LANE1PIN A1
#define LANE2PIN A0
#define LANE3PIN A2
#define LANE4PIN A3

#define AMBIENT A4
#define POTENTIOMETER A5

#define CUTOFF_DIAL_MAX 25

unsigned long wait = 1000;

int pin[] = {LANE1PIN, LANE2PIN, LANE3PIN, LANE4PIN};
int raw[4] = {0, 0, 0, 0};
bool broken[4] = {false, false, false, false};
int count[4] = {0, 0, 0, 0};

unsigned long time_broken_last[4] = {0, 0, 0, 0};
unsigned long time_broken_second_to_last[4] = {0, 0, 0, 0};

bool game_over = false;
bool playing = false;
bool external_control = false;

bool greenLast = true;
bool redLast = true;

bool greenPressed = false;
bool redPressed = true;

int ambiantVal;
int potVal;

int cutOff;

bool broken_temp;
int raw_temp;

int green_count = 0;
int red_count = 0;

int brightness = 128;

unsigned long now_wait = 0;

bool do_count = true;

String message = "";
String message_buffer = "";

int laps_options[] = {1,3,5,10,15,20,99};

int lap_i = 0;

int winner = 0;

void lcdprint(int col, int row, String message) {
  lcd.setCursor(col, row);
  lcd.print(message);
}

void setup() {
  
  lcd.begin(16, 2);
  
  pinMode(GREENBTN, INPUT_PULLUP);
  pinMode(REDBTN, INPUT_PULLUP);
  
  Serial.begin(115200);
    
  for (int i = 0; i < 4; ++i) {
    lcd.setCursor(i*4,1);
    lcd.print(String(i+1)+":"+String(count[i]));
            if (count[i] < 10) {
              lcd.print(" ");
            }
  }
  
}

void loop() {
    
    ambiantVal = analogRead(AMBIENT);
    potVal = analogRead(POTENTIOMETER);
    cutOff = map(potVal, 0, 1023, 0, CUTOFF_DIAL_MAX);

    if (millis()>5000) {
      bool btnTmp = digitalRead(GREENBTN) == HIGH;
      if (btnTmp && (!greenLast)) {
          ++green_count;
          greenPressed = !external_control;
      }
      greenLast = btnTmp;
      btnTmp = digitalRead(REDBTN) == HIGH;
      if (btnTmp && (!redLast)) {
          ++red_count;
          redPressed = !external_control;
      }
      redLast = btnTmp;
    }
    
    now_wait = millis() - wait;
    
    for (int i = 0; i < 4; ++i) {
      
      raw_temp = analogRead(pin[i]);
      broken_temp = raw_temp > cutOff;

      if ((not broken_temp) && broken[i]) {
        //Serial.println("Lane"+String(i+1)+" "+String(time_broken_last[i])+" "+String(now_wait));
          if (time_broken_last[i] < now_wait) {
            time_broken_second_to_last[i] = time_broken_last[i];
            time_broken_last[i] = millis();
            ++count[i];
            if (playing && count[i] == laps_options[lap_i]) {
              winner = winner*10+(i+1);
            }
            lcd.setCursor(i*4,1);
            lcd.print(String(i+1)+":"+String(count[i]));
            if (count[i] < 10) {
              lcd.print(" ");
            }
          }
      }

      if (winner!=0 && playing) {
        playing = false;
          lcd.home();
        if (!external_control) {
          lcd.print("Player "+String(winner)+" won!   ");
          while (digitalRead(GREENBTN) == LOW) {
            
          }
          while (digitalRead(GREENBTN) == HIGH) {
            
          }
          delay(500);
          lcd.home();
          lcd.print("First to "+String(laps_options[lap_i])+"     ");
        }
      }

      broken[i] = broken_temp;
      raw[i] = raw_temp;
    
    }
    
    if ( Serial.available() > 0 ) {

      while ( Serial.available() > 0 ) {
        message_buffer += (char)Serial.read();
        if (message_buffer.substring(message_buffer.length() - 1, message_buffer.length()) == "\n") {
          String last_message = message;
          message = message_buffer.substring(0, message_buffer.length() - 1);
          message_buffer = "";
          if (message == String("get all")) {
              Serial.print(
        String("{ ")+
        "\"lane_lap_counts\" : [ "+
        String(count[0])+", "+
        String(count[1])+", "+
        String(count[2])+", "+
        String(count[3])+
        "]"+
        ", "+
        "\"lane_sensors_broken\" : [ "+
        String(broken[0])+", "+
        String(broken[1])+", "+
        String(broken[2])+", "+
        String(broken[3])+
        "]"+
        ", "+
        "\"lane_sensors_raw\" : [ "+
        String(raw[0])+", "+
        String(raw[1])+", "+
        String(raw[2])+", "+
        String(raw[3])+
        "]"+
        ", "+
        "\"last_lap_end_time\" : [ "+
        String(time_broken_last[0])+", "+
        String(time_broken_last[1])+", "+
        String(time_broken_last[2])+", "+
        String(time_broken_last[3])+
        "]"+
        ", "+
        "\"last_lap_start_time\" : [ "+
        String(time_broken_second_to_last[0])+", "+
        String(time_broken_second_to_last[1])+", "+
        String(time_broken_second_to_last[2])+", "+
        String(time_broken_second_to_last[3])+
        "]");
        Serial.println(String(", ")+
        "\"ambient_value\" : "+String(ambiantVal)+
        +", "+
        "\"time_now\" : "+String(millis())+
        +", "+
        "\"last_message_recieved\" : \""+last_message+
        "\", "+
        "\"potentiometer_value\" : "+String(potVal)
        +", "+
        "\"laps\" : "+String(laps_options[lap_i])
        +", "+
        "\"wait\" : "+String(wait)
        +", "+
        "\"green_count\" : "+String(green_count)
        +", "+
        "\"external_control\" : "+String(external_control)
        +", "+
        "\"playing\" : "+String(playing)
        +", "+
        "\"winner\" : "+String(winner)
        +", "+
        "\"red_count\" : "+String(red_count)+
        " }"
      );
          } else if (message.startsWith(String("print "))) {
             Serial.println("{ \"message_out\" : \"printed\" }");
             lcd.setCursor(0,0);
             lcd.print(message.substring(6));
          } else if (message.startsWith(String("press red"))) {
             Serial.println("{ \"message_out\" : \"pressed\" }");
             redPressed = true;
          } else if (message.startsWith(String("press both"))) {
             Serial.println("{ \"message_out\" : \"pressed\" }");
             redPressed = true;
             greenPressed = true;
          } else if (message.startsWith(String("toggle external control"))) {
             external_control = !external_control;
             Serial.println("{ \"message_out\" : "+String(external_control)+" }");
          } else if (message.startsWith(String("toggle playing"))) {
             playing = !playing;
             Serial.println("{ \"message_out\" : "+String(playing)+" }");
             if (playing) {
                winner = 0;
             }
          } else if (message.startsWith(String("press green"))) {
             Serial.println("{ \"message_out\" : \"pressed\" }");
             greenPressed = true;
          } else if (message.startsWith(String("wait "))) {
             Serial.println("{ \"message_out\" : \"set\" }");
             wait = message.substring(5).toInt();
          } else if (message.startsWith(String("laps "))) {
             Serial.println("{ \"message_out\" : \"set\" }");
             lcd.setCursor(0,0);
             lap_i = 6;
             laps_options[lap_i] = message.substring(5).toInt();
             lcd.home();
             lcd.print("First to "+String(laps_options[lap_i])+"     ");
          } else if (message == String("reset counts")) {
             Serial.println("{ \"message_out\" : \"reset\" }");
            lcd.setCursor(0,1);
             for (int i = 0; i < 4; i++) {
              count[i] = 0;
              lcd.setCursor(i*4,1);
              lcd.print(String(i+1)+":"+String(count[i]));
            if (count[i] < 10) {
              lcd.print(" ");
            }
            }
          } else {
             Serial.println("{ \"message_out\" : \"Command not recognized.\" }");
          }
        }
      }
    }

    if (greenPressed && redPressed) {

      for (int i = 0; i < 4; i++) {
        count[i] = 0;
        lcd.setCursor(i*4,1);
        lcd.print(String(i+1)+":"+String(count[i]));
            if (count[i] < 10) {
              lcd.print(" ");
            }
      }
      
    } else {
    
      if (greenPressed) {
        greenPressed = false;
        for (int i = 0; i < 4; i++) {
          count[i] = 0;
          lcd.setCursor(i*4,1);
          lcd.print(String(i+1)+":"+String(count[i]));
            if (count[i] < 10) {
              lcd.print(" ");
            }
        }
        if (playing) {
          playing = false;
          lcd.home();
          lcd.print("Race canceled           ");
          delay(1500);
          lcd.home();
          lcd.print("First to "+String(laps_options[lap_i])+"     ");
        } else {
          playing = true;
          winner = 0;
          lcd.setCursor(12,0);
          lcd.print("3...");
          delay(999);
          lcd.setCursor(12,0);
          lcd.print("2...");
          delay(999);
          lcd.setCursor(12,0);
          lcd.print("1...");
          delay(999);
          lcd.setCursor(12,0);
          lcd.print("GO! ");
        }
      }
      if (redPressed) {
        redPressed = false;
        if (!playing) {
          ++lap_i;
          if (lap_i > 5) {
            lap_i = 0;
          }
          lcd.home();
          lcd.print("First to "+String(laps_options[lap_i])+"     ");
        }
      }

    }
}
