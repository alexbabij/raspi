#The will take the lowest unique available number i.e., if a-2.txt, a-3.txt exists, it will make a-1.txt instead of a-4.txt
import os
import time
#import time

def writeFile(vehicle,data,fileCreated=False,filePath=""):
#If the file is created during this session we want to write to it, so the first time we run the functoin, we want to create the file,
#we then want to continue to write to the same file until we re run the entire script that calls this function (we take another set of data)
    #print("CWD:",os.getcwd())
    
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
    #print("Saving to:",os.getcwd())
    
    #curTime = time.strftime("%Y_%m_%d-%H_%M_%S")
    #ideally, we could just name our files with the current system time, which also makes it easier to sort through them, but we won't reliably have internet 
    #access, and our will most likely lose power a lot, so the system time will not be accurate.

    #We will instead use the time that is input in our data list. This is not optimal, since if the location of that entry changes, this method breaks,
    #but we already hardcoded the tuple size and data type in each position elsewhere in here, so its not that bad.

    #from: https://stackoverflow.com/questions/17984809/how-do-i-create-an-incrementing-filename-in-python
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
        #dataTime = "2005-06-08T10:34:48.283Z" = typical format
        dataTime = str(int(round(time.time(),0))) #First position of first tuple is first recorded time
        
        #This should always be unique, since we are including the milliseconds in this naming scheme, 
        #and we physically can't poll our gps faster than the resolution of the milliseconds field.
        #We still leave the unique naming function in here, just in case there is some weird case of a collision, and it makes
        #testing this without actually getting unique data much easier

        new_path=next_path(vehicle+"_"+dataTime+"-"+"%s"+".csv")
        filePath = new_path
        print("Creating new file at:",new_path)
    
        with open(new_path, "x") as file1: 
            #We include exclusive creation, even though this should never be the case with our checks
            file1.write(vehicle+"\n") #Include name of vehicle as first line
            file1.writelines([','.join(map(str,i))+'\n' for i in data]) 
            #We know what our format will be so no need to make this procedural or complicated
    
    else:

        with open(filePath, "a") as file1:
            #If we have just created this, we want to continue writing to it
            file1.writelines([','.join(map(str,i))+'\n' for i in data]) 
            

    os.chdir(cwdOrigin) #Step back out to original directory so when we rerun the function we can find data and deeper folders
    #There is definitely a better way to do this, and idk how inefficient this is
    fileCreated = True
    return filePath, fileCreated
