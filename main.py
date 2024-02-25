import aiohttp
import asyncio
import requests
import uuid
import time
import config
from notify import dprint 
from trader import Trader  
from logger import logger




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
    trade_string = f"{trade['time']}{trade['symbol']}{trade['side']}{trade['price']}{trade['quantity']}"
    return trade_string



async def fetch_trade_history(session, portfolio_config, name, config,trader):
    bnc_uuid = generate_uuid()
    csrftoken = uuid.uuid4().hex
    x_trace_id = uuid.uuid4().hex
    x_ui_request_trace = uuid.uuid4().hex

    headers = generate_headers(bnc_uuid, csrftoken, x_trace_id, x_ui_request_trace)
    cookies = generate_cookies(bnc_uuid)
    data = {
        'pageNumber': 1,
        'pageSize': config['page_size'],
        'portfolioId': portfolio_config['portfolioId']
    }
    known_hashes = set()
    first_request = True
    last_total = 0

    while True:
        try:
            async with session.post(config['request_url'], headers=headers, cookies=cookies, json=data) as response:
                response.raise_for_status()
                result = await response.json()
                logger.debug(f"Check [{name}] {len(result['data']['list'])} history positions in list")
                current_total = result['data']['total']
                logger.debug(f"{first_request} {last_total != current_total} {last_total} {current_total}")
                #logger.info(result)
                new_trades = []
                if first_request or last_total != current_total:
                    logger.info(f"first_request:{first_request}")
                    sorted_list = sorted(result['data']['list'], key=lambda x: x['time'], reverse=True)
                    new_count = current_total - last_total
                    last_total = current_total
                    new_count = max(min(new_count , 10), 0)
                    logger.debug(f"new counter:{new_count}")
                    new_trades = sorted_list[:new_count] if new_count > 0 else []
                    if new_count > 10:
                        data['pageSize'] = new_count
                        logger.debug(f"new_count > 10 {new_count} ")
                        last_total = current_total
                        continue

                logger.info(f"first_request:{first_request}")
                if new_trades and not first_request:
                    dprint(f"NewTrades \n [{name}]\n" + str(new_trades))
                    logger.info(f"NewTrades \n [{name}]\n" + str(new_trades))
                    for trade in new_trades[::-1]:
                        try:
                            logger.info("[Trade]" + str(trade))
                            info =  await trader.follow_order_async(trade, portfolio_config['ratio'])
                            if 'info' in info.keys() and info['info']['status'] == "FILLED":
                                price = info['info']['avgPrice']
                                amt = info['info']['cumQty']
                                symbol = info["symbol"] 
                                dprint(f"[FILLED] {symbol} {amt}@{price} Successfully.")
                            logger.info(info)
                        except Exception as e:
                            logger.error(f"Order failed: {e}")
                first_request = False
                last_total = current_total
            await asyncio.sleep(config['request_interval'])
        except Exception as e:
            logger.error(f"Request failed: {e}")
            await asyncio.sleep(config['retry_interval'])

async def main(config,user_config, trades_list):
    trader = Trader(user_config) 
    async with aiohttp.ClientSession() as session:
        tasks = []
        for trader_name, portfolio_config in trades_list.items():
            task = asyncio.create_task(fetch_trade_history(session, portfolio_config, trader_name, config, trader))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main(config.config ,config.user_config, config.trades_list))

