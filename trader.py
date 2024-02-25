import ccxt.pro
import asyncio
from logger import logger

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

    async def follow_order_async(self, trade, ratio):
        symbol = trade['symbol']  
        type = 'market'  
        side = trade['side'].lower()  
        amount = trade['qty'] * ratio  
        positionSide = trade['positionSide']
        reduceOnly = False
        if abs(float(trade['realizedProfit'])) > 6e-5:
            reduceOnly = True
        order = {}
        try:
            order = await self.place_order_async(symbol, type, side, amount, positionSide, reduceOnly)
        except Exception as e:
            error_message = str(e)
            logger.error(error_message)
            if "-2022" in error_message and "code" in error_message:
                logger.debug("==========================")
                data = await self.exchange.fetch_positions(symbols = [symbol])
                logger.debug(data)
                filtered_positions = {item['symbol']: item['info']['positionAmt'] for item in data if abs(float(item['info']['positionAmt'])) > 0}
                logger.debug(f"[Position] \n {filtered_positions}")
                symbol_mangle = symbol + ":USDT"
                logger.debug(symbol_mangle)
                logger.debug(filtered_positions)
                if symbol_mangle in filtered_positions.keys():
                    amount = filtered_positions[symbol_mangle]
                    logger.debug(f"Recreated {symbol} {amount}")
                    logger.debug("---------------------------")
                    order = await self.place_order_async(symbol, type, side, amount, positionSide, reduceOnly)
            else:
                logger.info("error " + str(e))
        return order


from key import api_key,api_secret
async def test():
    config = {
        'api_key': api_key,
        'api_secret': api_secret,
        'ratio': 0.9,
    }
    
    trader = Trader(config)
    
    new_trade = {'time': 1708712240000, 'symbol': 'GALAUSDT', 'side': 'SELL', 'price': 0.02868, 'fee': -0.05240983, 'feeAsset': 'USDT', 'quantity': 262.04916, 'quantityAsset': 'USDT', 'realizedProfit': 2.01014, 'realizedProfitAsset': 'USDT', 'baseAsset': 'GALA', 'qty': 9137.0, 'positionSide': 'BOTH', 'activeBuy': True}

    order_result = await trader.follow_order_async(new_trade, config['ratio'])
    print(order_result)

if __name__ == '__main__':
    asyncio.run(test())

