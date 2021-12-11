from scipy import optimize
from datetime import datetime
from sqlitedict import SqliteDict
from binance_trade_bot.config import Config
from traceback import format_exc
from typing import Dict
import time
import random
from binance_trade_bot.backtest import MockBinanceManager, MockDatabase
from binance_trade_bot.logger import Logger
from binance_trade_bot.strategies import get_strategy
import logging.handlers
from binance_trade_bot.notifications import NotificationHandler
from binance.client import Client
from binance_trade_bot.binance_stream_manager import BinanceCache, BinanceOrder


### Settings
workers = 3  # number of backtests running parallel. Reduce if CPU usage is too high. Increase for faster.

# each variable to be optimized. slice(a, b, step) tells the optimizer to test every value between a and b with step.
# alternatively, using (a, b) will tell the optimizer to test between a and b.
paramdict = {
    "SCOUT_MARGIN": [0.5, 4]
}

START_DATE = datetime(2021, 11, 1)
END_DATE = datetime(2021, 11, 27)
POLISH = None  # Final optimization. None for no polish.
outfile = 'result.txt'  # File the results will be stored in at the end
SILENT = True  # False to see logger messages. Will clutter console if using multiple workers.
###


slices = list(paramdict.values())
variable_names = tuple(paramdict.keys())


class SilentLogger(Logger):
    def __init__(self, logging_service="crypto_trading", enable_notifications=True):
        self.Logger = logging.getLogger(f"{logging_service}_logger")
        self.Logger.setLevel(logging.DEBUG)
        self.Logger.propagate = False
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # default is "logs/crypto_trading.log"
        fh = logging.FileHandler(f"logs/{logging_service}.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.Logger.addHandler(fh)
        # notification handler
        self.NotificationHandler = NotificationHandler(enable_notifications)
        if not SILENT:
            # logging to console
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            self.Logger.addHandler(ch)


def backtest(
        start_date: datetime = None,
        end_date: datetime = None,
        interval=1,
        yield_interval=100,
        start_balances: Dict[str, float] = None,
        starting_coin: str = None,
        config: Config = None,
):
    """

    :param config: Configuration object to use
    :param start_date: Date to  backtest from
    :param end_date: Date to backtest up to
    :param interval: Number of virtual minutes between each scout
    :param yield_interval: After how many intervals should the manager be yielded
    :param start_balances: A dictionary of initial coin values. Default: {BRIDGE: 100}
    :param starting_coin: The coin to start on. Default: first coin in coin list

    :return: The final coin balances
    """
    sqlite_cache = SqliteDict("data/backtest_cache.db")
    config = config or Config()
    logger = SilentLogger("backtesting", enable_notifications=False)

    end_date = end_date or datetime.today()

    db = MockDatabase(logger, config)
    db.create_database()
    db.set_coins(config.SUPPORTED_COIN_LIST)
    manager = MockBinanceManager(
        Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET_KEY, tld=config.BINANCE_TLD),
        sqlite_cache,
        BinanceCache(),
        config,
        db,
        logger,
        start_date,
        start_balances
    )

    starting_coin = db.get_coin(starting_coin or config.CURRENT_COIN_SYMBOL or config.SUPPORTED_COIN_LIST[0])
    if manager.get_currency_balance(starting_coin.symbol) == 0:
        manager.buy_alt(starting_coin, config.BRIDGE, 0.0)  # doesn't matter mocking manager don't look at fixed price
    db.set_current_coin(starting_coin)

    strategy = get_strategy(config.STRATEGY)
    if strategy is None:
        logger.error("Invalid strategy name")
        return manager
    trader = strategy(manager, db, logger, config)
    trader.initialize()

    yield manager

    n = 1
    try:
        while manager.datetime < end_date:
            try:
                trader.scout()
            except Exception:  # pylint: disable=broad-except
                logger.warning(format_exc())
            manager.increment(interval)
            if n % yield_interval == 0:
                yield manager
            n += 1
    except KeyboardInterrupt:
        pass
    return manager


class OptimizerConfig(Config):
    def __init__(self, variables, params):
        super().__init__()
        for idx, name in enumerate(params):
            setattr(self, name, variables[idx])

def backtester(variables, *params):
    time.sleep(5*random.random())
    for manager in backtest(START_DATE, END_DATE, config=OptimizerConfig(variables, params)):
        bridge_value = - manager.collate_coins(manager.config.BRIDGE.symbol)
    print(f"{bridge_value} with {variables}")
    return bridge_value


result = optimize.brute(func=backtester,
                        ranges=slices,
                        workers=workers,
                        args=variable_names,
                        full_output=True,
                        finish=POLISH)
print(result)
f = open(outfile, 'w')
f.write(f"{result}")
f.close()



