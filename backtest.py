from datetime import datetime

from binance_trade_bot import backtest

if __name__ == "__main__":
    history = []
    start_time = datetime(2021, 12, 1, 0, 0)
    end_time = datetime(2021, 12, 7, 23, 59)
    start_balances = {"USDT": 10000}
    starting_coin = "BTC"
    show_btc = True
    print(f"BACKTEST from {start_time} to {end_time}")
    current_date = start_time.strftime("%d/%m/%Y")
    for manager in backtest(start_time, end_time):
        if show_btc:
            btc_value = manager.collate_coins("BTC")
        else:
            btc_value = 0
        bridge_value = manager.collate_coins(manager.config.BRIDGE.symbol)
        bridge_fees_value = manager.collate_fees(manager.config.BRIDGE.symbol)
        trades = manager.trades
        history.append((btc_value, bridge_value, trades, bridge_fees_value))
        if show_btc:
            btc_diff = round((btc_value - history[0][0]) / history[0][0] * 100, 3)
        else:
            btc_diff = 0
        bridge_diff = round((bridge_value - history[0][1]) / history[0][1] * 100, 3)
        if manager.datetime.strftime("%d/%m/%Y") != current_date:
            current_date = manager.datetime.strftime("%d/%m/%Y")
            time_diff = (manager.datetime - start_time).total_seconds() / 3600
            per_trade = round(100 * ((bridge_value / history[0][1]) ** (2 / (trades - 1)) - 1), 4)
            per_hour = round(100 * ((bridge_value / history[0][1]) ** (1 / time_diff) - 1), 4)
            print("------")
            print("TIME:", manager.datetime)
            print("TRADES:", trades)
            print(f"{manager.config.BRIDGE.symbol} FEES VALUE:", bridge_fees_value)
            print("BTC VALUE:", btc_value, f"({btc_diff}%)")
            print(f"{manager.config.BRIDGE.symbol} VALUE:", bridge_value, f"({bridge_diff}%)")
            print(f"PERFORMANCE: {per_trade}% {manager.config.BRIDGE.symbol}/trade, "
                  f"{per_hour}% {manager.config.BRIDGE.symbol}/hr")
            print("------")
    print("------")
    print("TIME:", manager.datetime)
    print("TRADES:", trades)
    print("POSITIVE COIN JUMPS:", manager.positve_coin_jumps)
    print("NEVATIVE COIN JUMPS:", manager.negative_coin_jumps)
    print(f"{manager.config.BRIDGE.symbol} FEES VALUE:", bridge_fees_value)
    print("BTC VALUE:", btc_value, f"({btc_diff}%)")
    print(f"{manager.config.BRIDGE.symbol} VALUE:", bridge_value, f"({bridge_diff}%)")
    print(f"PERFORMANCE: {per_trade}% {manager.config.BRIDGE.symbol}/trade, "
          f"{per_hour}% {manager.config.BRIDGE.symbol}/hr")
    print("------")