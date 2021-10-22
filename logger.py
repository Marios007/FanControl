import mysql.connector
import config
from mysql.connector import Error
import sys

class Logger():

    
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
        print("Error while connecting to MySQL", e)


    def writeData(self, temperature, humidity, pressure):
        print("write data to DB")
        query = """INSERT INTO fanData (id, temperature, humidity, pressure) VALUES (1, 1, 1.1, 1.1, 1.1)"""

    def closeDB(self):
        if self.connection.is_connected():
                self.cursor.close()
                self.connection.close()
                print("MySQL connection is closed")

# MariaDB [fanDB]> SHOW COLUMNS FROM fanData;
# id int(11)
# data_timestamp timestamp
# temperature float
# humidity float
# pressure float