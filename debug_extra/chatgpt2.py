import threading
import requests
import time



session = None


def set_global_session():
    global session
    if not session:
        session = requests.Session()

myVal = [0.0, 0.0, 0.0]

initTime = time.time()
delay = 0.5
rounding = 1

class MyThread1(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        #global myVal, initTime, delay, rounding
        
        target = initTime
        testvalue = 0.0
        
        while self.running:
            testvalue += 1.0 
            start = time.time()
            target = round(target + delay, rounding)
            name = threading.current_thread().name
            print('mult1', name, time.time(), "written value:", testvalue)
            with myVal_lock:
                myVal[0] = testvalue
                myVal[1] = 1.0
                myVal[2] = 2.0
            
            diff = time.time()
            if target - diff > 0:
                time.sleep(target - diff)
    
class MyThread2(threading.Thread):
    def __init__(self): #This runs each time an instance is created, equivalent to a = 1 in "global"/top level of a script
        #__init__ is standard notation for all class stuff, self is also standard 
        super().__init__() #This means MyThread2 has been setup with the setup from threading.Thread()
        #This calls the init function of threading.Thread
        #The function __init__ is just generally called a constructor (regardless of language)
        #super().__init__() is calling the init function of the thing we passed into the class, in our case threading.Thread
        self.running = True
        self.a = 0 #self. is an object sort of that holds all the variables of the class instance i.e. self.a of thread3 will have a 
        #different value from self.a of thread2

    def addNum(self,n): #when this is called, it "automatically" passes self into itself
        #Functions in classes will always need self passed into them to have access to self.a, etc.
        self.a += n
        print(self.a)

    def run(self): 
        #global myVal, initTime, delay, rounding
        
        target = initTime
        time.sleep(0.1)
        
        while self.running:
            target = round(target + delay, rounding)
            name = threading.current_thread().name
            
            with myVal_lock:
                parmyVal = [myVal[i] for i in range(0, 3)]
                
            print('mult2', name, time.time(), "received value:", parmyVal)
            
            diff = time.time()
            if target - diff > 0:
                time.sleep(target - diff)


myVal_lock = threading.Lock()

if __name__ == "__main__":
    set_global_session()
    
    thread1 = MyThread1() #This is one instance of a class - the class and its contents is assigned/copied to the variable thread1
    thread3 = MyThread2() #This is instantiating a thread
    thread1.start()
    thread2 = MyThread2()
    thread2.addNum(3) #This is calling a function contained within the class that we assigned/gave to thread2
    thread2.start()
    thread2.addNum(3)
    thread3.addNum(2)
    
    try:
        while True:
            time.sleep(3)
            print("a")
            thread1.running = False
            thread2.running = False
            thread1.join()
            thread2.join()
            thread3.running = False
            thread3.join()
    except KeyboardInterrupt:
        print("Attempting to close threads...")
        thread1.running = False
        thread2.running = False
        thread1.join()
        thread2.join()
        thread3.running = False
        thread3.join()
        print("Threads successfully closed.")



