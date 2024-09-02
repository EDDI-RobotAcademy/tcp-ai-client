from abc import abstractmethod, ABC


class LlamaTestRepository(ABC):
    @abstractmethod
    def generateText(self, userSendMessage):
        pass