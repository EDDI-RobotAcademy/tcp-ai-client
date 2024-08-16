from abc import ABC, abstractmethod


class LlamaTestService(ABC):
    @abstractmethod
    def chatWithLlama(self, userSendMessage):
        pass