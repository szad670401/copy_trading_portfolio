import ccxt.pro
import asyncio

class Trader:
    def __init__(self, config):
        self.exchange = ccxt.pro.binance({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })

    async def place_order_async(self, symbol, type, side, amount, positionSide, reduceOnly):
        symbol = symbol.replace('USDT', '/USDT')
        market = await self.exchange.load_markets()
        market = self.exchange.market(symbol)
        amount = self.exchange.amount_to_precision(symbol, amount)
        params = {
            'positionSide': positionSide.lower(),
            'reduceOnly': reduceOnly,
        }
        order = await self.exchange.create_order(symbol, type, side, amount, None, params)
        return order

    async def follow_order_async(self, trade, ratio, reduceOnly=False):
        symbol = trade['symbol']  
        type = 'market'  
        side = trade['side'].lower()  
        amount = trade['quantity'] * ratio  
        positionSide = trade['positionSide']
        order = await self.place_order_async(symbol, type, side, amount, positionSide, reduceOnly)
        return order



from key import api_key,api_secret
async def test():
    config = {
        'api_key': api_key,
        'api_secret': api_secret,
        'ratio': 0.9,
    }
    
    trader = Trader(config)
    
    new_trade = {
        'symbol': 'VETUSDT',
        'side': 'BUY',
        'quantity': 158.01552,  
        'positionSide': 'BOTH',
    }

    order_result = await trader.follow_order_async(new_trade, config['ratio'])
    print(order_result)

if __name__ == '__main__':
    asyncio.run(test())

