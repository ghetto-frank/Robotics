import Adafruit_PCA9685 # Import the PCA9685 module.
import time
import threading #threads usly take 0-1ms to start, however can take upto 4.
import os 
#-------------------------


module_ver = "1.beta"

global thread_rf #for thread_run_file, used in quick_stop & run_file.
#-----------



global servo_min_pl
global servo_max_pl

global servospins
global servosflip
global servosoffset
global servosmin
global servosminax


#----Servos-------------------------------------------------------------------------------------------------------------------

servo_min_pl = 150  # Min pulse length out of 4096
servo_max_pl = 600  # Max pulse length out of 4096

#              1    2    3    4    5    6    7     8     9     10   11   12   13   14   15   16
servospins = ["4", "5", "7", "0", "1", "3", "12", "14", "15", "8", "9", "11"] #Servo ID (1-16) matching to PCA Pinouts (0-15).
servosflip = ["n", "n", "n", "n" ,"n", "n", "n",  "n",  "n",  "n", "n", "n"] #Flip the values

#-----Servo offsets, here you can plus or minus to the servo values. 
#     NOTE: the 'offset' command will override the deafuls here. servosmin and servosmax still apply!
servosoffset = [ "0", "0", "0", "0", "0", "0", "0",  "0",  "0",  "0", "0", "0"] #NEW

servosmin = [ "0", "0", "0", "0", "65", "0", "0",  "0",  "0",  "0", "0", "0"] #Hard Limiting!!!
servosmax = [ "180", "180", "180", "180", "180", "180", "180",  "180",  "180",  "180", "180", "180"]

#-----------------------------------------------------------------------------------------------------------------------------






for x in range(0, len(servospins)):
    try:
        servospins[x] = int(servospins[x])
        servosmin[x] = int(servosmin[x])
        servosmax[x] = int(servosmax[x])
        servosoffset[x] = int(servosoffset[x]) #NEW
    except:
        print("ERROR: Cant Convert User Varibales To Intergers/Non Equal Lengths!\n  Check 'User Varibales' Code Section.")
        do_quit()






#=========================Start Main Funtions======================



#--------------------------------------------------------------------------------------------
def do_stop():
	
    global th_stop
    th_stop = 1 #stop after routine.
    
    return 0
#--------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------
def do_quickstop():
	
    global thread_rf #thread_run_file thread (used for join.)
    global th_stop
    
    th_stop = 2 #stop imedently (return from thread).
    
    thread_rf.join() #join thread (halt) till thread terminate.
    
    #for x in range(0, 2000): #2 second time out.
        #time.sleep(1 / 1000.0)
        #if get_status[0] == 1: #return when ready for next routine.
            #return 0
    
    return -1
#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------
def set_status(status, file_path, run_speed, run_count): #not realy for user call.

    global main_status
    
    try:
        main_status = [int(status), str(file_path), int(run_speed), int(run_count)] 
        #status, file path, run speed, run count
        #status: 0=initing 1=ready 2=loading 3=playing.
    except:
        return -1
        
    return 0
#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------
def get_status():

    global main_status
    
    return main_status
#--------------------------------------------------------------------------------------------



#--------------------------------------------------------------------------------------------
def do_quit():
	
    do_quickstop() 
    
    quit()
    
    return 0
#---------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------
def do_init():
	
    global pwm
    
    set_status(0, "", 0, 0) #status = initing.
    
    
    #---------asign lib----------
    try:
        pwm = Adafruit_PCA9685.PCA9685()
        pwm.set_pwm_freq(60)
    except:
        print("Error Initialising The PCA9685 Lib.")
        do_quit()
    #----------------------
        
    time.sleep(10 / 1000.0)
    
    set_status(1, "", 0, 0) #status = ready.

    return 0        
#----------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------
def run_file(file_path, run_speed, run_count):
	
    global thread_rf

    cur_state = get_status()
    if cur_state[0] <> 1: #check is ready.
        return -1

    if run_speed < 0 or run_speed > 60000:
        return -2 #Run speed out of range.
        
    if run_count < 1 or run_count > 600000:
        return -3 #Run count out of range.  
	
	
    #---------check file-----------	
    if not os.path.isfile(file_path): 
        return -4 #File dose not exist.
      
    
    set_status(2, "", 0, 0) #status = loading

    
    #---------start thread--------
    try:
        thread_rf = threading.Thread(target=thread_run_file, args=(file_path, run_speed, run_count,))  # need extra ','
        thread_rf.start()
    except:
        print("Error Starting Thread!")
        return -5
    #------------------------------  

    return 0 #all good.
    
#----------------------------------------------------------------------------------------------




#----------------------------------------------------------------------------------------------
def thread_run_file(file_path, run_speed, run_count): #not realy for user call.
	
    global th_stop
    
    th_stop = 0
    
    for x in range(0, run_count): #looping routine file.
			
			
        if th_stop == 1: #stop after the routine.
            set_status(1, "", 0, 0) #status = ready  
            return

        set_status(3, file_path, run_speed, run_count - x) #status = playing

        #--------------------
        main_file = open(file_path) #load file into memory.
        #----------------------------------------------------------------------------------------------
        for file_line in main_file:

            if th_stop == 2: #stop imedently.
                set_status(1, "", 0, 0) #status = ready   
                return
                

            file_line = file_line.strip() #remove line endings.
            file_line = file_line.lower()
                
        
            # ----------------------------------look for 'linespeed=' line--------------------------
            if run_speed == 0: #no run speed set so let file set it.
					
                if file_line[:10] == "linespeed=":  
  
                    try:
                        run_speed = int(file_line[10:])
                    except:
                        print(" Error on Line:" + str(line_count) + " Integer:" + str(file_line[10:]) + ".")
          
                    if not run_speed >= 10 and not run_speed <= 100000:
                        print(" ERROR: lineSpeed should be between 10 and 100000 Miliseconds..Setting to 50ms..")
                        run_speed = 50
            # -------------------------------------------------------------------------------------
	 
	 
            # -----------------------------------look for 'sleep=' line----------------------------
            if file_line[:6] == "sleep=":   
		  
                try:
                    onesleep = int(file_line[6:])
                except:
                    print("Error on Line:" + str(line_count) + " Integer:" + str(file_line[6:]) + ".")
                #--------------POTENTAL ERROR
                if onesleep > 20 and onesleep < 10000:
                    print("   * Waiting for:" + str(onesleep) + "ms...")	
                    time.sleep(onesleep / 1000.0)
                else:
                    print("Error: sleep should be between 20 and 10000 Miliseconds..")
            # ----------------------------------------------------- -------------------------------
	 
	 
            # ------------------------------------look for 'move' line-----------------------------
            if file_line[:5] == "move ":
					
                time.sleep(run_speed / 1000.0) #sleep for required ammount of time.
                do_move(file_line[5:])  #apears to still keep this fuction running under the current thread.
            # ----------------------------------------------------- -------------------------------
                
    set_status(1, "", 0, 0) #status = ready                   
    return
#----------------------------------------------------------------------------------------------




#---------------------------------------------------Move Servos Function!!!-----------------------------------------
def do_move(strline):  #example: 's1=33 s2=180 s4=33'....

        
    #global pwm #----servo lib


    allcmds = strline.split(" ")
        
        
    for z in range(0, len(allcmds)):
        
        rawcmds = allcmds[z].split("=") # Splits on an '='
      
        servonum = rawcmds[0] # first half will always be servonumber
        servonum = servonum[1:] # get rid of 's' char
          
        #----------servo number:----------
        try:
            servonum = int(servonum)
        except ValueError:
            print("  ! Error in Servo Number, Got:" + str(servonum) + ".\n")
            break
             
        if servonum > len(servospins) or servonum <= 0: #equal or less than 0
            print("  ! Error, Servo Number:" + str(servonum) + " Out Of Range!")
            break

        #-----------servo position:------
        try:
            servopos = int(rawcmds[1]) # second half of that '='
        except ValueError: 
            print("  ! Error in Servo Position Number!\n")
            break  
        #------------------------------------------------------   
             
             
        #---------------Flip Vaule?-----------
        if servosflip[servonum - 1] == "y":  #--FLIP THE VAULES IF NEEDED--
            servopos = servopos - 180
            if int(servopos) < 0: # must have unwanted - sign
                servopos = str(servopos) # Needed to remove - as string
                servopos = servopos[1:] # Removes '-' sign
                servopos = int(servopos) # back to int vaule. 
            else:
                servopos = 0
        #----------------------------------------
          
          
        #-----------------Servo Offset handeling:------
        if servosoffset[servonum - 1] <> 0: #not 0 so apply offset.
               
            if servosoffset[servonum - 1] < 0: #then minus with this value
                current_servo_offset = str(servosoffset[servonum - 1])
                current_servo_offset = current_servo_offset[1:]  # Removes '-' sign
                servopos = servopos - int(current_servo_offset) # apply - offset
            else: #plus a value
                current_servo_offset = int(servosoffset[servonum - 1])
                servopos = servopos + current_servo_offset
        #----------------------------------------------
           
          
        #---------------Check servopos is within limits-----------
        if servopos > servosmax[servonum - 1]: # -1 Becaulse Arrays start at 0 wharas servo nums at 1.. 
            print("  ! Error, Servo:" + str(servonum) + " Has A Maxamum Of:" + str(servosmax[servonum - 1]) + ", Got:" + str(servopos) + " (with offset:" + str(servosoffset[servonum - 1]) + ")")
            break
             
        if servopos < servosmin[servonum - 1]:
            print("  ! Error, Servo:" + str(servonum) + " Has A Minimum Of:" + str(servosmin[servonum - 1]) + ", Got:" + str(servopos) + " (with offset:" + str(servosoffset[servonum - 1]) + ")")
            break     
        #---------------------------------------------------------

   
        servopulse = ((servopos * (servo_max_pl - servo_min_pl)) / 180) + servo_min_pl #Convert degrees to pulse width
   

        #--------we have what we need. move servo command---------
        print("  - Servo:" + str(servonum) + " (Pin:" + str(servospins[servonum - 1]) + ") To:" + str(servopos) + " (Pulsewidth:" + str(servopulse) + " Flipped:" + servosflip[servonum - 1] + " Offset:" + str(servosoffset[servonum -1]) + ")")
        pwm.set_pwm(servospins[servonum - 1], 0, servopulse) # Move Servo

    return 0
#----------------------------------------------------------------------------------------------------------------
    
    
    

#=========================Finished Main Funtions======================





do_init()

print(" [cservo v" + str(module_ver) + " loaded.]")

