with open('configDevice.txt') as mycfgfile:
    config = mycfgfile.read().splitlines() #Read in each line as a list i.e. [a:1, b:2]
    config.pop(0)
    config = dict([eachLine.split(":") for eachLine in config]) 
#We are parsing the first line description at the top of the file, but its a dictionary, so we really don't care
    print(config)

    print(float(config["storage interval"]))
    print(type(float(config["storage interval"])))


from fileSave import *


L = [["2005-06-08T10:34:49.283Z",1],['t2',2],['t3',3]]
data = L
vehicle = config["current vehicle"]
data2 = [['t4',4],['t5',5],['t6',6]]

print("0cwd",os.getcwd())
filePath, fileCreated = writeFile(vehicle,data,fileCreated=False) #the first time we run it, filePath should be ignored by function
print("\n"+filePath,fileCreated)
print("1cwd",os.getcwd())
filePath, fileCreated = writeFile(vehicle,data2,fileCreated,filePath)
print("\n"+filePath,fileCreated)
print("2cwd",os.getcwd())
filePath, fileCreated = writeFile("car2",data,fileCreated=False)
print("3cwd",os.getcwd())
filePath, fileCreated = writeFile("car2",data,fileCreated,filePath)
print("4cwd",os.getcwd())
filePath, fileCreated = writeFile("car2",data2,fileCreated,filePath)
print("5cwd",os.getcwd())
