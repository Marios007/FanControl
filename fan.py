import RPi.GPIO as GPIO
from datetime import datetime, timedelta
from threading import Timer

class Fan():
    oneHour = 3600
    twoHours = 7200
    statusText = "Status FAN "
    statusNightTimer = "Status Timer "
    statusFan = False


    def fanOn(self, timer):
        print("Fan ON with Timer: " + str(timer))
        GPIO.output(12, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        self.statusFan = True
        self.setOffTimer(timer)
        
    def fanOff(self):
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)
        self.statusFan = False
    
    def nightTimerOff(self):
        try:
            self.t2.cancel()
            print("night timer cancelled")
        except:
            return

    def getStatusText(self):
        return self.statusText

    def getStatusTimer(self):
        return self.statusNightTimer
        
    def setStatus(self, status, time):
        if status == 0:
            self.statusText = 'FAN is OFF'
            return self.statusText
        if status == 1:
            timestamp = self.getTimeStamp(time)
            self.statusText = 'FAN is ON until ' + timestamp
            return self.statusText
        if status == 2:
            self.statusNightTimer = 'Timer is on from 5:00 to 6:00'
            return self.statusNightTimer
        if status == 3:
            self.statusNightTimer = 'Night timer off'
            return self.statusNightTimer
        
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
            sec_till_start = (startTimeTmr- now).total_seconds()
            print(sec_till_start)

        if now.hour < 5:
            sec_till_start = (now-startTimeToday).total_seconds()
            print(sec_till_start)
        print("Set On Timer startet: " + str(sec_till_start) + " with duration " + str(duration))
        self.t2 = Timer(sec_till_start, self.fanOn, [duration])
        self.t2.start()
        

    def setOffTimer(self, timer):
        self.t1 = Timer(timer, self.fanOff)
        print("Off Timer startet: " + str(timer) )
        self.t1.start()

    def getStatusFan(self):
        return self.statusFan
        

    def __init__(self):
        print('fan init')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
        GPIO.output(12, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)
