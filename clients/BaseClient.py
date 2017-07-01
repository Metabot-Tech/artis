from abc import ABC, abstractmethod


class BaseClient(ABC):
    @abstractmethod
    def get_balances(self):
        pass

    @abstractmethod
    def get_balance(self, currency):
        pass
