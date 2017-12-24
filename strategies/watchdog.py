from pyetherscan import Address
from dynaconf import settings


class WatchDog(object):
    def get_available_volume(self, coin, market):
        market_ico_address = settings[market].get("ICO_ADDRESS")
        address = Address(market_ico_address)

        contract_address = settings["CONTRACTS"].get(coin)
        return address.token_balance(contract_address)
