from abc import ABC, abstractmethod


class Strategy(ABC):

    @abstractmethod
    def run(self):
        pass
