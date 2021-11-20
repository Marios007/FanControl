from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import config


class CryptoApiLogger():


  url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
  parameters = {
    'id': '1027,5899,5567',
    'convert':'EUR'
  }
    #ETH: 1027
    #Casper: 5899
    #Celo: 5567
  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': config.apiKey,
  }


  session = Session()
  session.headers.update(headers)

  try:
    response = session.get(url, params=parameters)
    allData = json.loads(response.text)
    data = allData['data']
    #print(data)
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)

  def storeData():
    return 0 

  def extractData(self):
    etherData = self.data['1027']['quote']['EUR']['price']
    csprData = self.data['5899']['quote']['EUR']['price']
    celoData = self.data['5567']['quote']['EUR']['price']
    etherData  = float(round((etherData*config.amountEther), 2))
    csprData   = float(round((csprData*config.amountCspr), 2))
    celoData   = float(round((celoData*config.amountCelo), 2))
    total = round((etherData + csprData + celoData), 2)
    
    print("Etherium: " + str(etherData) + " EUR")
    print("Casper: " + str(csprData) + " EUR")
    print("Celo: " + str(celoData) + " EUR")
    print("Total: " + str(total))