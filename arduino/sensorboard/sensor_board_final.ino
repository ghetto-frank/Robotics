
#include <NewPing.h>

#define SONAR_NUM 4 // Number of sonar sensors.
#define MAX_DISTANCE 999 // Maximum distance (in cm) to ping.

// ---------------add sonar sensors------------
NewPing sonar[SONAR_NUM] = {     // Sensor object array.
  NewPing(2, 2, MAX_DISTANCE), // Each sensor's trigger pin, echo pin, and max distance to ping.
  NewPing(3, 3, MAX_DISTANCE),
  NewPing(4, 4, MAX_DISTANCE),
  NewPing(5, 5, MAX_DISTANCE),
  //NewPing(6, 6, MAX_DISTANCE),
  //NewPing(7, 7, MAX_DISTANCE),
  //NewPing(8, 8, MAX_DISTANCE),
  //NewPing(9, 9, MAX_DISTANCE),
};
// --------------------------------------------


// ---For PrintSonarVals Function:
int sonar_vals[SONAR_NUM]; //array holds sonar values (inch)
// ----



int ldr_pin = 0;





String readString; //seralport in string.


void setup() {
    Serial.begin(115200); //baud rate.
    pinMode(13, OUTPUT); //activity LED on pin 13
    pinMode(12, OUTPUT); //green (underglow) LED Pin 12

    boot_led_flash();
}



// ------------------------------------------------------------------------------------------------------------------------      

void loop() { //---START MAIN LOOP

  
    if (Serial.available()) { // ---START OF SERIAL COMMANDS---
   
        // -----------------------Build seralport data into readString------------------        
        readString = "";
    
        while (Serial.available()) {
            delay(2);
        
            if (Serial.available() > 0) {
                char c = Serial.read();  //gets one byte from serial buffer        
                readString += c; //makes the string readString    
            } 
         
        }
    
        readString.toLowerCase();  //nice eh
        // -----------------------------------------------------------------------------      


        // ----------------Get /info command----------------
        if (readString.substring(0,9) == "get /info"){
    
            digitalWrite(13, HIGH); // (led on)
            tell_info();
        }
        // -------------------------------------------------



        // ----------------Get /sonar command---------------
        if (readString.substring(0,10) == "get /sonar"){
    
            digitalWrite(13, HIGH); // (led on)
            PrintSonarVals();
        }
        // -----------------------------------------------



        // ----------------Get /ldr command---------------
        if (readString.substring(0,8) == "get /ldr"){
    
            digitalWrite(13, HIGH); // (led on)
            PrintLdrVals();
        }
        // -----------------------------------------------



        // ----------------led /on command---------------
        if (readString.substring(0,7) == "led /on"){
    
            digitalWrite(13, HIGH); // (led on)
            digitalWrite(12, HIGH); // (led on)
            Serial.println("=!v!=LED ON");
            tell_done();
        }
        // -----------------------------------------------


        // ----------------led /off command---------------
        if (readString.substring(0,8) == "led /off"){
    
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
void PrintSonarVals() {

    digitalWrite(13, HIGH); 
    
    String out_line = "=!v!=Sonar: ";
    int sonar_read = 0; //holds single sonar reading. 


    for (int cur_s = 0; cur_s < SONAR_NUM; cur_s++) {
      
        delay(4);
        // ------- get new values --------
        sonar_read = sonar[cur_s].ping_in();
 
        if (sonar_read > 0) { // oviod 0's, seems to randomly get them 
            sonar_vals[cur_s] = sonar_read;
        }
        // --------------
    // ----make output string-----
    out_line += sonar_vals[cur_s];
    out_line += ", ";
    }


    out_line.remove(out_line.length() - 2, 2); //remove last ", ".
    Serial.println(out_line);
  
    tell_done();  
}
// --------------------------------------------------





// --------------------------------------------------
void PrintLdrVals() {
  
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
    Serial.println(out_line); //print reading
  
    tell_done();
}
// --------------------------------------------------








// --------------------------------------------------
void tell_info() {

    Serial.println("=!v!=Sensor Board V1.0");  
      
    tell_done();
}
// --------------------------------------------------





// --------------------------------------------------
void tell_done() { // (so serial client knows that where done).
  
    Serial.println("=!=done=!=");
    digitalWrite(13, LOW); //activity led off.
}
// --------------------------------------------------

