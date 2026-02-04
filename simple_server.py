from sensor import Sensor
import RPi.GPIO as GPIO
import os
from sensor import *
from logger import *
from cryptoApiLogger import *
from led_ring import LedRing
from camera import Camera
from http.server import BaseHTTPRequestHandler, HTTPServer
import config

host_name = '192.168.178.38'  # Change this to your Raspberry Pi IP address
host_port = 8000


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
    <title>Home</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        body {{
            max-width: 100%;
            margin: 0;
            padding: 10px;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }}
        .container {{
            max-width: 500px;
            margin: 0 auto;
        }}
        .message {{
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 4px;
            text-align: center;
        }}
        iframe {{
            width: 100%;
            height: 400px;
            border: none;
        }}
    </style>
</head>
<body>
    <div class="container">
    <h1>HOME</h1>
    {}
    <form action="/lighton">
        <input type="submit" style="font-size: large; width: 100%; padding: 8px;" value="Light ON" />
    </form>
    
    <p></p>
    
    <form action="/startcamera">
        <input type="submit" style="font-size: large; width: 100%; padding: 8px;" value="Start Camera" />
    </form>
    
    <p></p>

<iframe src="http://192.168.178.38:3000/d-solo/ae86d7eb-af8a-47e3-80ea-426963f73ee3/kitchen?orgId=1&from=now-6h&to=now&timezone=browser&panelId=1&__feature.dashboardSceneSolo&refresh=10m"></iframe>
    
    <p></p>
    <p>Temperature:  {}</p>
    <p>Humidity:  {}</p>
    <p>Pressure:  {}</p>
    <p></p>
    <p>Current GPU temperature is {}</p>
    </div>
</body>
</html>
        '''
        gpuTemp = os.popen("/usr/bin/vcgencmd measure_temp").read()
        try:
            self.do_HEAD()
        except ConnectionResetError as identifier:
            print("ConnectionResetError")

        temp = sensor.getTempStr()
        humid = sensor.getHumidStr()
        pressure = sensor.getPressureStr()
        
        message = ""
        
        if self.path=='/':
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
        
        elif self.path=='/lighton' or self.path=='/lighton?':
            led_ring.light_on(300)  # 5 Minuten = 300 Sekunden
            print("LED Licht eingeschaltet für 5 Minuten")
            message = '<div class="message">LED light turned on for 5 minutes</div>'
        
        elif self.path=='/startcamera' or self.path=='/startcamera?':
            camera.start_capture_with_timeout(300, 30)  # 5 Minuten, alle 30 Sekunden
            print("Kamera gestartet, macht alle 30 Sekunden ein Foto für 5 Minuten")
            message = '<div class="message">Camera started - 10 photos in 5 minutes</div>'

        self.wfile.write(html.format(message, temp, humid, pressure, gpuTemp[5:] ).encode("utf-8"))


if __name__ == '__main__':
    try:
        http_server = HTTPServer((host_name, host_port), MyServer)
    except:
        os.system("sudo kill -9 $(ps -A | grep python | awk '{print $1}')")
        print("kill python to free address")
        http_server = HTTPServer((host_name, host_port), MyServer)
    
    sensor = Sensor()
    led_ring = LedRing()
    camera = Camera()
    crypto = CryptoApiLogger()
    crypto.writeData()
    
    print("Server Starts - %s:%s" % (host_name, host_port)) 
    logger = Logger()
    print("Start logger")
    logger.writeData()
    

    try:
        http_server.serve_forever()
        
    except KeyboardInterrupt:
        led_ring.cleanup()
        camera.cleanup()
        logger.closeDB()
        crypto.closeDB()
        http_server.server_close()
    except:
        led_ring.cleanup()
        camera.cleanup()
        logger.closeDB()
        crypto.closeDB()
        http_server.server_close()