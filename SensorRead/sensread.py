import sys
import time
import threading
import serial #--------NOTE: changed 'ser.isOpen()', To: 'ser.is_open'.. (Difrence In Version.)

global ser #out serial lib.
ser = "" #to avid not asined error.

global th_get_sensor #main thread to get the values.
global thread_run #allow thread to run if 1.
thread_run = 0


global sonar_values
global ldr_values
    
    
sonar_values = [0, 0, 0, 0, 0, 0, 0, 0]
ldr_values = 0




#------------------------------------------------------------------------------------------------
def do_connect(device_path, baud_rate):
	
    global ser

   
    try:
        ser = serial.Serial(device_path, baud_rate, timeout=1.0)  # open serial port
    except:
        return (-1, "") #failed to connect.
		
 
    if not ser.is_open == True:
        return (-2, "") #cant open port.
    
    #------connected--- 

    time.sleep(2) #give device a little time before sending data.
    #note: only seems to work with 2 sec delay. 
   
    
    err_code1 = do_send("get /info")       

    if not err_code1[0] == 0: 
        ser.close()
        return (-3, "")#connected, but to wrong device.
    
   
    return (0, str(err_code1[1])) #return 0, device name.
#------------------------------------------------------------------------------------------------    



#------------------------------------------------------------------------------------------------    
def is_connected():
	
    global ser
	
    if ser == "": #not yet asined.
        return False	
	
    if ser.is_open == True:
        return True
    else:
        return False
#------------------------------------------------------------------------------------------------    

    

#------------------------------------------------------------------------------------------------   
def do_send(send_line):
	
    global ser
    
    #-------------------------------
    if ser.is_open == False:
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
            print("Error In Reciving/Decodeing The Data From Device!")
            return (-5, "")
			
        if in_line[0:5] == "=!v!=": #extract the line where intrested in.
            out_line = str(in_line[5:])

    #----------------------------------------------------------------------------------
    return (0, out_line)
#------------------------------------------------------------------------------------------------   



#------------------------------------------------------------------------------------------------  
def thread_get_values():
	
    global sonar_values
    global ldr_values
    
    global thread_run
    
    
    thread_run = 1
    while thread_run == 1:
		
        
        #------put sonar values into sonar_values[] array-------
        sonar_err = do_send("get /sonar")
    
        if sonar_err[0] <> 0:
            return -1
        
        sonar_tmp = sonar_err[1]
        sonar_tmp = sonar_tmp.replace("sonar:", "")
        sonar_tmp = sonar_tmp.replace(" ", "")
	
        sonar_tmp = sonar_tmp.split(",")	
        
        for x in range(0, len(sonar_tmp)):
            sonar_values[x] = int(sonar_tmp[x])
            
            
        #------put ldr values into ldr_values[] array-------
        ldr_err = do_send("get /ldr")
    
        if ldr_err[0] <> 0:
            return -1
        
        ldr_tmp = ldr_err[1]
        ldr_tmp = ldr_tmp.replace("ldr:", "")
        ldr_tmp = ldr_tmp.replace(" ", "")
	
        ldr_values = int(ldr_tmp)

        #print(sonar_values)
        #print(ldr_values)
        
    #=====Closeing Thread=====    
    for x in range(0, len(sonar_values)): #reset values, keeping length
        sonar_values[x] = 0
		
    ldr_values = 0
    return
#------------------------------------------------------------------------------------------------ 
	


#------------------------------------------------------------------------------------------------ 
def update_sensors(on_off):
	
    global thread_run
    global th_get_sensor #main thread to get the values.

    if is_connected() == False:
        return -1 #no device connected.

    #------------------------------
    
    if on_off == True:
		
        if is_live() == True:
            return -2 #thread already running.
		
        th_get_sensor = threading.Thread(target=thread_get_values)
        th_get_sensor.start()
        
        for time_out in range(0, 2000): #wait 2sec till thread is getting data to return.
            time.sleep(1 / 1000.0)
            if is_live() == True:
                return 0
                
        return -3 #timed out waiting for thread to return data.
        
    else:

        thread_run = 0 #force thread to close.
        th_get_sensor.join() #join the thread to return when actualy closed.
        
        return 0
#------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------
def is_live():
	
    global thread_run

    if is_connected() == False:
        return False

    total_vals = 0
    for x in range(0, len(sonar_values)):
        total_vals = total_vals + sonar_values[x]
	
	
    if thread_run == 1 and total_vals > 0:
        return True
    else:
        return False
	
#------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------    
def do_led_on(on_off):
	
    if is_live() == True:
        update_sensors(False)
	
	
    if on_off == True:
        err_code = do_send("led /on")
    else:
        err_code = do_send("led /off")	

    if is_live() == False:
        update_sensors(True)

    if err_code[0] == 0:
        return 0
    else:
        return -1
#------------------------------------------------------------------------------------------------    


      
#------------------------------------------------------------------------------------------------          
def do_sonar_minmax(Min_Max, sensorNum_sensorValue):

    if is_live() == False:
        return -1 #not live.

    print(sonar_values)


    #----------------------get minimium sensor number---------------------
    tmpfourvals = [0,0,0,0] #4 for now. (left, right, top, bottom)
    for x in range(0, 4):
        tmpfourvals[x] = sonar_values[x] #capture values (make sure values dont chenge)
  
    print(tmpfourvals)
    
    if Min_Max.lower() == "max":
        tmp_val = max(tmpfourvals, key=float)
    else:
        tmp_val = min(tmpfourvals, key=float) #get minimum single int in the list
 
    print("DEBUG TMP VAL :" + str(tmp_val))
    if sensorNum_sensorValue.lower() == "sensornum": #look for maxval in list
		
        for x in range(0, len(tmpfourvals)):
            if tmpfourvals[x] == tmp_val: #look for what value 
                interest_sensor = x + 1
                print("DEBUG HERE. " + str(x))
                return interest_sensor
        return -1 #no such value in list??
    
    return tmp_val
#------------------------------------------------------------------------------------------------    


























def debug_test():

    tr = do_connect("/dev/ttyUSB0", 115200)
    print(tr)

    update_sensors(True)

    for x in range(0, 20):
        print(sonar_values)
        time.sleep(200 / 1000.0)
    


    print(do_led_on(True))



    for x in range(0, 20):
        print(sonar_values)
        time.sleep(200 / 1000.0)
    


    print(do_led_on(False))



    update_sensors(False)



def debug_start():
	

    tr = do_connect("/dev/ttyUSB0", 115200)
    print(tr)

    update_sensors(True)


print(" [sens loaded v1.beta]\n")
