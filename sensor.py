import smbus2
import bme280


class Sensor():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address)

    def getTemp(self):
        temp = str(self.data.temperature) 
        temp = temp[:5] + "'C"
        return temp

    def getHumid(self):
        humid = str(self.data.humidity)
        humid = humid[:5] + "%"
        return humid

