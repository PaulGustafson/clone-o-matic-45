import requests
#companies = ['NVDA', 'TSLA', 'META', 'AAPL', 'MSFT', 'PLTR', 'SMCI', 'AMZN',
#'#APP', 'INTC', 'COIN', 'MSTR', 'AVGO', 'AMD', 'ABNB', 'NFLX', 'PANW', 'LLY',
#'DKNG', 'HOOD', 'GOOG', 'HIMS', 'MRK', 'PG', 'MU', 'AMAT', 'V', 'SOUN', 'DELL',
#'TWLO', 'UNH', 'CRM', 'ROKU', 'XOM', 'RDDT']
companies = ['Nvidia', 'Tesla', 'Meta', 'Apple', 'Microsoft', 'Palantir', 'Supermicro',
'Amazon', 'AppLovin', 'Intel', 'Coinbase', 'Microstrategy', 'Broadcom', 'AMD',
'Airbnb', 'Netflix', 'PaloAlto', 'Lilly', 'DraftKings', 'Robinhood', 'Google',
'Hims', 'Merck', 'ProcterGamble', 'Micron', 'AppliedMaterials', 'Visa',
'SoundHound', 'Dell', 'Twilio', 'UnitedHealth', 'Salesforce', 'Roku', 'Exxon',
'Reddit']

url = 'https://newsdata.io/api/1/latest?apikey=pub_69774246b6e09534dedf7763a7aeb10334db6&q={}'

for company in companies:
  response = requests.get(url.format(company))
  with open('data/{}.json'.format(company), 'wb') as outf:
    outf.write(response.content)
    