from sensor import Sensor
import RPi.GPIO as GPIO
import os
from fan import *
from sensor import *
from logger import *
from cryptoApiLogger import *
from http.server import BaseHTTPRequestHandler, HTTPServer

host_name = '192.168.10.28'  # Change this to your Raspberry Pi IP address
host_port = 8000

oneHour = 3600
twoHours = 7200


class MyServer(BaseHTTPRequestHandler):
    """ A special implementation of BaseHTTPRequestHander for reading data from
        and control GPIO of a Raspberry Pi
    """
    
    
    def do_HEAD(self):
        """ do_HEAD() can be tested use curl command
            'curl -I http://server-ip-address:port'
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """ do_GET() can be tested using curl command
            'curl http://server-ip-address:port'
        """
        html = '''
           <html>
<head>
    <title>FAN Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
</head>
<body style="width:400px; margin: 10px auto;">
    <h1> FAN Control</h1>
    
    <p></p>
   
    <div style="font-size: xx-large;" id="fanStatus"></div>
    <p></p>
    <div style="font-size: xx-large;" id="timerStatus"></div>
    <p></p>
    
    <form action="/on60">
        <input type="submit" style="font-size: xx-large;" value="SWITCH ON 1h" />
    </form>
    
    <form action="/on120">
        <input type="submit" style="font-size: xx-large;" value="SWITCH ON 2h" />
    </form>

    <form action="/FanOff">
        <input type="submit"  style="font-size: xx-large;" value="Fan OFF" />
    </form>

    <form action="/timerMode">
        <input type="submit" style="font-size: xx-large;" value="Night Timer ON" />
    </form>


    <form action="/NightTimerOff">
        <input type="submit"  style="font-size: xx-large;" value="Night Timer OFF" />
    </form>

    <form>
      <input type="button" onclick="window.location.href = 'http://192.168.10.28/graph.html';" value="Graph"/>
    </form>

<iframe src="http://192.168.10.28:3000/d-solo/ba6d4a47-74d9-490a-90bc-d4a9484380a9/crypto?orgId=1&from=1682959450000&to=1682970118000&theme=dark&panelId=3" width="450" height="200" frameborder="0"></iframe>
    <script>
        document.getElementById("fanStatus").innerHTML = "{}";
        document.getElementById("timerStatus").innerHTML = "{}";

    </script>
    <p></p>
    <p>Temperature:  {}</p>
    <p>Humidity:  {}</p>
    <p>Pressure:  {}</p>
    <p></p>
    <p>Current GPU temperature is {}</p>
</body>
</html>
        '''
        gpuTemp = os.popen("/usr/bin/vcgencmd measure_temp").read()
        try:
            self.do_HEAD()
        except ConnectionResetError as identifier:
            print("ConnectionResetError")

        statusText = fan.getStatusText()
        statusNightTimer = fan.getStatusTimer()
        temp = sensor.getTempStr()
        humid = sensor.getHumidStr()
        pressure = sensor.getPressureStr()

        #logger.writeData(10)
        
        if self.path=='/':
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(12, GPIO.OUT)
            GPIO.setup(16, GPIO.OUT)

        elif self.path=='/FanOff' or self.path=='/FanOff?':
            fan.fanOff()
            statusText = fan.setStatus(0,0)
            
        elif self.path=='/on60' or self.path=='/on60?':
            fan.fanOn(oneHour)
            statusText = fan.setStatus(1,oneHour)
            
        elif self.path=='/on120' or self.path=='/on120?':
            fan.fanOn(twoHours)
            statusText = fan.setStatus(1,twoHours)

        elif self.path=='/timerMode' or self.path=='/timerMode?':
            statusNightTimer = fan.setStatus(2,0)
            fan.setOnTimer(5,oneHour)

        elif self.path=='/NightTimerOff' or self.path=='/NightTimerOff?':
            statusNightTimer = fan.setStatus(3,0)
            fan.nightTimerOff()
        
        # elif self.path=='/RefreshStatus' or self.path=='/RefreshStatus?':
        #     statusText = fan.getStatusText()
        #     statusNightTimer = fan.getStatusTimer()
            

        self.wfile.write(html.format(statusText, statusNightTimer, temp, humid, pressure, gpuTemp[5:] ).encode("utf-8"))


if __name__ == '__main__':
    try:
        http_server = HTTPServer((host_name, host_port), MyServer)
    except:
        os.system("sudo kill -9 $(ps -A | grep python | awk '{print $1}')")
        print("kill python to free address")
        http_server = HTTPServer((host_name, host_port), MyServer)
    fan = Fan()
    sensor = Sensor()
    crypto = CryptoApiLogger()
    crypto.writeData()
    #initialize the GPIO ports
    print("Server Starts - %s:%s" % (host_name, host_port)) 
    logger = Logger(fan)
    print("Start logger")
    logger.writeData()
    

    try:
        http_server.serve_forever()
        
    except KeyboardInterrupt:
        fan.fanOff()
        logger.closeDB()
        crypto.closeDB()
        http_server.server_close()
    except:
        fan.fanOff()
        logger.closeDB()
        crypto.closeDB()
        http_server.server_close()