import smbus2
import bme280


class Sensor():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address)
    _temp = data.temperature
    _humid = data.humidity
    _pressure = data.pressure


    def getTemp(self):
        temp = str(self._temp) 
        temp = temp[:5] + "'C"
        return temp

    def getHumid(self):
        humid = str(self._humid)
        humid = humid[:5] + "%"
        return humid

    def getPressure(self):
        pressure = str(self._pressure)
        pressure = pressure + "hPa"
        return pressure

    

