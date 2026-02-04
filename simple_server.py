from sensor import Sensor
import RPi.GPIO as GPIO
import os
from sensor import *
from logger import *
from cryptoApiLogger import *
from http.server import BaseHTTPRequestHandler, HTTPServer

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
</head>
<body style="width:400px; margin: 10px auto;">
    <h1>Sensor Monitor</h1>
    
    <p></p>

    <form action="/lighton">
        <input type="submit" style="font-size: xx-large; width: 100%; padding: 10px;" value="Light ON" />
    </form>
    
    <p></p>
    
    <form action="/startcamera">
        <input type="submit" style="font-size: xx-large; width: 100%; padding: 10px;" value="Start Camera" />
    </form>
    
    <p></p>

    <form>
      <input type="button" onclick="window.location.href = 'http://192.168.178.38/graph.html';" value="Graph"/>
    </form>

<iframe src="http://192.168.178.38:3000/d-solo/ae86d7eb-af8a-47e3-80ea-426963f73ee3/kitchen?orgId=1&from=1770043276284&to=1770216076284&timezone=browser&panelId=1&__feature.dashboardSceneSolo" width="450" height="200" frameborder="0"></iframe>
    
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

        temp = sensor.getTempStr()
        humid = sensor.getHumidStr()
        pressure = sensor.getPressureStr()
        
        if self.path=='/':
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

        self.wfile.write(html.format(temp, humid, pressure, gpuTemp[5:] ).encode("utf-8"))


if __name__ == '__main__':
    try:
        http_server = HTTPServer((host_name, host_port), MyServer)
    except:
        os.system("sudo kill -9 $(ps -A | grep python | awk '{print $1}')")
        print("kill python to free address")
        http_server = HTTPServer((host_name, host_port), MyServer)
    
    sensor = Sensor()
    crypto = CryptoApiLogger()
    crypto.writeData()
    
    print("Server Starts - %s:%s" % (host_name, host_port)) 
    logger = Logger()
    print("Start logger")
    logger.writeData()
    

    try:
        http_server.serve_forever()
        
    except KeyboardInterrupt:
        logger.closeDB()
        crypto.closeDB()
        http_server.server_close()
    except:
        logger.closeDB()
        crypto.closeDB()
        http_server.server_close()