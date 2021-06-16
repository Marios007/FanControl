import RPi.GPIO as GPIO
from datetime import datetime, timedelta
from threading import Timer


class Fan():
   
    oneHour = 3600
    twoHours = 7200

    def fanOn(self, timer):
        print("Fan ON with Timer")
        GPIO.output(12, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        print(timer)
        self.setOffTimer(timer)
        

    def fanOff(self):
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)
        try:
            self.t2.cancel()
        except:
            return
        

    def setStatus(self, status, time):
        if status == 0:
            return 'FAN is OFF'
        if status == 1:
            timestamp = self.getTimeStamp(time)
            return ('FAN is ON until ' + timestamp)
        if status == 2:
            return ('FAN is ON from 5:00 to 6:00 ')
        

    # get timespamp + delta time
    def getTimeStamp(self, delta):
        min_added = delta / 60
        addDeltaTime = datetime.now() + timedelta(minutes=min_added)
        addDeltaTime = addDeltaTime.strftime("%H:%M")
        return addDeltaTime

    def setOnTimer(self, hour, duration):
        now = datetime.today()
        startTimeTmr = now.replace(day=(now.day)+1, hour=hour, minute=0, second=0)
        startTimeToday = now.replace(hour=hour, minute=0, second=0)
        sec_till_start = 0
        
        if now.hour >= 5:
            print('>5')
            sec_till_start = (startTimeTmr- now).total_seconds()
            print(sec_till_start)

        if now.hour < 5:
            print('<5')
            sec_till_start = (now-startTimeToday).total_seconds()
            print(sec_till_start)
            
        self.t2 = Timer(sec_till_start, self.fanOn, [sec_till_start+duration])
        self.t2.start()
        

    def setOffTimer(self, timer):
        
        self.t1 = Timer(timer, self.fanOff)
        print("Off Timer startet: " + str(timer) )
        self.t1.start()
        


    def __init__(self):
        print('fan init')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)
