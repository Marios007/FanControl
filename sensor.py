import smbus2
import bme280
import time


class Sensor():
    
    port = 1
    address = 0x76
    
    bus = smbus2.SMBus(port)
    time.sleep(5)
    #os.system('i2cdetect -y 1')
    
    bme280.load_calibration_params(bus, address)
    time.sleep(1)
    data = bme280.sample(bus, address)

    _temp = data.temperature
    _humid = data.humidity
    _pressure = data.pressure


    def __init__(self):
        self.updateData()

    def updateData(self):
        self.data = bme280.sample(self.bus, self.address)
        self._temp = self.data.temperature
        self._humid = self.data.humidity
        self. _pressure = self.data.pressure

    def getTemp(self):
        self.updateData()
        temp = str(self._temp) 
        temp = temp[:5] + "'C"
        return temp

    def getHumid(self):
        self.updateData()
        humid = str(self._humid)
        humid = humid[:5] + "%"
        return humid

    def getPressure(self):
        self.updateData()
        pressure = str(self._pressure)
        pressure = pressure + "hPa"
        return pressure
