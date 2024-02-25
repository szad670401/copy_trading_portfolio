config = {
    'page_size': 10,
    'request_interval': 0.4,
    'retry_interval': 10,
    #'request_url':  'http://127.0.0.1:5000/test_endpoint'
    'request_url':  'https://www.binance.com/bapi/futures/v1/public/future/copy-trade/lead-portfolio/trade-history'
}


trades_list = {
        "StrategyCryptoCap":{"portfolioId": '3776145285231904001', "ratio": 0.8} , 
        "PlymouthBot":{"portfolioId": "3804328247989185792" , "ratio": 0.6}
}


dingtalk_token = "602993cd4f85d502a08a83da8b1213ed126154e78167eac5821e71c2fbf12f2a"
#dingtalk_token = "602993cd4f85d502a08a83da8b1213ed126154e78167eac5821e71c2fbf12f2a"

from key import api_key,api_secret
user_config = {
    'type': 'binance',
    'api_key': api_key,
    'api_secret': api_secret,
    'ratio': 0.5,
}


