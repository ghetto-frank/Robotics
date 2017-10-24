#include <NewPing.h>

#define SONAR_NUM     4 // Number of sonar sensors.
#define MAX_DISTANCE 999 // Maximum distance (in cm) to ping.

// ------------------add sensors---------------
// ---side note: shame it doesnt seem posible to do this in an array loop to save on lines.
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


void setup() {
  Serial.begin(115200); //baud rate.
  pinMode(13, OUTPUT); //activity LED on pin 13
  pinMode(12, OUTPUT); //green (underglow) LED Pin 12

}










// -------------------------------------------------SET VARS-------------------------------------

String vernum="1.2 beta";
int startup_flash = 18;

// ---For PrintSonarVals Function:
int x=0;
int sonar_vals[SONAR_NUM]; //array holds sonar values (inch)
int getvaluedelay=2; //how long to delay between getting each sonar vaule (can interfear if to low)
int tempval=0;
// ----

//---For PrintLdrsonar_vals Function:
int ldrpin=A0; //pin ldr is on
int ldr_reading; //holds 0-255 of light reading.
// ----


// ---For Testmodes:
int sonar_testmode=0;
int ldr_testmode=0;

// ---For Serial Port:
String readString; //seralport in string

// -----------------------------------------------END SET VARS------------------------------------
 
 
 
 
 
// ----------------------------------------------START MAINLOOP-----------------------------------
void loop() {

// ---------------------------------------BOOTUP LED FLASHS------------------------
  while (startup_flash > 0) {

    digitalWrite(13, HIGH);
    
    delay(70);

    digitalWrite(13, LOW);
    digitalWrite(12, HIGH);
    delay(startup_flash * 12);
    
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    startup_flash = startup_flash - 1;
  }
  
// ---------------------------------------------------------------------------------


  
 if(Serial.available()) { // ------------START OF SERIAL COMMANDS-------------
   
// ----------------------------------------------Build seralport data into readString-------------------------------------        
    readString = "";
    
    while (Serial.available()) {
        delay(2);
        if (Serial.available() > 0) {
  	        char c = Serial.read();  //gets one byte from serial buffer        
            readString += c; //makes the string readString    
        }  
    }
    
    readString.toLowerCase();  //nice eh
// ------------------------------------------------------------------------------------------------------------------------      

// --------------------------------------------------SERIAL COMMANDS-------------------------------------------------------      


  // -----------------LED ON COMMAND----------------
  if (readString.substring(0,6) == "led on"){
    digitalWrite(12, HIGH); // (led on)
    Serial.println("Underglow LED on.");
    Serial.println("[LED_OK]");
  }
  
  // -----------------LED OFF COMMAND----------------
  if (readString.substring(0,7) == "led off"){
    digitalWrite(12, LOW); // (led on)
    Serial.println("Underglow LED off.");
    Serial.println("[LED_OK]");
  }





  // -----------------INFO COMMAND----------------
  if (readString.substring(0,4) == "info"){
    
    digitalWrite(13, HIGH); // (led on)
    
    
    Serial.print(" --=-Spider-Sence-=--  Sensor Board. V");
    Serial.print(vernum);
    Serial.println("");
    Serial.println("--------------------");
    
    Serial.println("Sonar Sensors: ");
    Serial.print("   - Count:");
    Serial.print(SONAR_NUM);
    Serial.println("");
    
    Serial.print("   - Range(Inch):1-");
    Serial.print(MAX_DISTANCE);
    Serial.println("");
    
    Serial.print("   - Time Per Sonar(Ms):");
    Serial.print(getvaluedelay);
    Serial.println("");
    
    Serial.print("   - Time For All(Ms):");
    Serial.print(getvaluedelay * SONAR_NUM);
    Serial.println("");

    Serial.println("");
    Serial.println("LDR Sensors: ");
    Serial.println("   - Count:1");
    Serial.println("   - Range:1-255");
    Serial.println("--------------------");
    
    Serial.println("[DONE]");
    digitalWrite(13, LOW); // (led off)
  }
  // --------------------------------------------



  // -----------------GET ALL COMMAND----------------  
  if (readString.substring(0,7) == "get all"){
    PrintSonarVals();
    PrintLdrVals();
    Serial.println("[GET_ALL_DONE]");
  }
  
  
  // -----------------GET SONAR COMMAND----------------  
  if (readString.substring(0,9) == "get sonar"){
    PrintSonarVals();
  }


  
  // -----------------GET LDR COMMAND----------------  
  if (readString.substring(0,7) == "get ldr"){
    PrintLdrVals();
    Serial.println("[DONE]");
  }






  
  // -----------------TESTSONAR ON COMMAND----------------
  if (readString.substring(0,12) == "testsonar on"){
    sonar_testmode=1;
    Serial.println("Sonar Test Mode Is On.");
    Serial.println("");
  }

  // -----------------TESTSONAR OFF COMMAND----------------
  if (readString.substring(0,13) == "testsonar off"){
    sonar_testmode=0;
    Serial.println("Sonar Test Mode Is Off.");
    Serial.println("");
  }


  // -----------------TESTLDR ON COMMAND----------------
  if (readString.substring(0,10) == "testldr on"){
    ldr_testmode=1;
    Serial.println("");
    Serial.println("LDR Test Mode Is On.");
    Serial.println("");
  }

  // -----------------TESTLDR OFF COMMAND----------------
  if (readString.substring(0,11) == "testldr off"){
    ldr_testmode=0;
    Serial.println("");
    Serial.println("LDR Test Mode Is Off.");
    Serial.println("");
  }






  // ---------------REFRESH COMMAND--------------
  if (readString.substring(0,8) == "refresh="){
    readString.replace("refresh=", ""); //Replace 'refresh=' with nothing to just get the number
    getvaluedelay = readString.toInt(); //Convert to Int.
    if (getvaluedelay > 0 and getvaluedelay < 2000) {  //Check its in range.
      Serial.print("Each Sonar Will Now Take: ");
      Serial.print(getvaluedelay);
      Serial.print("ms To Complete And ");
      Serial.print(getvaluedelay * SONAR_NUM);
      Serial.print("ms To Read All.");
      
      Serial.println("");
      Serial.println("[DONE]");
    }else { 
      Serial.print("Refresh Invalid! (remaining unchanged)");  //Its not in range.
      Serial.println("");
      Serial.println("[ERROR]");
    }
  }

  

  } // ---END OF SERIAL COMMANDS---
   



// -------------------------------------------------------------CONTUNIUES COMMANDS------------------------------------

// --------------TEST COMMAND--------------
if (sonar_testmode == 1) {
  PrintSonarVals();
  
//  while (x < SONAR_NUM) {
//    sonar_vals[x] 
//    x = x + 1;
//  }

}
// -----------------------------------------


// --------------TESTLDR COMMAND--------------
if (ldr_testmode == 1) {
  PrintLdrVals();
  delay(150);
  
  if (ldr_reading < 30) {
    digitalWrite(12, HIGH);
  } else{
    digitalWrite(12, LOW);
  }
  
}
// -----------------------------------------


}
// ---------------------------------------------------------------END MAINLOOP------------------------------------------










// -------------------------------------------------------------------MAIN FUNCTIONS----------------------------------------!!!!!!!!!!!!

// ---------------------------------------------------------------------------PRINT SONAR VALS---------
void PrintSonarVals()
{
  digitalWrite(13, HIGH); // (led on)
  
  // -------put values in 'sonar_vals[]' if > 0-------
  x = 0;
  
  while (x < SONAR_NUM) {
    delay(getvaluedelay);
    tempval = sonar[x].ping_in();
 
    if (tempval > 0) { // oviod 0's, seems to randomly get them 
      sonar_vals[x] = tempval;
    }
    
    x = x + 1;
  }
  
  //--------------------------------------------     
  // --------------print 'sonar_vals[]'-----------------
  Serial.print("Sonar:"); 

   x = 0;

   while (x < SONAR_NUM) {
     Serial.print(" ");
     Serial.print(x + 1);
     Serial.print("=");
     Serial.print(sonar_vals[x]);
     
     
     analogWrite(11, sonar_vals[0]);
     
     
     x = x + 1;
  }
  
  Serial.println(""); 
  // -----------------------------------------------
  digitalWrite(13, LOW); 
} 
  



// ---------------------------------------------------------------------------PRINT LDR VALS------
void PrintLdrVals()
{
  digitalWrite(13, HIGH); 
    
  ldr_reading = analogRead(ldrpin); //max is 1023
  ldr_reading = ldr_reading / 2; //half the value.
  
  if (ldr_reading > 255){
    ldr_reading = 255;
  }
  // cheeky way of makeing the ldr 'more sensetive' and a good range.

  
  Serial.print("LDR: "); 
  Serial.print(ldr_reading); //print reading
  Serial.println("");
  
  digitalWrite(13, LOW); 
}

  
  

// -----------------------------------------END MAIN FUNCTIONS--------------------------------------
