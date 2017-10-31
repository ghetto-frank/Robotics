
#include <NewPing.h>

#define sonar_total 4 // Number of sonar sensors.
#define MAX_DISTANCE 999 // Maximum distance (in cm) to ping.

// ---------------add sonar sensors------------
NewPing sonar[sonar_total] = {     // Sensor object array.
    NewPing(2, 2, MAX_DISTANCE), // Each sensor's trigger pin, echo pin, and max distance to ping.
    NewPing(3, 3, MAX_DISTANCE),
    NewPing(4, 4, MAX_DISTANCE),
    NewPing(5, 5, MAX_DISTANCE),
};
// --------------------------------------------


String ver_num = "1.1";


// ---Sensor Reading Storage Arrays.
int sonar_vals[sonar_total]; //array holds sonar values (inch)
int ldr_pin = 0; //single int.


// ----------------------------main setup------------------------
void setup() {
    Serial.begin(115200); //baud rate.
    pinMode(13, OUTPUT); //activity LED on pin 13
    pinMode(12, OUTPUT); //green (underglow) LED Pin 12

    boot_led_flash();
}
// --------------------------------------------------------------


// ------------------------------------------------------------------------------------------------------------------------      

void loop() { //---START MAIN LOOP

  
    if (Serial.available()) { // ---START OF SERIAL COMMANDS---
   
        // -----------------------Build seralport data into readString------------------        
        String readString = "";
    
        while (Serial.available()) {
            delay(2);
            if (Serial.available() > 0) {
                char c = Serial.read();  //gets one byte from serial buffer        
                readString += c; //makes the string readString    
            } 
        }
    
        readString.toLowerCase();  //nice eh
        // -----------------------------------------------------------------------------      


        // ----------------Get /ver command----------------
        if (readString.substring(0,9) == "get /ver"){ //return basic info (helps test everything is working as it should.)
      
            digitalWrite(13, HIGH); // (led on)
            Serial.print("=!v!=Sensor Board V");  
            Serial.println(ver_num);  
            tell_done();
        }
        // -------------------------------------------------

        // ----------------Get /allsonar command---------------
        if (readString.substring(0,13) == "get /allsonar"){ //returns comma seporated values for all sonar sensors.
          
            digitalWrite(13, HIGH); 
            Serial.println(GetAllSonar());
            tell_done(); 
        }
        // -----------------------------------------------
        
        // ----------------Get /sonar command--------------
        if (readString.substring(0,11) == "get /sonar:"){ //returns single sonar value.
          
            digitalWrite(13, HIGH); 

            int single_sonar;
            single_sonar = readString.substring(11,readString.length()).toInt();
            
            Serial.println(GetSonarValue(single_sonar));
            tell_done(); 
        }
        // -----------------------------------------------

        // ----------------Get /ldr command---------------
        if (readString.substring(0,8) == "get /ldr"){ //returns the value of the ldr sensor.
    
            Serial.println(GetLdrValue());
            tell_done(); 
        }
        // -----------------------------------------------

        // ----------------led /on command---------------
        if (readString.substring(0,7) == "led /on"){ //underglow led on.
    
            digitalWrite(13, HIGH); // (led on)
          
            digitalWrite(12, HIGH); // (led on)
            Serial.println("=!v!=LED ON");
            tell_done();
        }
        // -----------------------------------------------

        // ----------------led /off command---------------
        if (readString.substring(0,8) == "led /off"){ //underglow led off.
    
            digitalWrite(13, HIGH); // (led on)
          
            digitalWrite(12, LOW); // (led off)
            Serial.println("=!v!=LED OFF");
            tell_done();
        }
        // -----------------------------------------------



    } // ---END OF SERIAL COMMANDS---
  
delay(1); //stop maxing out CPU.
}//---END MAIN LOOP.  
// ------------------------------------------------------------------------------------------------------------------------      
 
//--------------------------------FUNTIONS---------------------------------


// --------------------------------------------------
void boot_led_flash() {
  
    delay(60);
    Serial.println("\r\nSENSOR BOARD BOOT...");

    for (int flash_delay = 15; flash_delay > 0; flash_delay--) {
      
        digitalWrite(12, HIGH);
        delay(flash_delay * 12);
        digitalWrite(12, LOW);
        delay(60);
    } 

    digitalWrite(12, LOW);
    Serial.println("SENSOR BOARD READY.\r\n");
}
// --------------------------------------------------

// --------------------------------------------------
String GetSonarValue(int sonar_num) {

    if (sonar_num < 0 or sonar_num > sonar_total) { //non valid sonar number (out of range)
        return "error: out of range.";
    }

    int sonar_read = 0; //holds a single sonar reading. 
    String out_line = "=!v!=Sonar";

    out_line += sonar_num;
    out_line += ": ";
    
    sonar_read = sonar[sonar_num].ping_in(); //get distence from sensor in inch.
 
    if (sonar_read > 0) { // oviod 0's
        sonar_vals[sonar_num] = sonar_read; //only replace the value in the global array if >0. (get 0's often)
    }
        
    // ----make output string-----
    out_line += sonar_vals[sonar_num];
    return out_line;
}
// --------------------------------------------------

// --------------------------------------------------
String GetAllSonar() {

    int sonar_read = 0; //holds a single sonar reading.     
    String out_line = "=!v!=All-Sonar: ";

    for (int cur_s = 0; cur_s < sonar_total; cur_s++) {
      
        delay(3); //delay between sensor readingings as may interurpt each other in quick susesion. 
        sonar_read = sonar[cur_s].ping_in(); //get distence from sensor in inch.
 
        if (sonar_read > 0) { // oviod 0's
            sonar_vals[cur_s] = sonar_read; //only replace the value in the global array if >0. (get 0's often)
        }
        
        // ----make output string-----
        out_line += sonar_vals[cur_s];
        out_line += ", ";
    }
    out_line.remove(out_line.length() - 2, 2); //remove last ", ".
    return out_line; 
}
// --------------------------------------------------

// --------------------------------------------------
String GetLdrValue() {
  
    digitalWrite(13, HIGH); 

    String out_line = "=!v!=LDR: ";
    int ldr_reading = 0;
    
    ldr_reading = analogRead(ldr_pin); //max is 1023
    ldr_reading = ldr_reading / 2;
  
    if (ldr_reading > 255){
        ldr_reading = 255;
    }
    // cheeky way of makeing the ldr 'more sensetive' and a good range. could of used MAP() but think this is lighter.

    out_line += ldr_reading;
    return out_line;
}
// --------------------------------------------------

// --------------------------------------------------
void tell_done() { // (so serial client knows that where done).
  
    Serial.println("=!=done=!=");
    digitalWrite(13, LOW); //activity led off.
}
// --------------------------------------------------
