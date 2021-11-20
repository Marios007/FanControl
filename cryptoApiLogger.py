from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import config
import threading
import mysql.connector
from mysql.connector import Error


class CryptoApiLogger():

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'id': '1027,5899,5567',
        'convert': 'EUR'
    }
    #ETH: 1027
    #Casper: 5899
    #Celo: 5567
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': config.apiKey,
    }

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

        # Data structure
        # table: cryptoData
        # id int, data_timestamp timestamp,  etherPrice float, csprPrice float, celoPrice float, etherEur float, csprEur float,  celoEur, totalEur float

    def writeData(self):
        session = Session()
        session.headers.update(self.headers)
        
        try:
          response = session.get(self.url, params=self.parameters)
          allData = json.loads(response.text)
          data = allData['data']
          # print(data)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
          print(e)

        etherPrice = self.data['1027']['quote']['EUR']['price']
        csprPrice = self.data['5899']['quote']['EUR']['price']
        celoPrice = self.data['5567']['quote']['EUR']['price']
        # print(self.data['1027']['quote']['EUR'])
        etherTotal = float(round((etherPrice*config.amountEther), 2))
        csprTotal = float(round((csprPrice*config.amountCspr), 2))
        celoTotal = float(round((celoPrice*config.amountCelo), 2))
        totalEur = round((etherTotal + csprTotal + celoTotal), 2)
        query = """INSERT INTO CryptoData (etherPrice, csprPrice, celoPrice, etherEur, csprEur, celoEur, totalEur) VALUES ( %s, %s, %s, %s, %s, %s, %s)"""
        newTuple = (etherPrice, csprPrice, celoPrice,
                    etherTotal, csprTotal, celoTotal, totalEur)
        self.cursor.execute(query, newTuple)
        self.connection.commit()
        threading.Timer(600.0, self.writeData).start()

        #print("Etherium: " + str(etherTotal) + " EUR")
        #print("Casper: " + str(csprTotal) + " EUR")
        #print("Celo: " + str(celoTotal) + " EUR")
        #print("Total: " + str(totalEur))

    def closeDB(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection for Crypto is closed")
