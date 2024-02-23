import aiohttp
import asyncio
import requests
import uuid
import time
import config
import logging
from logging.handlers import RotatingFileHandler
from notify import dprint 


logger = logging.getLogger('monitor')
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler('monitor.log', maxBytes=50*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def generate_uuid():
    return str(uuid.uuid4())

def generate_headers(bnc_uuid, csrftoken, x_trace_id, x_ui_request_trace):
    return {
        'authority': 'www.binance.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,eu;q=0.8',
        'bnc-uuid': bnc_uuid,
        'clienttype': 'web',
        'content-type': 'application/json',
        'csrftoken': csrftoken,
        'lang': 'zh-CN',
        'origin': 'https://www.binance.com',
        'referer': 'https://www.binance.com/zh-CN/copy-trading/lead-details/3776145285231904001?timeRange=7D',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'x-trace-id': x_trace_id,
        'x-ui-request-trace': x_ui_request_trace,
    }

def generate_cookies(bnc_uuid):
    return {
        'bnc-uuid': bnc_uuid,
        'userPreferredCurrency': 'USD_USD',
        'theme': 'dark',
        'lang': 'en',
        'BNC-Location': 'BINANCE'
    }
def generate_str(trade):
    trade_string = f"{trade['time']}{trade['symbol']}{trade['side']}{trade['price']}"
    return trade_string



async def fetch_trade_history(session, portfolioId, name, config):
    bnc_uuid = generate_uuid()
    csrftoken = uuid.uuid4().hex
    x_trace_id = uuid.uuid4().hex
    x_ui_request_trace = uuid.uuid4().hex

    headers = generate_headers(bnc_uuid, csrftoken, x_trace_id, x_ui_request_trace)
    cookies = generate_cookies(bnc_uuid)
    data = {
        'pageNumber': 1,
        'pageSize': config['page_size'],
        'portfolioId': portfolioId
    }
    known_hashes = set()
    first_request = True
    while True:
        try:
            async with session.post('https://www.binance.com/bapi/futures/v1/public/future/copy-trade/lead-portfolio/trade-history',
                                    headers=headers, cookies=cookies, json=data) as response:
                response.raise_for_status()
                result = await response.json()
                new_trades = []
                logger.debug(f"Check {len(result['data']['list'])} Positions in List")
                for item in result['data']['list']:
                    trade_hash = generate_str(item)
                    if trade_hash not in known_hashes:
                        if not first_request:
                            new_trades.append(item)
                        known_hashes.add(trade_hash)
                if new_trades:
                    logger.info(new_trades)
                    dprint(new_trades)
                first_request = False
            await asyncio.sleep(config['request_interval'])
        except Exception as e:
            logger.error(f"Request failed: {e}")
            await asyncio.sleep(config['retry_interval'])

async def main(config, trades_list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for trader_name, portfolioId in trades_list.items():
            task = asyncio.create_task(fetch_trade_history(session, portfolioId, trader_name, config))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main(config.config, config.trades_list))

