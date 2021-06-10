import pytest

import os, datetime

from sqlalchemy.orm import Session, scoped_session, sessionmaker

from binance_trade_bot.database import Database
from binance_trade_bot.logger   import Logger
from binance_trade_bot.config   import Config
from binance_trade_bot.models.coin import Coin
from binance_trade_bot.models.coin_value import CoinValue

from .common import infra

@pytest.fixture(scope='class', autouse=True)
def DoUserConfig():

    '''
    CURRENT_COIN_SYMBOL:
    SUPPORTED_COIN_LIST: "XLM TRX ICX EOS IOTA ONT QTUM ETC ADA XMR DASH NEO ATOM DOGE VET BAT OMG BTT"
    BRIDGE_SYMBOL: USDT
    API_KEY: vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A
    API_SECRET_KEY: NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j
    SCOUT_MULTIPLIER: 5
    SCOUT_SLEEP_TIME: 1
    TLD: com
    STRATEGY: default
    BUY_TIMEOUT: 0
    SELL_TIMEOUT: 0
    BUY_ORDER_TYPE: limit
    SELL_ORDER_TYPE: market
    '''

    #os.environ['CURRENT_COIN'] = 'ETH'
    os.environ['CURRENT_COIN_SYMBOL'] = 'ETH'

    os.environ['API_KEY'] = 'vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A'
    os.environ['API_SECRET_KEY'] = 'NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j'
    #os.environ['CURRENT_COIN_SYMBOL'] = 'BTT'
    os.environ['SUPPORTED_COIN_LIST'] = "XLM TRX ICX EOS IOTA ONT QTUM ETC ADA XMR DASH NEO ATOM DOGE VET BAT OMG BTT"
    os.environ['BRIDGE_SYMBOL'] = "USDT"
    os.environ['SCOUT_MULTIPLIER'] = "5"
    os.environ['SCOUT_SLEEP_TIME'] = "1"
    os.environ['TLD'] = 'com'
    os.environ['STRATEGY'] = 'default'
    os.environ['BUY_TIMEOUT']  = "0"
    os.environ['SELL_TIMEOUT'] = "0"
    os.environ['BUY_ORDER_TYPE'] = 'limit'
    os.environ['SELL_ORDER_TYPE'] = 'market'

    yield

class TestDatabase:

    @pytest.mark.xfail
    def test_socketio_connect(self):
        # test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        result: bool = dbtest.socketio_connect()
        assert result

    def test_db_session(self):
        # test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        session: Session = dbtest.db_session()
        assert True

    @pytest.mark.skip
    def test_schedule_execute_later(self):
        assert False

    @pytest.mark.skip
    def test_execute_postponed_calls(self):
        assert False

    def test_manage_session(self):
        # test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        session: Session = dbtest.manage_session(session=None)
        assert session
        session: Session = dbtest.manage_session(session=session)
        assert session
        session: Session = dbtest.manage_session()
        assert session

    def test_set_coins(self):
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        # testing empty
        dbtest.set_coins([])
        listCoins = dbtest.get_coins(only_enabled=False)
        assert len(listCoins) == len(config.SUPPORTED_COIN_LIST), "Not matched size"
        for ii in listCoins:
            assert ii.symbol in config.SUPPORTED_COIN_LIST, "No matched"

        # testing not empty
        dbtest.set_coins(config.SUPPORTED_COIN_LIST)
        listCoins = dbtest.get_coins(only_enabled=False)
        assert len(listCoins) == len(config.SUPPORTED_COIN_LIST), "Not matched size"
        for ii in listCoins:
            assert ii.symbol in config.SUPPORTED_COIN_LIST, "No matched"

    def test_get_coins(self):

        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        # TODO: what do with enable?
        # testing empty
        dbtest.set_coins([])
        listCoins = dbtest.get_coins(only_enabled=False)
        assert len(listCoins) == len(config.SUPPORTED_COIN_LIST), "Not matched size"
        for ii in listCoins:
            assert ii.symbol in config.SUPPORTED_COIN_LIST, "No matched"

        # testing not empty
        dbtest.set_coins(config.SUPPORTED_COIN_LIST)
        listCoins = dbtest.get_coins(only_enabled=False)
        assert len(listCoins) == len(config.SUPPORTED_COIN_LIST), "Not matched size"
        for ii in listCoins:
            assert ii.symbol in config.SUPPORTED_COIN_LIST, "No matched"

    def test_get_coin(self):

        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        # TODO: not KeyError raises?
        '''
        with pytest.raises(KeyError) :
            ccoin = dbtest.get_coin('XXXXXX')
        '''

        dbtest.set_coins(config.SUPPORTED_COIN_LIST)

        # testing string
        ccoin = dbtest.get_coin(config.SUPPORTED_COIN_LIST[0])
        assert config.SUPPORTED_COIN_LIST[0] == ccoin.symbol

        # testing type
        ccoin = dbtest.get_coin(Coin(config.SUPPORTED_COIN_LIST[-1]))
        assert config.SUPPORTED_COIN_LIST[-1] == ccoin.symbol

    def test_set_current_coin(self):

        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        # TODO: not KeyError raises?
        '''
        with pytest.raises(KeyError) :
            ccoin = dbtest.get_coin('XXXXXX')
        '''

        dbtest.set_coins(config.SUPPORTED_COIN_LIST)

        # testing string
        dbtest.set_current_coin(config.SUPPORTED_COIN_LIST[0])
        ccoin: Coin = dbtest.get_current_coin()
        assert config.SUPPORTED_COIN_LIST[0] == ccoin.symbol

        # testing type
        dbtest.set_current_coin(Coin(config.SUPPORTED_COIN_LIST[-1]))
        ccoin: Coin = dbtest.get_current_coin()
        assert config.SUPPORTED_COIN_LIST[-1] == ccoin.symbol

    def test_get_current_coin(self):
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        # TODO: add specificate
        # TODO: not KeyError raises?
        '''
        with pytest.raises(KeyError) :
            ccoin = dbtest.get_coin('XXXXXX')
        '''

        dbtest.set_coins(config.SUPPORTED_COIN_LIST)

        # testing string
        dbtest.set_current_coin(config.SUPPORTED_COIN_LIST[0])
        ccoin: Coin = dbtest.get_current_coin()
        assert config.SUPPORTED_COIN_LIST[0] == ccoin.symbol

        # testing type
        dbtest.set_current_coin(Coin(config.SUPPORTED_COIN_LIST[-1]))
        ccoin: Coin = dbtest.get_current_coin()
        assert config.SUPPORTED_COIN_LIST[-1] == ccoin.symbol

    # TODO: find use
    @pytest.mark.xfail
    @pytest.mark.parametrize('from_coin',[Coin('XML'), 'XML'])
    @pytest.mark.parametrize('to_coin',  [Coin('BTT'), 'BTT', 'XML'])
    def test_get_pair(self, from_coin, to_coin):

        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()
        dbtest.set_coins(config.SUPPORTED_COIN_LIST)

        pair = dbtest.get_pair(from_coin, to_coin)
        print(pair)
        print(type(pair))
        assert True

    @pytest.mark.xfail
    def test_batch_log_scout(self):
        assert False

    def test_prune_scout_history(self):

        # Test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()
        dbtest.set_coins(config.SUPPORTED_COIN_LIST)
        dbtest.prune_scout_history()
        assert True

    def test_prune_value_history(self):

        # Test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()
        dbtest.set_coins(config.SUPPORTED_COIN_LIST)
        dbtest.prune_value_history()
        assert True

    def test_create_database(self):
        # Test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()
        assert True

    # TODO : ATR ??? XML-XML ???
    @pytest.mark.parametrize('from_coin',['XML','ATR'])
    @pytest.mark.parametrize('to_coin',  ['BTT', 'XML'])
    @pytest.mark.parametrize('selling',  [True, False])
    def test_start_trade_log(self, from_coin: str, to_coin: str, selling: bool):

        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        tradeLog = dbtest.start_trade_log(from_coin, to_coin, selling)
        #print(type(tradeLog))
        #print(tradeLog)

        assert True

    # TODO: find using ?
    def test_send_update(self):
        # test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()
        dbtest.send_update(None)

        assert True

    @pytest.mark.skip
    def test_migrate_old_state(self):
        assert False

    def test_commit_ratios(self):
        # test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()
        dbtest.commit_rasio()
        assert True

    def test_batch_update_coin_values(self):
        # test on run
        logger = Logger("db_testing", enable_notifications=False)
        config = Config()

        dbtest = Database(logger, config)
        dbtest.create_database()

        dbtest.batch_update_coin_values([])

        vlist = [CoinValue(Coin('BTT'), 4.0, 5000.0, 0.89, 'HOURLY', None),
                 CoinValue(Coin('BTT'), 4.0, 5000.0, 0.89, 'DAILY', datetime.datetime.now()),]
        dbtest.batch_update_coin_values(vlist)

        assert True
