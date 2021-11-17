from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import config


def extractData(data):
    #ETH: 1027
    #Casper: 5899
    #Celo: 5567

    if data['id'] == '1027':
        print('ETHER')



url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
  'id': '1027,5899,5567',
  'convert':'EUR'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': config.apiKey,
}

session = Session()
session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  allData = json.loads(response.text)
  #print(data)
  data = allData['data']
  etherData = data['1027']['quote']['EUR']['price']
  csprData = data['5899']['quote']['EUR']['price']
  celoData = data['5567']['quote']['EUR']['price']
  etherData  = float(round((etherData*0.80157), 2))
  csprData = float(round((csprData*67990), 2))
  celoData = float(round((csprData*67990), 2))

  
  print("Etherium: " + str(etherData) + " EUR")
  print("Casper: " + str(csprData) + " EUR")
  print("Celo: " + str(csprData) + " EUR")

  #print(csprData)
  #print(celoData)



except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)

