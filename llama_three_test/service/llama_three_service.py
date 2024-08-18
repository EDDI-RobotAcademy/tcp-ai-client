from abc import abstractmethod, ABC


class LlamaThreeService(ABC):
    @abstractmethod
    def letsChat(self, userSendMessage):
        pass