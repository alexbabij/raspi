#Running this file will collect gps data at the specified interval 


#Parsing the GPSD json:


#I have 0 idea how the threading works. All I know is that the threading constantly polls the serial connection so that the buffer doesn't overflow and we don't lose/miss data,
#BUT we can choose when we actually want to pull the data independent of this i.e. threading stuff collects data, we pull from threading stuff