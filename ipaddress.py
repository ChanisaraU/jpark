import socket    
hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)    

if IPAddr == '172.20.1.125' :
    zero = "select date_in,time_in,date_out, TIME_FORMAT(time_out, '%T') as time_out from test_log where id = 0"
else IPAddr == '172.20.1.0' :    
    one = "select date_in,time_in,date_out, TIME_FORMAT(time_out, '%T') as time_out from test_log where id = 1"
print("Your Computer Name is:" + hostname)    
print("Your Computer IP Address is:" + IPAddr)  
