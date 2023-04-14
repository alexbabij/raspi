#The will take the lowest unique available number i.e., if a-2.txt, a-3.txt exists, it will make a-1.txt instead of a-4.txt
import os

L = [['t1',1],['t2',2],['t3',3]]
fileCreated = False
data = L
vehicle = "car1"
data2 = [['t4',4],['t5',5],['t6',6]]


def writeFile(vehicle,data,fileCreated=False,filePath=""):
#If the file is created during this session we want to write to it, so the first time we run the functoin, we want to create the file,
#we then want to continue to write to the same file until we re run the entire script that calls this function (we take another set of data)
    print("CWD:",os.getcwd())
    
    #Check if directory for vehicle exists and if not, create it
    #Changing directory is not limited to the function scope, so we need to reset it when we are done, or else it won't
    #find our data folder that already exists
    cwdOrigin = os.getcwd()

    if not os.path.isdir(os.getcwd()+"/data"):
        os.makedirs("data")
        print("Created directory \"data\"")

    os.chdir(os.getcwd()+"/data")

    #at this stage, cwd should be in data folder
    if not os.path.isdir(os.getcwd()+"/"+vehicle): #evaluates to false if dir doesn't exist
        os.makedirs(vehicle)
        print("Created directory \""+vehicle+"\"")


    os.chdir(os.getcwd()+"/"+vehicle) #Put each vehicle's data in its own folder
    print("Saving to:",os.getcwd())

    def next_path(path_pattern):
        """
        Finds the next free path in an sequentially named list of files

        e.g. path_pattern = 'file-%s.txt':

        file-1.txt
        file-2.txt
        file-3.txt

        Runs in log(n) time where n is the number of existing files in sequence
        """
        i = 1

        # First do an exponential search
        while os.path.exists(path_pattern % i):
            i = i * 2

        # Result lies somewhere in the interval (i/2..i]
        # We call this interval (a..b] and narrow it down until a + 1 = b
        a, b = (i // 2, i)
        while a + 1 < b:
            c = (a + b) // 2 # interval midpoint
            a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

        return path_pattern % b

    if not fileCreated:
           
        new_path=next_path("a-%s.txt")
        filePath = new_path
        print(new_path)
    
        with open(new_path, "x") as file1: 
            #We include exclusive creation, even though this should never be the case with our checks
            file1.write(vehicle+"\n") #Include name of vehicle as first line
            file1.writelines([i[0]+','+str(i[1])+'\n' for i in data]) 
            #We know what our format will be so no need to make this procedural or complicated
    
    else:

        with open(filePath, "a") as file1:
            #If we have just created this, we want to continue writing to it
            file1.writelines([i[0]+','+str(i[1])+'\n' for i in data]) 
            

    os.chdir(cwdOrigin) #Step back out to original directory so when we rerun the function we can find data and deeper folders
    #There is definitely a better way to do this, and idk how inefficient this is
    fileCreated = True
    return filePath, fileCreated

print("0cwd",os.getcwd())
filePath, fileCreated = writeFile(vehicle,data,fileCreated,"") #the first time we run it, filePath should be ignored by function
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