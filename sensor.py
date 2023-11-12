from smbus2 import SMBus
import bme280



class Sensor():

    port = 1
    address = 0x76

    bus = SMBus(port)
    #time.sleep(1)
    #os.system('i2cdetect -y 1')

    bme280.load_calibration_params(bus, address)
    #time.sleep(1)
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
        self. _pressure = self.data.pressure+60.9

    def getTempStr(self):
        self.updateData()
        temp = str(self.getTemp()) 
        temp = temp[:5] + "'C"
        return temp

    def getHumidStr(self):
        self.updateData()
        humid = str(self.getHumid())
        humid = humid[:5] + "%"
        return humid

    def getPressureStr(self):
        self.updateData()
        pressure = str(self.getPressure())
        pressure = pressure + "hPa"
        return pressure

    def getTemp(self):
        self.updateData()
        temp = round(float(self._temp),2)
        return temp

    def getHumid(self):
        self.updateData()
        humid = round(float(self._humid),2)
        return humid

    def getPressure(self):
        self.updateData()
        pressure = round(float(self._pressure),2)
        return pressure
