import mysql.connector
import config
from sensor import *
from mysql.connector import Error
import threading

class Logger():

    def __init__(self, fan):
        self.fan = fan

    try:
        connection = mysql.connector.connect(
            user=config.username,
            password=config.password,
            host="localhost",
            port=3306,
            database=config.database
        )

        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
            
    except Error as e:
        print("Error while connecting to FanDB ", e)

    sensorLog = Sensor()

    def writeData(self):
        temp = self.sensorLog.getTemp()
        humid = self.sensorLog.getHumid()
        pressure = self.sensorLog.getPressure()
        fanStatus = self.fan.getStatusFan()
        #print("write data ", temp, "  ", humid ,"  ", pressure)
        query = """INSERT INTO fanData (temperature, humidity, pressure, statusFan) VALUES ( %s, %s , %s, %s)"""
        tuple1 = (temp, humid, pressure, fanStatus)
        self.cursor.execute(query, tuple1)
        self.connection.commit()
        threading.Timer(60.0, self.writeData).start()


    def closeDB(self):
        if self.connection.is_connected():
                self.cursor.close()
                self.connection.close()
                print("MySQL connection is closed")

