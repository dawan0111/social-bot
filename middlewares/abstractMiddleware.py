from abc import ABC, abstractmethod

class AbstractMiddleware(ABC):

    @abstractmethod
    def run(self, response):
        pass