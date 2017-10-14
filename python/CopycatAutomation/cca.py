import sys
import time
import serial #--------NOTE: changed 'ser.is_open', To: 'ser.isOpen()'.. (Difrence In Version.)

import cservo
#------------------------------------------------------------------------------------------------


global ser
ser = ""


global usr_servo_id
global usr_pots_id


#------------------------------------------------------------------
#------user map pots to servos:
usr_pots_id  =  [1, 2]
usr_flip_pots = ["n", "n"] #TODO.

usr_servo_id = [5, 6]
#------------------------
usr_analog_max = 760 #sets the highest analog value for 180. (max 1023) (senstity.)


#------------------------------------------------------------------




#------------------------------------------------------------------------------------------------
def do_quit():
	
    global ser
	
    print("\nExiting...")
	
    if not ser == "": #if its been asigned.
        if ser.isOpen() == True:
            ser.close()
        
        
    cservo.do_close()
        
    time.sleep(500 / 1000.0) #time to disconnect, and cservos thread to end.
	
    quit()
#------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------
def try_connect(device_path, baud_rate):
	
    global ser

   
    try:
        ser = serial.Serial(device_path, baud_rate, timeout=1.01)  # open serial port
    except:
		return (-1, "") #failed to connect.
		
 
    if not ser.isOpen() == True:
        return (-1, "") #cant open port.
    
    #------connected--- 

    time.sleep(2) #give device a little time before sending data.
    #note: only seems to work with 2 sec delay.
    
   
    
    err_code1 = do_send("get /info")       

    if not err_code1[0] == 0: 
        ser.close() 
        return (-2, "")#connected, but to wrong device.
    
    
  
       
    return (0, str(err_code1[1])) #return 0, device name.
#------------------------------------------------------------------------------------------------    



#------------------------------------------------------------------------------------------------    
def do_set_amax(analog_max_val): #ajust sensetivity of pots.
	
    if analog_max_val < 100:
        return -1 #to small
        
    if analog_max_val > 1023:
        return -2 #to large   
	
    #--------------set analog max map in device-----------
    err_code = do_send("do /amax=" + str(analog_max_val)) 
            
    if not err_code[0] == 0:  
        return -3
        
    res_line = err_code[1]
    
    new_d_amax = 0
    if res_line[0:12] == "analog max: ":
        res_line = res_line[12:] #res_line.replace("analog max: ", "")
        new_d_amax = res_line
        try:
            new_d_amax = int(new_d_amax)
        except:
            return -4
            
    if not new_d_amax == analog_max_val:
        return -4
		 
    return 0 #all good
#------------------------------------------------------------------------------------------------    



#------------------------------------------------------------------------------------------------  
def do_write_lines(full_arr, file_name):
	
    err_code = 0
    
    try:
		
        with open("./" + file_name, "w") as myfile:
            for line_count in range(0, len(full_arr)):
                myfile.write(str(full_arr[line_count]) + "\r\n")
                
    except:
		
        err_code = -1 #error ocurd.                      
                
    #---------------------------------
    full_arr = [] #clear large array.
    return err_code
#------------------------------------------------------------------------------------------------  
 


#------------------------------------------------------------------------------------------------ 
def show_examples():
	
		
    print("\nExamples:\n")
       
    print(" * [P]lay A Routine File:")
    print(" " + str(sys.argv[0]) + " -p:'/save_file.ext' ")
    print("")
        
    print(" * Control Robot And Record A Routine Useing Standard [R]eal-[T]ime Technique:")
    print(" " + str(sys.argv[0]) + " -rt d:'/dev/USBTTL0' s:'/save_file.ext'")
    print("")
    
    print(" * Control Robot And Record A Routine Useing [S]top-[M]otion Technique:")
    print(" " + str(sys.argv[0]) + " -sm d:'/dev/USBTTL0' s:'/save_file.ext'")
    print("")
        
    print(" * [M]onitor All Potentiometer Values:")
    print(" " + str(sys.argv[0]) + " -m d:'/dev/USBTTL0'")
    print("")

    print(" * [T]est The Device:")
    print(" " + str(sys.argv[0]) + " -t d:'/dev/USBTTL0'")
    print("")
    
    return 0
#------------------------------------------------------------------------------------------------ 



#------------------------------------------------------------------------------------------------    
def parse_commands():
	          
    if len(sys.argv) == 3 or len(sys.argv) == 4:
		
        program_mode = ""
        program_dev_path = ""
        program_save_path = ""
        
		#----------------------------------------
        for x in range(1, len(sys.argv)):
            sys.argv[x] == str(sys.argv[x])
            sys.argv[x] == sys.argv[x].strip()
            sys.argv[x] == sys.argv[x].lower() #lower case.

            cur_arg = sys.argv[x]
            cur_arg = cur_arg.replace('"', '') #remove "
            
            #----find program mode:
            if cur_arg == "-rt":
                program_mode = "rt"
                
            if cur_arg == "-sm":
                program_mode = "sm"
                
            if cur_arg == "-m":
                program_mode = "m"  
                
            if cur_arg == "-t":
                program_mode = "t" 
                
            if cur_arg[0:3] == "-p:":
                program_mode = "p" 
                
            #----find device path:   
            if cur_arg[:2] == "d:":
                program_dev_path = cur_arg[2:]
                
            #----find save file: 
            if cur_arg[:2] == "s:":
                program_save_path = cur_arg[2:]
        #----------------------------------------
		
        #-----------------------
        if len(program_mode) == 0:
            show_examples()
            do_quit()
		
        if len(program_dev_path) == 0:
            show_examples()
            do_quit()
		
        if program_mode == "rt":
            if len(program_save_path) == 0:
                show_examples()
                do_quit()
                
        if program_mode == "sm":
            if len(program_save_path) == 0:
                show_examples()
                do_quit()
    #----------------------------------------        
    else:
		
        show_examples()
        do_quit() 	
    #----------------------------------------
			
    if program_mode == "m":
        return (program_mode, program_dev_path)
    else:
        return (program_mode, program_dev_path, program_save_path)
#------------------------------------------------------------------------------------------------    


  
#----------------------------------------------------------------------------
def do_send(send_line):
	
    global ser
    
    #-------------------------------
    if ser.isOpen() == False:
        return (-1, "") #ser not open.
        
    send_line = str(send_line)
    send_line = send_line.strip()
     
    if len(send_line) < 1:
        return (-2, "") #no data to send.
    #--------------------------------           

    try:
        ser.write(send_line + "\r\n")    # write the string.
    except:
        return (-3, "")
	
    time.sleep(1 / 1000.0) #wait for data to reach device.
        
        
    in_line = "" #data from device.
    out_line = "" #line to return from device.
    line_timeout = 0
        
    #----------------------------------------------------------------------------------
    while not in_line[0:10] == "=!=done=!=": #last line must be read to read all buffer. 
 
        if line_timeout > 10: #done line sould always be < 10 lines in.
            return (-4, "") #line timeout/non-vailid command to device.
        else:
            line_timeout = line_timeout + 1
        
        #---------------
        try:
            in_line = ser.readline()
            in_line = in_line.lower() #convert all to lower case.
            in_line = in_line.strip()
            in_line = str(in_line)
        except:
            #print("Error In Reciving/Decodeing The Data From Device!")
            return (-5, "")
			
        if in_line[0:5] == "=!v!=": #extract the line where intrested in.
            out_line = str(in_line[5:])

    #----------------------------------------------------------------------------------
    return (0, out_line)
#----------------------------------------------------------------------------
	
	
		
#------------------------------------------------------------------------------------------------  
def do_device_test():


    total_time = 0
    av_time = 0
    min_time = 999999999
    max_time = 0
    
    readings_per_set = 0
    
    print("")
    print("  - Running Device Test...") 

    for x in range(1, 200):
		
        time_start = int(round(time.time() * 1000)) #capture current ms.
   
        vals_arr = do_send("get /values") 
        
        if not vals_arr[0] == 0:
            print("There Was An Error Getting A Set Of Readings!")
            return -1
            
        pot_vals = str(vals_arr[1])
        pot_vals = pot_vals.replace(" ","") #remove spaces.
        pot_vals = pot_vals.lower()
        
        if pot_vals[:7] == "values:":
            pot_vals = pot_vals.replace("values:","")
            pot_vals = pot_vals.split(",")
            readings_per_set = len(pot_vals)
        else:
            return -2
			
            
        time_end = int(round(time.time() * 1000)) #capture current ms.
   
        time_taken = time_end - time_start
        total_time = total_time + time_taken

        if time_taken < min_time:
            min_time = time_taken
            
        if time_taken > max_time:
            max_time = time_taken   
            
    av_time = total_time / 200
    
    print("")  
    print("  ! Test Complete:\n")
    print("  - Total Reading Sets: 200")
    print("  - Readings Per Set: " + str(readings_per_set))
    print("  - Total Readings: " + str(200 * readings_per_set))    
    print("  - Total Time Taken: " + str(total_time) + "ms")   
    print("  - Avrage Time Taken: " + str(av_time) + "ms")   
    print("  - Minimun Time Taken: " + str(min_time) + "ms")  
    print("  - Maximun Time Taken: " + str(max_time) + "ms")     
    print("  - Avrage Time For 1 Reading: " + str(av_time / readings_per_set) + "ms") 
    
    return 0
    
    
#------------------------------------------------------------------------------------------------  



#------------------------------------------------------------------------------------------------    
def do_main(mode, save_path):
	

    global usr_servo_id #defined at top
    global usr_pots_id #defined at top


    
    routine_save_arr = ["linespeed=50"] #first line off full file in array.
    
    print("")
    
    try:  #used for detecting ctrl-c.

        #time.sleep(2) #needed before we send data succsessfully.

    
        print("  - Ready To Record.")
        tmp = raw_input("  ! Press Enter To Start Recording, Ctrl-C To Stop...")
        tmp = ""
        print("____________________________________________________________")
        
        while 0 == 0: #every set of values.
			
			
            if mode == "sm": #'stop-motion' mode.
                tmp = raw_input("Press Enter To Capture Position.")
                
                
            time_start = int(round(time.time() * 1000)) #capture current ms.
            #----------------------------------------------------------------
			
            vals_arr = do_send("get /values") 
             
            pot_vals = str(vals_arr[1])
            pot_vals = pot_vals.replace(" ","") #remove spaces.
            pot_vals = pot_vals.lower()
            pot_vals = pot_vals.replace("values:","")
            
            pot_vals = pot_vals.split(",") #turn into array, separating on ','. NOTE: pot_vals is always a string.
        
            routine_line = "move"
            #-------------------------------------------
            for x in range(0, len(usr_servo_id)):
                routine_line = routine_line + " s" + str(usr_servo_id[x]) + "=" + str(pot_vals[usr_pots_id[x] - 1] )
            #-------------------------------------------
            
            if mode == "rt" or mode == "sm": #allow moveing of servos.      
                try:
                    cservo.do_move(routine_line[5:]) #call to cservo libary to move servos! (skip 'move ')
                except:
                    pass
            #-------------------------------------------
            routine_save_arr.append(str(routine_line)) #add the line to the full list.
            
            time_finish = int(round(time.time() * 1000)) #capture current ms.
            #----------------------------------------------------------------
            
            time_taken = time_finish - time_start
                
                
            print("  [" + str(len(routine_save_arr)-1) + "] - '" + str(routine_line) + "' . [Taken:" + str(time_taken) + "ms]")
                
                
            if time_taken < 50:
				
                delay_ballance = 50 - time_taken
                time.sleep(delay_ballance / 1000.0) #-----so each loop takes exacly 50ms.
                
            else:
            
                print("Warning: Device Taken To Long To Return Readings! Needs To Be Less Than 50ms.")



    #-----------------------------------------------------------------------------------
    except: #ctrl-c was pressed.
		
        print("\n____________________________________________________________")
        
        print("\n  Ctrl-C Hit. Recording Stopped.\n")

        
        
        if len(save_path) > 0:
			
            print("  - Saveing...")
            
            save_err_code = do_write_lines(routine_save_arr, save_path)
            
            if save_err_code == 0:
                print("  ! File: '" + save_path + "' Writen " + str(len(routine_save_arr)) + " Lines. Ok!")
            else:
                print("  ! FAILED TO SAVE.")
        #----------------------
        
        routine_save_arr = [] #clear large array. 
         
        
    return 0
	
	
	
#------------------------------------------------------------------------------------------------    









#--------------------------------------------START MAIN CODE (End of main funtions)---------------------------------------







#------------------------error check user varibales---------------


if not len(usr_servo_id) == len(usr_pots_id):
    print("Error: usr_servo_id and 'usr_pots_id' Are Not The Same Lengths!\nEvery Servo Has To Be Assined A Pot ID.")
    do_quit()



#---------both len are equel----------

for x in range(0, len(usr_servo_id)):
	
    #-------usr_servo_id:
    if usr_servo_id[x] > 16:
        print("Error: PCA Contoler Only Suppots 16 Servos.")
        do_quit()
        
    if usr_servo_id[x] <= 0:
        print("Error: Servo ID's Start At 1.")
        do_quit()        
    
        
    #-------usr_pots_id:
    if usr_pots_id[x] > 16:
        print("Error: This Software Only Supports Upto 16 Pot ID's.")
        do_quit()
        
    if usr_pots_id[x] <= 0:
        print("Error: Pot ID's Start At 1.")
        do_quit() 

#-----analog max----


if usr_analog_max > 1023:
    print("Error: Analog Max Has A Maxumum Of 1023.")
    do_quit()	

if usr_analog_max < 10:
    print("Error: Analog Max Has A Minumum Of 10.")
    do_quit()	

#---------------------------------------------------------------------------------






#--------ok



main_commands = parse_commands() #checks its valid too.


#------------------------------------------------------------------
print("\n = Minibot Started = \n")


#-----------------connect to device------------
print("Connecting To: " + main_commands[1] + "...")

con_err_code = try_connect(main_commands[1], 115200)

if not con_err_code[0] == 0:
    print("Failed To Connect To: " + str(main_commands[1]) + " @ 115200 Baud.")
    do_quit()
      
dev_name = con_err_code[1]

print("Connected, Device Name: '" + dev_name + "'.")


#---------------set analog max-------------------
print("Setting Analog Max Sensetivity To: " + str(usr_analog_max) + ".")

a_max_err_code = do_set_amax(usr_analog_max) #set analog max.


if not a_max_err_code == 0:
    print("Error Setting Analog Max!")
    do_quit()



#--------------start main function---------------


if main_commands[0] == "rt": #"realtime"	
    cservo.do_init()
    do_main("rt", main_commands[2]) #rt and save path.

if main_commands[0] == "sm": #"stop-motion"	
    cservo.do_init()
    do_main("sm", main_commands[2])

if main_commands[0] == "m": #"monitor"	
    do_main("m", "")

if main_commands[0] == "t": #"test"	
    do_device_test()

#-------------------------------------------------


do_quit()










